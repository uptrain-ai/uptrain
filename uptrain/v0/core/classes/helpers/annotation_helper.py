from uptrain.v0.core.lib.helper_funcs import read_json


class AnnotationHelper:
    """
    Helper class to integrate different annotation methods

    ...

    Methods
    -------
    annotations_from_master_file(dataset):
        Reads gt from the master_file. Expects matching_key (defaulted to id) and master_file to be present in args
    """

    def __init__(self, args={}):
        self.args = args

    def annotations_from_master_file(self, dataset):
        """Reads gt annotation from a master_file using matching_key as the index
        Expects location of master_file in args
        Defaults matching_key to id if not present in args
        """

        matching_key = self.args.get("matching_key", "id")
        data = read_json(dataset)
        master_data = read_json(self.args["master_file"])
        all_master_keys = [x[matching_key] for x in master_data]
        for datapoint in data:
            datapoint.update(
                {
                    "gt": master_data[all_master_keys.index(datapoint[matching_key])][
                        "gt"
                    ]
                }
            )
        return data
