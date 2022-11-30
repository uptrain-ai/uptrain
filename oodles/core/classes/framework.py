import json
import os
import shutil
import copy
import numpy as np
from datetime import datetime

from oodles.core.classes.dataset_handler import DatasetHandler
from oodles.core.classes.model_handler import ModelHandler
from oodles.core.classes.anomaly_manager import AnomalyManager
from oodles.core.lib.helper_funcs import read_json, write_json
from oodles.core.encoders.numpy_encoder import NumpyEncoder


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

        cfg.setdefault("checks", [])
        cfg.setdefault("training_args", {})
        cfg.setdefault("evaluation_args", {})
        cfg.setdefault("data_identifier", "identifier")
        cfg.setdefault("batch_size", 1)
        self.cfg = cfg

        self.orig_training_file = cfg["training_args"].get("orig_training_file", "")
        self.fold_name = cfg["training_args"].get(
            "fold_name", "oodles_smart_data " + str(datetime.utcnow())
        )
        if os.path.exists(self.fold_name):
            print("Deleting the folder: ", self.fold_name)
            shutil.rmtree(self.fold_name)
        os.mkdir(self.fold_name)

        self.log_folder = cfg["training_args"].get(
            "log_folder", "oodles_logs " + str(datetime.utcnow())
        )
        if os.path.exists(self.log_folder):
            shutil.rmtree(self.log_folder)

        self.selected_count = 0
        self.predicted_count = 0
        self.version = 1
        self.anomaly_manager = AnomalyManager(cfg["checks"], self.log_folder)
        self.dataset_handler = DatasetHandler()
        self.model_handler = ModelHandler()
        self.create_data_folders()

        self.batch_size = cfg["batch_size"]
        self.data_identifier_type = cfg["data_identifier"]
        self.data_summary_file = self.fold_name + "/data_summary.json"
        self.summary_data = {"all_data": [], "smart_data": [], "versions": {}}
        write_json(self.data_summary_file, self.summary_data)

        if "data_transformation_func" in cfg["training_args"]:
            self.set_data_transformation_func(
                cfg["training_args"]["data_transformation_func"]
            )
        if "annotation_method" in cfg["training_args"]:
            self.set_annotation_method(
                cfg["training_args"]["annotation_method"]["method"],
                args=cfg["training_args"]["annotation_method"].get("args", {}),
            )
        if "golden_testing_dataset" in cfg["evaluation_args"]:
            self.set_golden_testing_dataset(
                cfg["evaluation_args"]["golden_testing_dataset"]
            )
        if "training_func" in cfg["training_args"]:
            self.set_training_func(cfg["training_args"]["training_func"])
        if "inference_func" in cfg["evaluation_args"]:
            self.set_inference_func(cfg["evaluation_args"]["inference_func"])

    def create_data_folders(self):
        if not os.path.exists(self.fold_name + "/" + str(self.version)):
            os.mkdir(self.fold_name + "/" + str(self.version))
            os.mkdir(self.fold_name + "/" + str(self.version) + "/smart_data/")
            os.mkdir(self.fold_name + "/" + str(self.version) + "/all_data/")

    def add_data_point_to_all_warehouse(self, inputs, outputs, gts=None, extra_args={}):
        """Logs all the test cases to data warehouse. Logged under sub-folder 'all_data'"""

        saved = self.add_data_point_to_warehouse(
            inputs,
            outputs,
            "all_data/",
            gts=gts,
            extra_args=extra_args,
        )
        if not saved["is_repeat"]:
            self.summary_data["all_data"].append(saved)
            self.predicted_count += 1

    def add_data_point_to_smart_warehouse(
        self, inputs, outputs, gts=None, extra_args={}
    ):
        """Logs only the interesting test cases to data warehouse. Logged under sub-folder 'smart_data'"""

        saved = self.add_data_point_to_warehouse(
            inputs,
            outputs,
            "smart_data/",
            gts=gts,
            extra_args=extra_args,
        )
        if not saved["is_repeat"]:
            self.summary_data["smart_data"].append(saved)
            self.selected_count += 1

    def add_data_point_to_warehouse(
        self, inputs, outputs, warehouse, gts=None, extra_args={}
    ):
        """Creates a json file per data-point.
        Deletes model-related fields and transforms input, output data in a json-compatible format.
        """

        if "model" in inputs:
            del inputs["model"]

        identifier = extra_args["identifier"]
        path = (
            self.fold_name
            + "/"
            + str(self.version)
            + "/"
            + warehouse
            + str(identifier[0])
            + ".json"
        )
        is_repeat = True

        if not os.path.exists(path):
            is_repeat = False
            datapoint = {
                "input": json.dumps(inputs, cls=NumpyEncoder),
                "output": json.dumps(outputs, cls=NumpyEncoder),
                "gt": json.dumps(gts, cls=NumpyEncoder),
                "extra_args": json.dumps(extra_args, cls=NumpyEncoder),
                "identifier": json.dumps(identifier, cls=NumpyEncoder),
            }
            write_json(
                path,
                datapoint,
            )

        return {"path": path, "identifier": identifier, "is_repeat": is_repeat}

    def get_data_identifier(self, inputs, extra_args={}):
        if self.data_identifier_type in inputs:
            return inputs[self.data_identifier_type]
        elif self.data_identifier_type in extra_args:
            return extra_args[self.data_identifier_type]
        elif self.data_identifier_type in ["utc_timestamp", "identifier"]:
            return [str(datetime.utcnow())]
        raise Exception("Invalid Data Identifier type %s" % self.data_identifier_type)

    def smartly_add_data(self, inputs, outputs, gts=None, extra_args={}):
        """
        Checks if the given data-point is interesting.
        If yes, logs them to smart_data warehouse, which
        is used to create retraining dataset.
        """

        old_selected_count = self.selected_count
        this_identifier = self.get_data_identifier(inputs, extra_args=extra_args)
        extra_args.update({"identifier": this_identifier})

        # Log all the data-points into all_data warehouse
        self.add_data_point_to_all_warehouse(
            inputs, outputs, gts=gts, extra_args=extra_args
        )

        if self.is_data_interesting(inputs, outputs, gts=gts, extra_args=extra_args):
            # Log the interesting data-points into smart_data warehouse
            self.add_data_point_to_smart_warehouse(
                inputs, outputs, gts=gts, extra_args=extra_args
            )

        if (not (self.selected_count == old_selected_count)) and (
            self.selected_count % 50 == 0
        ):
            print(
                self.selected_count,
                " edge-cases collected out of ",
                self.predicted_count,
                " inferred samples",
            )
        return this_identifier

    def extract_data_point_from_batch(self, data, i):
        if isinstance(data, dict):
            this_data = {}
            for key in list(data.keys()):
                this_data.update(
                    {key: self.extract_data_point_from_batch(data[key], i)}
                )
            return this_data
        elif isinstance(data, np.ndarray):
            if data.shape[0] == self.batch_size:
                return np.array([data[i]])
            else:
                return data
        elif isinstance(data, list):
            if len(data) == self.batch_size:
                return [data[i]]
            else:
                return data
        else:
            return data

    def check_and_add_data(
        self, inputs, outputs, gts=None, extra_args={}, batch_size=-1
    ):
        if batch_size < 0:
            batch_size = self.batch_size

        # TODO: We are assuming inputs = BATCH_SIZE x INPUT_SIZE,
        # Current implementation assumes BATCH_SIZE = 1, how do we extend this?
        identifiers = []
        for i in range(batch_size):
            this_inputs = self.extract_data_point_from_batch(inputs, i)
            this_outputs = self.extract_data_point_from_batch(outputs, i)
            this_gts = self.extract_data_point_from_batch(gts, i)
            this_extra_args = self.extract_data_point_from_batch(extra_args, i)

            self.check(
                this_inputs, this_outputs, gts=this_gts, extra_args=this_extra_args
            )
            this_identifiers = self.smartly_add_data(
                this_inputs, this_outputs, gts=this_gts, extra_args=this_extra_args
            )
            identifiers.append(this_identifiers[0])
        return np.array(identifiers)

    def check(self, inputs, outputs, gts=None, extra_args={}):
        return self.anomaly_manager.check(
            inputs, outputs, gts=gts, extra_args=extra_args
        )

    def is_data_interesting(self, inputs, outputs, gts=None, extra_args={}):
        """A data-point is deemed interesting if the defined signal is turned on for it"""
        return self.anomaly_manager.is_data_interesting(
            inputs, outputs, gts=gts, extra_args=extra_args
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
            write_json(
                self.data_summary_file, json.dumps(self.summary_data, cls=NumpyEncoder)
            )
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

    def attach_ground_truth(self, gt_data):
        if type(gt_data) is str:
            gt_file = copy.deepcopy(gt_data)
            gt_data = read_json(gt_file)
        elif type(gt_data) is dict:
            gt_data = [gt_data]

        summary_data = self.summary_data
        all_idens_in_smart_data = np.array(
            [x["identifier"] for x in summary_data["smart_data"]]
        )
        all_idens_in_all_data = np.array(
            [x["identifier"] for x in summary_data["all_data"]]
        )

        for full_gt_row in gt_data:
            for i in range(len(full_gt_row["gt"])):
                gt_row = self.extract_data_point_from_batch(full_gt_row, i)
                all_data_files_to_be_checked = []
                files_to_be_updated = []
                this_iden = gt_row[self.data_identifier_type]
                this_gt = gt_row["gt"]

                all_data_idx = np.where(all_idens_in_all_data == this_iden)[0]
                if len(all_data_idx):
                    files_to_be_updated.append(
                        summary_data["all_data"][all_data_idx[0]]["path"]
                    )
                    all_data_files_to_be_checked.append(
                        summary_data["all_data"][all_data_idx[0]]["path"]
                    )

                smart_data_idx = np.where(all_idens_in_smart_data == this_iden)[0]
                if len(smart_data_idx):
                    files_to_be_updated.append(
                        summary_data["smart_data"][smart_data_idx[0]]["path"]
                    )

                for file_to_be_updated in files_to_be_updated:
                    old_data = read_json(file_to_be_updated)
                    old_data.update({"gt": json.dumps(this_gt, cls=NumpyEncoder)})
                    write_json(file_to_be_updated, old_data)

                for file_to_be_checked in all_data_files_to_be_checked:
                    this_saved_data = read_json(file_to_be_checked)
                    self.check_and_add_data(
                        json.loads(this_saved_data["input"]),
                        json.loads(this_saved_data["output"]),
                        gts=json.loads(this_saved_data["gt"]),
                        extra_args=json.loads(this_saved_data["extra_args"]),
                        batch_size=1,
                    )
