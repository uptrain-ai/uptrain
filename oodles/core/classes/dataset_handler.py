import numpy as np

from oodles.core.classes.annotation_helper import AnnotationHelper
from oodles.core.lib.helper_funcs import read_json, write_json
from oodles.constants import AnnotationMethod


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

    def __init__(self, transformation_func=(lambda x: x)):
        self.transformation_func = transformation_func
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

        transformed_data = [self.transformation_func(x) for x in data]
        return transformed_data

    def create_retraining_dataset(self, dataset_location, new_data, old_dataset):
        """Creates retraining dataset by combining original training data with collected data-points
        - Transforms logged data-points via transformation_func
        - Add annotatons via attached annotation method
        - Combine old training data and newly collected data into retraining dataset file
        """

        new_data = self.transform_collected_data(new_data)
        write_json(dataset_location + "/cleaned_dataset.json", new_data)
        new_data = self.add_annotations(dataset_location + "/cleaned_dataset.json")
        write_json(dataset_location + "/annotated_dataset.json", new_data)
        write_json(
            dataset_location + "/training_dataset.json",
            self.merge_training_datasets(
                old_dataset, dataset_location + "/annotated_dataset.json", ratio=5
            ),
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
