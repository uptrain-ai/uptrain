from __future__ import annotations
from copy import deepcopy
import json
import os
import shutil
from datetime import datetime
import random
from queue import SimpleQueue
from threading import Thread
from typing import Optional

import pandas as pd
import numpy as np
from sklearn.preprocessing import normalize

from uptrain.v0.core.classes.helpers import DatasetHandler, ModelHandler, config_handler
from uptrain.v0.core.classes.logging import LogHandler
from uptrain.v0.core.classes.logging.new_log_handler import LogHandler as NewLogHandler
from uptrain.v0.core.classes.managers import CheckManager
from uptrain.v0.core.classes.io import RunTimeManager
from uptrain.v0.core.lib.helper_funcs import (
    read_json,
    extract_data_points_from_batch,
    add_data_to_warehouse,
    get_df_indices_from_ids,
    get_feature_names_list,
    load_list_from_df,
    clear_directory,
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
        """Initialises the uptrain Framework.

        Parameters
        ----------
        cfg : dict
            Config to initialize uptrain framework
        """

        cfg = config_handler.Config(**cfg_dict)
        self.config_obj = cfg
        self.run_background_log_consumer = cfg.run_background_log_consumer

        if self.run_background_log_consumer:
            self.msg_queue = SimpleQueue()
            cfg_copy = deepcopy(cfg_dict)
            cfg_copy.update({"run_background_log_consumer": False})
            daemon = Thread(
                target=background_log_consumer_task,
                args=(
                    self.msg_queue,
                    cfg_copy,
                ),
                daemon=True,
                name="Background Log Consumer",
            )
            daemon.start()
        else:
            training_args = cfg.training_args
            evaluation_args = cfg.evaluation_args
            self.reader_args = cfg.reader_args

            self.orig_training_file = training_args.orig_training_file
            self.fold_name = cfg.retraining_folder
            if os.path.exists(self.fold_name):
                print("Deleting contents of the folder: ", self.fold_name)
                clear_directory(self.fold_name)
            else:
                os.mkdir(self.fold_name)

            self.log_data = cfg.logging_args.log_data
            self.use_cache = cfg.use_cache
            self.cache = {}
            self.predicted_count = 0
            self.extra_args = {}
            self.checks = cfg.checks
            self.batch_size = None
            self.feat_name_list = cfg.feat_name_list
            self.retrain_after = cfg.retrain_after
            self.data_id_type = cfg.data_id
            self.version = 0
            self.if_retraining = cfg.retrain
            self.path_all_data = os.path.join(self.fold_name, "all_data.csv")

            # TODO: placeholder till we decide on which way to go
            if cfg.logging_args.use_new_handler:
                self.log_handler = NewLogHandler(framework=self, cfg=cfg)
            else:
                self.log_handler = LogHandler(framework=self, cfg=cfg)

            self.dataset_handler = DatasetHandler(framework=self, cfg=cfg)
            self.model_handler = ModelHandler()
            self.check_manager = CheckManager(self, self.checks)
            self.reset_retraining()

            if training_args.data_transformation_func:
                self.set_data_transformation_func(
                    training_args.data_transformation_func
                )
            if training_args.annotation_method:
                am = training_args.annotation_method
                self.set_annotation_method(am.method, args=am.args)
            if evaluation_args.golden_testing_dataset:
                self.set_golden_testing_dataset(evaluation_args.golden_testing_dataset)
            if training_args.training_func:
                self.set_training_func(training_args.training_func)
            if evaluation_args.inference_func:
                self.set_inference_func(evaluation_args.inference_func)

            if self.reader_args.mode == 'continuous':
                self.runtime_manager = RunTimeManager(self.reader_args, self)


    def reset_retraining(self):
        self.version += 1
        self.selected_count = 0
        self.smart_data_ids = []
        retrain_folder = os.path.join(self.fold_name, str(self.version))
        if not os.path.exists(retrain_folder):
            os.mkdir(retrain_folder)

    def get_data_id(self, inputs):
        if self.data_id_type in inputs:
            ids = inputs[self.data_id_type]
        elif self.data_id_type in inputs:
            ids = inputs[self.data_id_type]
        elif self.data_id_type == "utc_timestamp":
            timestamp = str(datetime.utcnow().timestamp()).replace(".", "")
            rand_int = random.sample(
                range(10 * self.batch_size), self.batch_size
            ).sort()
            ids = [int(timestamp + str(x)) for x in rand_int]
        elif self.data_id_type == "id":
            ids = list(
                range(self.predicted_count, self.predicted_count + self.batch_size)
            )
        else:
            raise Exception("Invalid Data id type: %s" % self.data_id_type)
        return ids

    def smartly_add_data(self, data, extra_args={}):
        """
        Checks if the given data-point is interesting.
        If yes, logs them to smart_data warehouse, which
        is used to create retraining dataset.
        """

        old_selected_count = self.selected_count
        smart_data = {}

        is_interesting, reasons = self.is_data_interesting(
            data, data["output"], data["gt"], extra_args=extra_args
        )
        num_selected_datapoints = np.sum(np.array(is_interesting))
        self.selected_count += num_selected_datapoints
        self.smart_data_ids.extend(np.array(data["id"])[np.array(is_interesting)])

        """
        Log only the interesting test cases to data
        warehouse. Logged under sub-folder 'smart_data'
        """
        path_smart_data = os.path.join(
            self.fold_name, str(self.version), "smart_data.csv"
        )

        if self.log_data and (num_selected_datapoints > 0):
            data.update({"reasons": reasons})
            smart_data = extract_data_points_from_batch(
                data, np.where(is_interesting == True)[0]
            )
            add_data_to_warehouse(deepcopy(smart_data), path_smart_data)

        edge_cases_txt = (
            str(self.selected_count)
            + " edge cases identified out of "
            + str(self.predicted_count)
            + " total samples"
        )
        if self.selected_count > 0:
            self.log_handler.add_alert(
                "Number of edge cases collected", edge_cases_txt, "edge_cases"
            )

        if (not (self.selected_count == old_selected_count)) and (
            not (int(self.selected_count / 50) == int(old_selected_count / 50))
        ):
            print(edge_cases_txt)

    def infer_batch_size(self, inputs):
        batch_sizes = []
        for k, item in inputs.items():
            item_batch_size = len(item)
            batch_sizes.append(item_batch_size)
        if np.var(np.array(batch_sizes)) > 0:
            # TODO: Raise warning on what is going wrong
            raise Exception("Batch size should be same for all input features")
        return batch_sizes[0]

    def check_and_add_data(self, inputs, outputs, gts=None, extra_args={}):
        # inputs = dict(config_handler.InputArgs(**inputs))
        if ("id" in inputs) and (inputs["id"] is None):
            del inputs["id"]
        self.batch_size = self.infer_batch_size(inputs)

        ids = self.get_data_id(inputs)
        inputs.update({"id": ids})

        if self.feat_name_list is None:
            self.feat_name_list = get_feature_names_list(inputs)

        outputs = list(outputs) if outputs is not None else [None] * self.batch_size
        gts = list(gts) if gts is not None else [None] * self.batch_size
        data = inputs
        data.update(
            {
                "output": list(outputs),
                "gt": gts,
            }
        )

        # Check for any monitors
        self.check(data, extra_args)
        self.predicted_count += self.batch_size

        if self.log_data:
            data.update(extra_args)
            # Log all the data-points into all_data warehouse
            add_data_to_warehouse(deepcopy(data), self.path_all_data)

        # Smartly add data for retraining
        self.smartly_add_data(data, extra_args)
        self.extra_args = extra_args
        return ids

    def check(self, data, extra_args={}):
        extra_args.update({"id": data["id"]})
        self.check_manager.check(
            data,
            data["output"],
            gts=data["gt"],
            extra_args=extra_args,
        )

    def is_data_interesting(self, inputs, outputs, gts=None, extra_args={}):
        """A data-point is deemed interesting if the defined signal is positive"""
        return self.check_manager.is_data_interesting(
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
        if self.if_retraining:
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
        print("\nKicking off re-training")
        # print(
        #     str(self.selected_count),
        #     "data-points selected out of " + str(self.predicted_count),
        # )

        # Collect newly collected data
        df = pd.read_csv(self.path_all_data)
        smart_data_indices = get_df_indices_from_ids(df, self.smart_data_ids)
        df_smart_data = df.loc[smart_data_indices]
        for feat in self.feat_name_list:
            df_smart_data[feat] = df_smart_data[feat].apply(json.loads)
        retraining_data = df_smart_data.to_dict(orient="records")

        # Generate training dataset
        self.dataset_handler.create_retraining_dataset(
            dataset_location, retraining_data, self.orig_training_file
        )
        # Retrain the model
        self.model_handler.retrain(
            dataset_location + "/training_dataset.json", self.version
        )
        print("Model retraining done...\n")
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
        df.loc[gt_id_indices, "gt"] = np.array(gt_data["gt"], dtype="object")
        df.to_csv(self.path_all_data, index=False)

        """
        TODO: Currently assumes that input is only one column.
        In some cases, the input might have multiple data
        structures (e.g., cascaded models).
        """
        df_gt = df.loc[gt_id_indices]
        data = dict(
            zip(
                self.feat_name_list,
                [load_list_from_df(df_gt, x) for x in self.feat_name_list],
            )
        )
        data.update(
            {
                "output": load_list_from_df(df_gt, "output"),
                "id": list(gt_data["id"]),
                "gt": list(gt_data["gt"]),
            }
        )
        self.check(data, extra_args=self.extra_args)
        self.smartly_add_data(data, extra_args=self.extra_args)

    # TODO: @Vipul - Do we need this?
    def feat_slicing(self, relevant_feat_list, limit_list):
        """
        This function checks anomalies for a subset of data.
        feat_name: Feature on which data slicing is done.
        lower_limit: Lower limit for feature value
        upper_limit: Upper limit for feature value
        """
        df = pd.read_csv(self.path_all_data)
        input_arr = np.array(load_list_from_df(df, "data"))

        # Create normalized array
        input_arr = normalize(input_arr, axis=1, norm="l1")
        relevant_ids_all = set(range(len(input_arr)))
        for i, feat_name in enumerate(relevant_feat_list):
            feat_id = self.feat_name_list.index(feat_name)
            relevant_ids = (input_arr[:, feat_id] >= limit_list[i][0]) & (
                input_arr[:, feat_id] <= limit_list[i][1]
            )
            relevant_ids_all = relevant_ids_all.intersection(set(relevant_ids))

        df_feat = df.loc[relevant_ids]
        self.batch_size = len(df_feat)

        data = {
            "data": load_list_from_df(df_feat, "data"),
            "output": load_list_from_df(df_feat, "output"),
            "id": load_list_from_df(df_feat, "id"),
            "gt": load_list_from_df(df_feat, "gt"),
        }
        self.extra_args.update({"feat_name": feat_name})
        self.check_manager = CheckManager(self, self.checks)
        self.check(data, extra_args=self.extra_args)

    def log_measurable(self, ids, vals, col_name):
        for idx in range(len(ids)):
            self.cache[col_name].update(
                {ids[idx]: extract_data_points_from_batch(vals, idx)}
            )

    def convert_inputs_table_to_dict(self, inputs):
        cols = inputs.columns.tolist()
        ids = inputs.index.tolist()
        data = {}
        for col in cols:
            data.update({col: np.array(list(inputs[col]))})
        if "id" not in cols:
            data.update({"id": np.array(ids)})
        return data

    def convert_dict_values_to_numpy_values(self, inputs: dict) -> dict:
        data = {}
        for key, value in inputs.items():
            data.update({key: np.array(value)})
        return data


    def run_endlessly(self):
        self.runtime_manager.run_endlessly()


    def log(
        self,
        inputs=None,
        outputs=None,
        gts=None,
        identifiers=None,
        extra=None,
    ):
        if self.run_background_log_consumer:
            data = {
                "inputs": inputs,
                "outputs": outputs,
                "gts": gts,
                "identifiers": identifiers,
                "extra": extra,
            }
            try:
                self.msg_queue.put(data)
            except:
                print("Model monitoring failed!")
            # Return identifiers by fetching it from the background thread
            return
        else:
            # if (inputs is not None) and (outputs is None):
            #     raise Exception("Predictions should be present while logging inputs")
            if (inputs is None) and (outputs is not None):
                raise Exception("Inputs should be present while logging predictions")
            if (gts is not None) and (identifiers is None):
                raise Exception(
                    "Identifiers should be present while logging ground truths"
                )

            if inputs is not None:
                if isinstance(inputs, pd.DataFrame):
                    inputs = self.convert_inputs_table_to_dict(inputs)
                elif isinstance(inputs, dict):
                    inputs = self.convert_dict_values_to_numpy_values(inputs)
                else:
                    raise Exception(
                        "Inputs was expected to be a Pandas Dataframe or Python Dictionary"
                    )
                identifiers = self.check_and_add_data(inputs, outputs)

            if gts is not None:
                self.attach_ground_truth({"id": identifiers, "gt": gts})

            if self.need_retraining():
                self.retrain()

            return identifiers

    def clear_cache(self):
        self.cache = {}


def background_log_consumer_task(msg_queue, cfg):
    framework = Framework(cfg_dict=cfg)
    # run forever
    while True:
        # get the next message
        data = msg_queue.get()

        # log the message
        framework.log(
            inputs=data["inputs"],
            outputs=data["outputs"],
            gts=data["gts"],
            identifiers=data["identifiers"],
            extra=data["extra"],
        )
