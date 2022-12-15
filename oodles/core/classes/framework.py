from collections import OrderedDict
from copy import deepcopy
import json
import os
import shutil
import pandas as pd
from datetime import datetime
import random
import numpy as np

from oodles.core.classes.helpers import DatasetHandler, ModelHandler
from oodles.core.classes.helpers import config_handler
from oodles.core.classes.anomalies.managers import AnomalyManager
from oodles.core.lib.helper_funcs import (
    read_json,
    extract_data_point_from_batch,
    add_data_to_warehouse,
    add_data_to_batch,
    get_df_indices_from_ids,
)


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
        Checks if the given data-point represents an edge case
        and needs to be added to the retraining dataset.
    retrain():
        Creates a new version of the model by retraining
        on collected data.
    """

    def __init__(self, cfg_dict={}):
        """Initialises the Oodles Framework.

        Parameters
        ----------
        cfg : dict
            Config to initialize oodles framework
        """

        cfg = config_handler.Config(**cfg_dict)
        training_args = cfg.training_args
        evaluation_args = cfg.evaluation_args

        self.orig_training_file = training_args.orig_training_file
        self.fold_name = training_args.fold_name
        if os.path.exists(self.fold_name):
            print("Deleting the folder: ", self.fold_name)
            shutil.rmtree(self.fold_name)
        os.mkdir(self.fold_name)

        self.log_folder = training_args.log_folder
        if os.path.exists(self.log_folder):
            shutil.rmtree(self.log_folder)

        self.predicted_count = 0
        self.extra_args = {}
        self.anomaly_manager = AnomalyManager(
            cfg.checks, log_args={"log_folder": self.log_folder}
        )
        self.dataset_handler = DatasetHandler(
            cluster_plot_func=training_args.cluster_plot_func
        )
        self.model_handler = ModelHandler()

        self.version = 0
        self.reset_retraining()
        self.path_all_data = os.path.join(self.fold_name, "all_data.csv")

        self.batch_size = cfg.batch_size
        self.retrain_after = cfg.retrain_after
        self.data_id_type = cfg.data_id

        if training_args.data_transformation_func:
            self.set_data_transformation_func(training_args.data_transformation_func)
        if training_args.annotation_method:
            am = training_args.annotation_method
            self.set_annotation_method(am.method, args=am.args)
        if evaluation_args.golden_testing_dataset:
            self.set_golden_testing_dataset(evaluation_args.golden_testing_dataset)
        if training_args.training_func:
            self.set_training_func(training_args.training_func)
        if evaluation_args.inference_func:
            self.set_inference_func(evaluation_args.inference_func)

    def reset_retraining(self):
        self.version += 1
        self.selected_count = 0
        self.smart_data_ids = []
        retrain_folder = os.path.join(self.fold_name, str(self.version))
        if not os.path.exists(retrain_folder):
            os.mkdir(retrain_folder)

    def get_data_id(self, inputs):
        if inputs[self.data_id_type]:
            return inputs[self.data_id_type]
        elif self.data_id_type == "utc_timestamp":
            timestamp = str(datetime.utcnow().timestamp()).replace(".", "")
            rand_int = random.sample(
                range(10 * self.batch_size), self.batch_size
            ).sort()
            ids = [int(timestamp + str(x)) for x in rand_int]
            return ids
        elif self.data_id_type == "id":
            ids = list(
                range(self.predicted_count, self.predicted_count + self.batch_size)
            )
            return ids
        raise Exception("Invalid Data id type: %s" % self.data_id_type)

    def smartly_add_data(self, data, extra_args={}):
        """
        Checks if the given data-point is interesting.
        If yes, logs them to smart_data warehouse, which
        is used to create retraining dataset.
        """

        old_selected_count = self.selected_count
        smart_data = {}
        for i in range(self.batch_size):
            this_data = extract_data_point_from_batch(data, i)
            if this_data["id"][0] not in self.smart_data_ids:
                if self.is_data_interesting(
                    this_data["data"],
                    this_data["output"],
                    gts=this_data["gt"],
                    extra_args=extra_args,
                ):
                    smart_data = add_data_to_batch(smart_data, this_data)
                    self.smart_data_ids.append(this_data["id"][0])
                    self.selected_count += 1

        """
        Log only the interesting test cases to data 
        warehouse. Logged under sub-folder 'smart_data'
        """
        path_smart_data = os.path.join(
            self.fold_name, str(self.version), "smart_data.csv"
        )
        add_data_to_warehouse(smart_data, path_smart_data)

        if (not (self.selected_count == old_selected_count)) and (
            self.selected_count % 50 == 0
        ):
            print(
                self.selected_count,
                " edge-cases collected out of ",
                self.predicted_count,
                " inferred samples",
            )

    def check_and_add_data(self, inputs, outputs, gts=None, extra_args={}):
        inputs = dict(config_handler.InputArgs(**inputs))
        ids = self.get_data_id(inputs)
        gts = list(gts) if gts is not None else [None] * self.batch_size
        data = OrderedDict(inputs)
        data.update(
            {
                "output": list(outputs),
                "id": list(ids),
                "gt": gts,
            }
        )

        # Check for any anomalies
        self.check(data, extra_args)
        self.predicted_count += self.batch_size

        # Log all the data-points into all_data warehouse
        add_data_to_warehouse(deepcopy(data), self.path_all_data)

        # Smartly add data for retraining
        self.smartly_add_data(data, extra_args)
        self.extra_args = extra_args
        return ids

    def check(self, data, extra_args={}):
        for i in range(self.batch_size):
            this_data = extract_data_point_from_batch(data, i)
            if this_data["gt"] == [None]:
                this_data["gt"] = None

            """Note: We assume that the input dict has test data in key data"""
            self.anomaly_manager.check(
                this_data["data"],
                this_data["output"],
                gts=this_data["gt"],
                extra_args=extra_args,
            )

    def is_data_interesting(self, inputs, outputs, gts=None, extra_args={}):
        """A data-point is deemed interesting if the defined signal is positive"""
        if gts == [None]:
            gts = None
        return self.anomaly_manager.is_data_interesting(
            inputs, outputs, gts=gts, extra_args=extra_args
        )

    def set_data_transformation_func(self, func):
        """Attach data transformation func to convert
        logged data-point -> Training dataset"""
        self.dataset_handler.set_transformation_func(func)

    def set_annotation_method(self, method, args={}):
        """Attach data annotation pipeline"""
        self.dataset_handler.set_annotation_method(method, args=args)

    def need_retraining(self):
        """Checks if enough data-points are collected and the
        framework needs to kickoff model retraining"""

        if self.selected_count > self.retrain_after:
            return True
        return False

    def retrain(self):
        """Retrains the model. Executes following steps sequentially.
        - Creates Retraining dataset by collecting data from the 'smart_data' warehouse
        - Retrains the model and saves it under the new version
        - Kicks off model comparison report
        - Deploys the new model and increments model version by 1
        """

        dataset_location = os.path.join(self.fold_name, str(self.version))
        print("Kicking off re-training")
        print(
            str(self.selected_count),
            "data-points selected out of " + str(self.predicted_count),
        )

        # Collect newly collected data
        df = pd.read_csv(self.path_all_data)
        smart_data_indices = get_df_indices_from_ids(df, self.smart_data_ids)
        df_smart_data = df.loc[smart_data_indices]
        df_smart_data["data"] = df_smart_data["data"].apply(json.loads)
        retraining_data = df_smart_data.to_dict(orient="records")

        # Generate training dataset
        self.dataset_handler.create_retraining_dataset(
            dataset_location, retraining_data, self.orig_training_file
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
        self.reset_retraining()

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
            gt_data = read_json(gt_data)
        elif type(gt_data) is not dict:
            print(f"Ground truth datatype {type(gt_data)} not supported.")
        gt_data = dict(config_handler.GroundTruthArgs(**gt_data))

        self.batch_size = len(gt_data["gt"])

        df = pd.read_csv(self.path_all_data)
        gt_id_indices = get_df_indices_from_ids(df, gt_data["id"])
        df.loc[gt_id_indices, "gt"] = np.array(gt_data["gt"], dtype='object')
        df.to_csv(self.path_all_data, index=False)

        """
        TODO: Currently assumes that input is only one column. 
        In some cases, the input might have multiple data 
        structures (e.g., cascaded models). 
        Note: gt_data is assumed to be a dictionary.
        """
        df_gt = df.loc[gt_id_indices]
        inputs = [json.loads(x) for x in list(df_gt["data"])]
        try:
            outputs = [json.loads(x) for x in list(df_gt["output"])]
        except:
            out_json = [json.dumps(x) for x in list(df_gt["output"])]
            outputs = [json.loads(x) for x in out_json]
        data = {
            "data": list(inputs),
            "output": list(outputs),
            "id": list(gt_data["id"]),
            "gt": list(gt_data["gt"]),
        }
        self.check(data, extra_args=self.extra_args)
        self.smartly_add_data(data, extra_args=self.extra_args)
