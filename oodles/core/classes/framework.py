import json
import os
import shutil
from datetime import datetime
from oodles.constants import Anomaly, DataDrift

from oodles.core.classes.signal_manager import SignalManager
from oodles.core.classes.dataset_handler import DatasetHandler
from oodles.core.classes.model_handler import ModelHandler
from oodles.core.lib.helper_funcs import read_json, write_json
from oodles.core.encoders.numpy_encoder import NumpyEncoder
from oodles.core.classes.data_drift_manager import DataDriftDDM


class Framework:
    """
    Base Framework class which handles model observability and retraining

    ...

    Attributes
    ----------
    fold_name : str
        Path to the folder where selected data-points are logged

    Methods
    -------
    smartly_add_data(inputs, outputs, extra_args=None):
        Checks if the given data-point represents an edge case and needs to be added to the retraining dataset.
    retrain():
        Creates a new version of the model by retraining on collected data.
    """

    def __init__(self, cfg={}):
        """Initialises the Oodles Framework.

        Parameters
        ----------
        cfg : dict
            Config to initialize oodles framework
        """

        cfg.setdefault('checks', [])
        cfg.setdefault('training_args', {})
        cfg.setdefault('evaluation_args', {})
        self.cfg = cfg
        self.signal_manager = SignalManager()
        self.orig_training_file = cfg['training_args'].get("orig_training_file", "")
        self.fold_name = cfg['training_args'].get(
            "fold_name", "oodles_smart_data " + str(datetime.utcnow())
        )
        if os.path.exists(self.fold_name):
            print("Deleting the folder: ", self.fold_name)
            shutil.rmtree(self.fold_name)
        os.mkdir(self.fold_name)
        self.selected_count = 0
        self.predicted_count = 0
        self.version = 1
        self.dataset_handler = DatasetHandler()
        self.model_handler = ModelHandler()
        self.create_data_folders()
        self.ddm_manager = None

        for check in cfg['checks']:
            if check['type'] == Anomaly.EDGE_CASE:
                self.add_signal_formulae(check["signal_formulae"])
            if check['type'] == Anomaly.DATA_DRIFT:
                if check['algorithm'] == DataDrift.DDM:
                    warn_thres = check.get("warn_thres", 2)
                    alarm_thres = check.get("alarm_thres", 3)
                    self.ddm_manager = DataDriftDDM(warn_thres, alarm_thres)
        if "data_transformation_func" in cfg['training_args']:
            self.set_data_transformation_func(cfg['training_args']["data_transformation_func"])
        if "annotation_method" in cfg['training_args']:
            self.set_annotation_method(
                cfg['training_args']["annotation_method"]["method"],
                args=cfg['training_args']["annotation_method"].get("args", {}),
            )
        if "golden_testing_dataset" in cfg['evaluation_args']:
            self.set_golden_testing_dataset(cfg['evaluation_args']["golden_testing_dataset"])
        if "training_func" in cfg['training_args']:
            self.set_training_func(cfg['training_args']["training_func"])
        if "inference_func" in cfg['evaluation_args']:
            self.set_inference_func(cfg['evaluation_args']["inference_func"])

        #TODO: Move concept drift to a Drift Manager class
        self.acc_arr = []

    def create_data_folders(self):
        if not os.path.exists(self.fold_name + "/" + str(self.version)):
            os.mkdir(self.fold_name + "/" + str(self.version))
            os.mkdir(self.fold_name + "/" + str(self.version) + "/smart_data/")
            os.mkdir(self.fold_name + "/" + str(self.version) + "/all_data/")

    def add_data_point_to_all_warehouse(self, inputs, outputs, extra_args={}):
        """Logs all the test cases to data warehouse. Logged under sub-folder 'all_data'"""

        self.add_data_point_to_warehouse(
            inputs,
            outputs,
            "all_data/" + str(self.predicted_count),
            extra_args=extra_args,
        )

    def add_data_point_to_smart_warehouse(self, inputs, outputs, extra_args={}):
        """Logs only the interesting test cases to data warehouse. Logged under sub-folder 'smart_data'"""

        self.add_data_point_to_warehouse(
            inputs,
            outputs,
            "smart_data/" + str(self.selected_count),
            extra_args=extra_args,
        )
        self.selected_count += 1

    def add_data_point_to_warehouse(self, inputs, outputs, warehouse, extra_args={}):
        """Creates a json file per data-point.
        Deletes model-related fields and transforms input, output data in a json-compatible format.
        """

        if "model" in inputs:
            del inputs["model"]

        datapoint = {
            "input": json.dumps(inputs, cls=NumpyEncoder),
            "output": str(outputs),
            "extra_args": str(extra_args),
        }
        write_json(
            self.fold_name + "/" + str(self.version) + "/" + warehouse + ".json",
            datapoint,
        )

    def smartly_add_data(self, inputs, outputs, extra_args={}):
        """Checks if the given data-point is interesting.
        If yes, logs them to smart_data warehouse (which is used to create retraining dataset)
        """

        old_selected_count = self.selected_count
        if self.is_data_interesting(inputs, outputs, extra_args=extra_args):
            # Log the interesting data-points into smart_data warehouse
            self.add_data_point_to_smart_warehouse(
                inputs, outputs, extra_args=extra_args
            )

        # Log all the data-points into all_data warehouse
        self.add_data_point_to_all_warehouse(inputs, outputs, extra_args=extra_args)
        self.predicted_count += 1
        if (not (self.selected_count == old_selected_count)) and (
            self.selected_count % 50 == 0
        ):
            print(
                self.selected_count,
                " edge-cases collected out of ",
                self.predicted_count,
                " inferred samples",
            )

    def add_signal_formulae(self, formulae):
        """Attach the defined signal formulae to identify interesting data-points"""

        self.signal_manager.add_signal_formulae(formulae)

    def is_data_interesting(self, inputs, outputs, extra_args={}):
        """A data-point is deemed interesting if the defined signal is turned on for it"""

        return self.signal_manager.evaluate_signal(
            inputs, outputs, extra_args=extra_args
        )

    def set_data_transformation_func(self, func):
        """Attach data transformation func to convert logged data-point -> Training dataset"""

        self.dataset_handler.set_transformation_func(func)

    def set_annotation_method(self, method, args={}):
        """Attach data annotation pipeline"""

        self.dataset_handler.set_annotation_method(method, args=args)

    def need_retraining(self):
        """Checks if enough data-points are collected and the framework needs to kickoff model retraining"""

        if self.selected_count > 250:
            return True
        return False

    def retrain(self):
        """Retrains the model. Executes following steps sequentially.
        - Creates Retraining dataset by collecting data from the 'smart_data' warehouse
        - Retrains the model and saves it under the new version
        - Kicks off model comparison report
        - Deploys the new model and increments model version by 1
        """

        dataset_location = self.fold_name + "/" + str(self.version)
        print("Kicking off re-training")
        print(
            str(self.selected_count),
            "data-points selected out of " + str(self.predicted_count),
        )

        # Collect newly collected data
        new_data = [
            read_json(dataset_location + "/smart_data/" + x)
            for x in os.listdir(dataset_location + "/smart_data/")
        ]
        # Generate training dataset
        self.dataset_handler.create_retraining_dataset(
            dataset_location, new_data, self.orig_training_file
        )
        # Retrain the model
        self.model_handler.retrain(
            dataset_location + "/training_dataset.json", self.version
        )
        print("Model retraining done...")
        print("Generating comparison report...")

        # Generate Model report
        self.model_handler.compare_new_model(
            self.golden_testing_dataset,
            self.version,
            self.orig_training_file,
            self.selected_count,
        )

        # TODO: Deploy new model
        self.version += 1
        self.selected_count = 0
        self.create_data_folders()

    def set_training_func(self, func):
        """Attach model training pipeline"""
        self.model_handler.set_training_func(func)

    def set_golden_testing_dataset(self, dataset):
        """Attach testing dataset for model comparison"""
        self.golden_testing_dataset = dataset

    def set_inference_func(self, func):
        """Attach inference pipeline for model comparison"""
        self.model_handler.set_inference_func(func)

    def check_for_data_drift(self, inputs, outputs):
        if self.ddm_manager:
            if "y_test" in inputs.keys():
                y_gt = inputs["y_test"]
                y_pred = outputs

                for i, _ in enumerate(y_pred):
                    if y_pred[i] == y_gt[i]:
                        out = self.ddm_manager.add_prediction(0)
                    else:
                        out = self.ddm_manager.add_prediction(1)
                    if out:
                        break
