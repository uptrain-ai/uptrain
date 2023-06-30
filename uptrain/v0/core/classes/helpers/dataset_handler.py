import numpy as np
from uptrain.v0.core.classes.helpers import AnnotationHelper
from uptrain.v0.core.lib.helper_funcs import read_json, write_json, cluster_and_plot_data
from uptrain.v0.constants import AnnotationMethod


class DatasetHandler:
    """
    Handler class to help with all the dataset related functionalities

    ...
    Attributes
    ----------
    transformation_func : func
        Used to transform logged data-points to training compatible data-points
    annotation_method: AnnotationMethod
        Attached annotation method

    Methods
    -------
    add_annotations(dataset):
        Calls the Annotation Helper to add gt to retraining dataset
    set_transformation_func(func):
        Attach data transformation func to convert logged data-point -> Training dataset
    set_annotation_method(method):
        Set the annotation method
    """

    def __init__(self, framework=None, cfg=None, transformation_func=(lambda x: x)):
        self.transformation_func = transformation_func
        self.cluster_plot_func = cfg.cluster_visualize_func
        self.log_handler = framework.log_handler
        np.random.seed(10)

    def add_annotations(self, dataset):
        """Adds gt to the dataset file by calling appropriate funcs on the annotation helper based on attached annotation method"""

        if self.annotation_method == AnnotationMethod.MASTER_FILE:
            annotated_data = self.annotation_helper.annotations_from_master_file(
                dataset
            )
        else:
            raise Exception("Unsupported annotation method")
        return annotated_data

    def set_transformation_func(self, func):
        """Attach data transformation func to convert logged data-point -> Training dataset"""

        self.transformation_func = func

    def set_annotation_method(self, method, args={}):
        """Set data annotation method"""

        self.annotation_method = method
        self.annotation_helper = AnnotationHelper(args=args)

    def transform_collected_data(self, data):
        """Transforms logged data via self.transformation_func"""
        if self.transformation_func:
            transformed_data = [self.transformation_func(x) for x in data]
            return transformed_data

    def create_retraining_dataset(
        self, dataset_location, new_data, old_dataset, ratio=5
    ):
        """Creates retraining dataset by combining original training data with collected data-points
        - Transforms logged data-points via transformation_func
        - Add annotatons via attached annotation method
        - Combine old training data and newly collected data into retraining dataset file
        """

        new_data = self.transform_collected_data(new_data)
        write_json(dataset_location + "/cleaned_dataset.json", new_data)

        if self.cluster_plot_func is not None:
            cluster_and_plot_data(
                np.array([x["kps"] for x in new_data]),
                9,
                cluster_plot_func=self.cluster_plot_func,
                plot_save_name=self.log_handler.get_plot_save_name(
                    "collected_edge_cases_clusters.png", "edge_cases"
                ),
            )

        new_data = self.add_annotations(dataset_location + "/cleaned_dataset.json")
        write_json(dataset_location + "/annotated_dataset.json", new_data)
        write_json(
            dataset_location + "/training_dataset.json",
            self.merge_training_datasets(
                old_dataset, dataset_location + "/annotated_dataset.json", ratio=ratio
            ),
        )
        print(
            "Creating retraining dataset:",
            dataset_location + "/training_dataset.json",
            " by merging ",
            old_dataset,
            " and collected edge cases.\n",
        )

    def merge_training_datasets(self, old_dataset, new_dataset, ratio=1):
        """Merges two datasets with weights = specified ratio.
        Supports only integer ratios
        """

        old_data = read_json(old_dataset)
        new_data = read_json(new_dataset)
        new_data_upsampled = new_data * int(round(ratio))
        old_data.extend(new_data_upsampled)
        return old_data
