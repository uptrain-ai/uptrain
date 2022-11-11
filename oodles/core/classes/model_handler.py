class ModelHandler:
    """
    Handler class to help with all the model training related functionalities

    ...
    Attributes
    ----------
    training_func : func
        Used to train the model
    inference_func: func
        Used to evaluate the model

    Methods
    -------
    set_training_func(func):
        Attach the model training func
    set_inference_func(func):
        Attach the model evaluation func
    retrain():
        Retrains the model using the provided training dataset. Saves under new version
    compare_new_model(testing_dataset):
        Compares the new model against the old model on the given testing dataset
    """

    def set_training_func(self, func):
        """Attach model training pipeline"""

        self.training_func = func

    def retrain(self, training_file, new_model_version):
        """Calls the training func on the given training_file
        New model is saved under the name: 'version_' + provided new_model_version

        Parameters
        ----------
        training_file : str
            Path to the file used to train the model
        new_model_version : int or str
            New model is saved under the name: 'version_' + provided new_model_version
        """

        self.training_func(training_file, "version_" + str(new_model_version))

    def set_inference_func(self, func):
        """Attach model evaluation pipeline"""

        self.inference_func = func

    def compare_new_model(
        self, testing_dataset, new_model_version, old_training_dataset, selected_count
    ):
        """Compares new model against the old model on testing dataset

        Parameters
        ----------
        testing_dataset : str
            Path to the file used to test the model
        new_model_version : int or str
            Old model is trained and saved under the name: 'version_' + provided new_model_version - 1
        old_training_dataset : str
            Training file for the old model
        selected_count : int
            Number of data-points selected by the framework to add to the retraining dataset
        """

        new_model_name = "version_" + str(new_model_version)
        old_model_name = "version_" + str(new_model_version - 1)

        # Train the old model
        # TODO: No need for this, we can just use the deployed old model
        self.training_func(old_training_dataset, old_model_name)

        # Compute and print accuracies of the old and new model
        old_model_accuracy = self.inference_func(testing_dataset, old_model_name)
        new_model_accuracy = self.inference_func(testing_dataset, new_model_name)

        print("---------------------------------------------")
        print("---------------------------------------------")
        print("Old model accuracy: ", old_model_accuracy)
        print(
            "Retrained model accuracy (ie "
            + str(selected_count)
            + " smartly collected data-points added): ",
            new_model_accuracy,
        )
        print("---------------------------------------------")
        print("---------------------------------------------")
