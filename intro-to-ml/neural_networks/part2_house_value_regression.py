# import torch
import pickle
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelBinarizer
from sklearn.metrics import mean_squared_error
from part1_nn_lib import MultiLayerNetwork, Trainer, Preprocessor
from typing import Optional, cast
from itertools import product

np.seterr(all="ignore")


class Regressor:
    def __init__(
        self,
        x,
        nb_epoch=1000,
        learning_rate=0.01,
        loss_layer="mse",
        batch_size=32,
        network_structure=[8, 16, 1],
        activations=["relu", "relu"],
    ):
        # You can add any input parameters you need
        # Remember to set them with a default value for LabTS tests
        """
        Initialise the model.

        Arguments:
            - x {pd.DataFrame} -- Raw input data of shape
                (batch_size, input_size), used to compute the size
                of the network.
            - nb_epoch {int} -- number of epochs to train the network.

        """

        #######################################################################
        #                       ** START OF YOUR CODE **
        #######################################################################

        # Replace this code with your own
        X, _ = self._preprocessor(x, training=True)
        self.input_size = X.shape[1]
        self.output_size = 1

        self.normaliser_x = None
        self.normaliser_y = None

        self.input_columns = None
        self.input_columns_types = None

        self.model = MultiLayerNetwork(self.input_size, network_structure, activations)
        self.trainer = Trainer(
            self.model,
            batch_size=batch_size,
            nb_epoch=nb_epoch,
            learning_rate=learning_rate,
            loss_fun=loss_layer,
            shuffle_flag=True,
        )

        return

        #######################################################################
        #                       ** END OF YOUR CODE **
        #######################################################################

    def _flatten_categorical_data(self, dataframe):
        current_df = dataframe

        # we need to flatten categorical data (assuming strings are all categorical) into their own columns
        # loop over columns which are potentially strings
        for col in current_df.select_dtypes(include="object"):
            # skip any columns which aren't strings
            if not pd.api.types.is_string_dtype(current_df[col].dtype):
                continue

            # and we can then binarise the data
            lb = LabelBinarizer()
            binarised = lb.fit_transform(current_df[col])
            lb_dataframe = pd.DataFrame(binarised, columns=lb.classes_)
            current_df = pd.concat([current_df, lb_dataframe], axis=1).drop(col, axis=1)

        return current_df

    def _fill_numeric_empty_with_medians(self, dataframe):
        # fill empty values with the median of the column
        curr_df = dataframe.copy()

        # loop over columns with numeric data
        for col in curr_df.select_dtypes(include=["number"]):
            medians = curr_df[col].median()
            curr_df[col].fillna(medians, inplace=True)

        return curr_df

    def _recover_dataframe_from_input_numpy_array(self, input_x: np.ndarray):
        df = pd.DataFrame(input_x, columns=self.input_columns)

        cols = [] if not self.input_columns else self.input_columns
        col_types = [] if not self.input_columns_types else self.input_columns_types

        for col, t in zip(cols, col_types):
            df[col] = df[col].astype(t)

        return df

    def _preprocessor(
        self, x: pd.DataFrame, y: Optional[pd.DataFrame] = None, training=False
    ):
        """
        Preprocess input of the network.

        Arguments:
            - x {pd.DataFrame} -- Raw input array of shape
                (batch_size, input_size).
            - y {pd.DataFrame} -- Raw target array of shape (batch_size, 1).
            - training {boolean} -- Boolean indicating if we are training or
                testing the model.

        Returns:
            - {torch.tensor} or {numpy.ndarray} -- Preprocessed input array of
              size (batch_size, input_size). The input_size does not have to be the same as the input_size for x above.
            - {torch.tensor} or {numpy.ndarray} -- Preprocessed target array of
              size (batch_size, 1).

        """

        #######################################################################
        #                       ** START OF YOUR CODE **
        #######################################################################

        # Replace this code with your own
        # Return preprocessed x and y, return None for y if it was None

        input_x = x
        input_y = y

        median_filled_data = self._fill_numeric_empty_with_medians(input_x)
        flattened_data = self._flatten_categorical_data(median_filled_data)

        self.input_columns = flattened_data.columns
        self.input_columns_types = [
            flattened_data[col].dtype for col in self.input_columns
        ]

        preprocessed_x = flattened_data.to_numpy()
        preprocessed_y = None
        if input_y is not None:
            preprocessed_y = input_y.to_numpy()

        # i.e we can recover the original dataframe from the numpy array since we've saved both column names and datatypes
        # print(flattened_data.equals(self._recover_dataframe_from_input_numpy_array(preprocessed_x)))

        return preprocessed_x, preprocessed_y

        #######################################################################
        #                       ** END OF YOUR CODE **
        #######################################################################

    def fit(self, x: pd.DataFrame, y: pd.DataFrame):
        """
        Regressor training function

        Arguments:
            - x {pd.DataFrame} -- Raw input array of shape
                (batch_size, input_size).
            - y {pd.DataFrame} -- Raw output array of shape (batch_size, 1).

        Returns:
            self {Regressor} -- Trained model.

        """

        #######################################################################
        #                       ** START OF YOUR CODE **
        #######################################################################

        preprocessed_x, preprocessed_y = self._preprocessor(x, y)

        self.normaliser_x = Preprocessor(preprocessed_x)
        self.normaliser_y = Preprocessor(preprocessed_y)

        normalised_x = self.normaliser_x.apply(preprocessed_x)
        normalised_y = self.normaliser_y.apply(preprocessed_y)

        self.trainer.train(normalised_x, cast(np.ndarray, normalised_y))

        #######################################################################
        #                       ** END OF YOUR CODE **
        #######################################################################

    def predict(self, x: pd.DataFrame):
        """
        Output the value corresponding to an input x.

        Arguments:
            x {pd.DataFrame} -- Raw input array of shape
                (batch_size, input_size).

        Returns:
            {np.ndarray} -- Predicted value for the given input (batch_size, 1).

        """

        #######################################################################
        #                       ** START OF YOUR CODE **
        #######################################################################

        # X is the preprocessed input array
        preprocessed_x, _ = self._preprocessor(x, None)
        normalised_x = self.normaliser_x.apply(preprocessed_x)

        output = self.model.forward(normalised_x)
        return self.normaliser_y.revert(output)

        #######################################################################
        #                       ** END OF YOUR CODE **
        #######################################################################

    def score(self, x: pd.DataFrame, y: pd.DataFrame):
        """
        Function to evaluate the model accuracy on a validation dataset.

        Arguments:
            - x {pd.DataFrame} -- Raw input array of shape
                (batch_size, input_size).
            - y {pd.DataFrame} -- Raw output array of shape (batch_size, 1).

        Returns:
            {float} -- Quantification of the efficiency of the model.

        """

        #######################################################################
        #                       ** START OF YOUR CODE **
        #######################################################################

        pred_y = self.predict(x)
        if not np.all(np.isfinite(pred_y)):
            print("Failed to train")
            return np.inf

        rmse = mean_squared_error(y.to_numpy(), pred_y, squared=False)

        return rmse

        #######################################################################
        #                       ** END OF YOUR CODE **
        #######################################################################


def save_regressor(trained_model):
    """
    Utility function to save the trained regressor model in part2_model.pickle.
    """
    # If you alter this, make sure it works in tandem with load_regressor
    with open("part2_model.pickle", "wb") as target:
        pickle.dump(trained_model, target)
    print("\nSaved model in part2_model.pickle\n")


def load_regressor():
    """
    Utility function to load the trained regressor model in part2_model.pickle.
    """
    # If you alter this, make sure it works in tandem with save_regressor
    with open("part2_model.pickle", "rb") as target:
        trained_model = pickle.load(target)
    print("\nLoaded model in part2_model.pickle\n")
    return trained_model


def load_housing_dataset():
    output_label = "median_house_value"

    data = pd.read_csv("housing.csv")

    # Splitting input and output
    x_train: pd.DataFrame = data.drop(output_label, axis=1)
    y_train: pd.DataFrame = data.loc[:, [output_label]]

    return x_train, y_train


def GridSearch(epoch_nums, learning_rates, activation_functions):
    reduced_hyperparameter_search_space = (
        len(epoch_nums) * len(learning_rates) * len(activation_functions)
    )

    print(
        f"Reduced hyperparameter search space size: {reduced_hyperparameter_search_space}"
    )

    # found to perform well through trial and error
    fixed_network_structure = [8, 16, 1]
    fixed_loss_layer = "mse"
    fixed_batch_size = 32

    x_train, y_train = load_housing_dataset()
    best_regressor = None
    best_regressor_score = np.inf

    def MakeRegressor(nb_epoch, lr, activation_functions):
        return Regressor(
            x_train,
            network_structure=fixed_network_structure,
            loss_layer=fixed_loss_layer,
            batch_size=fixed_batch_size,
            nb_epoch=nb_epoch,
            learning_rate=lr,
            activations=activation_functions,
        )

    for epochs, lr, activs in product(epoch_nums, learning_rates, activation_functions):
        r = MakeRegressor(epochs, lr, activs)
        r.fit(x_train, y_train)

        score = r.score(x_train, y_train)
        if score < best_regressor_score:
            best_regressor = r
            best_regressor_score = score
            print(best_regressor_score)

    print(f"Best regressor score found: {best_regressor_score}")
    return best_regressor, best_regressor_score


def get_combo_in_lists(lists, idx):
    result = []
    for l in lists:
        list_idx = idx % len(l)
        result.append(l[list_idx])
        idx //= len(l)
    return result


def RandomisedSearch(
    epoch_nums,
    learning_rates,
    loss_layers,
    batch_sizes,
    network_structures,
    activation_functions,
):
    NUM_SAMPLES = 100

    hyperparameter_space_size = (
        len(epoch_nums)
        * len(learning_rates)
        * len(loss_layers)
        * len(batch_sizes)
        * len(network_structures)
        * len(activation_functions)
    )

    x_train, y_train = load_housing_dataset()
    best_regressor = None
    best_regressor_score = np.inf

    random_idxs = [
        np.random.randint(0, hyperparameter_space_size) for _ in range(NUM_SAMPLES)
    ]

    lists = [
        epoch_nums,
        learning_rates,
        loss_layers,
        batch_sizes,
        network_structures,
        activation_functions,
    ]
    for i in random_idxs:
        combo = get_combo_in_lists(lists, i)
        r = Regressor(x_train, *combo)
        r.fit(x_train, y_train)

        score = r.score(x_train, y_train)
        if score < best_regressor_score:
            best_regressor = r
            best_regressor_score = score
            print(best_regressor_score)

    print(f"Best regressor score found: {best_regressor_score}")
    return best_regressor, best_regressor_score


def RegressorHyperParameterSearch():
    # Ensure to add whatever inputs you deem necessary to this function
    """
    Performs a hyper-parameter for fine-tuning the regressor implemented
    in the Regressor class.

    Arguments:
        Add whatever inputs you need.

    Returns:
        The function should return your optimised hyper-parameters.

    """

    #######################################################################
    #                       ** START OF YOUR CODE **
    #######################################################################

    seed = np.random.randint(0, 2**32 - 1)
    np.random.seed(seed)
    print(f"Seed being used for current run: {seed}")

    MAX_LAYERS = 3
    NODE_INTERVAL_BASE = 2
    NODE_MAX_SCALE = 5
    POSSIBLE_NODE_VALS = [NODE_INTERVAL_BASE**i for i in range(NODE_MAX_SCALE)]

    MAX_EPOCHS_SCALE = 10
    EPOCH_INTERVAL = 10

    INIT_LR = 10**-5
    LR_EXPONENT_BASE = 10
    LR_MAX_SCALE = 6

    BATCH_EXPONENT_BASE = 2
    BATCH_SCALE = 7

    # generate every possible network structure for num_layers layers
    # using POSSIBLE_NODE_VALUES
    def network_structure_gen(num_layers):
        if num_layers == 0:
            return [[]]

        return [
            structure + [n_val]
            for structure in network_structure_gen(num_layers - 1)
            for n_val in POSSIBLE_NODE_VALS
        ]

    epoch_nums = [EPOCH_INTERVAL * i for i in range(MAX_EPOCHS_SCALE)]
    learning_rates = [INIT_LR * (LR_EXPONENT_BASE**i) for i in range(LR_MAX_SCALE)]
    loss_layers = [
        "mse"
    ]  # fixing the loss layer since cross entropy is better suited for classification
    batch_sizes = [BATCH_EXPONENT_BASE**i for i in range(BATCH_SCALE)]
    network_structures = []
    for num_layers in range(MAX_LAYERS):
        # adding 1 for the final output node
        network_structures += [s + [1] for s in network_structure_gen(num_layers + 1)]

    activation_functions = MultiLayerNetwork.ActivationFunctionOptions[:]

    hyperparameter_space_size = (
        len(epoch_nums)
        * len(learning_rates)
        * len(loss_layers)
        * len(batch_sizes)
        * len(network_structures)
        * len(activation_functions)
    )

    print(f"The hyperparameter search space size is: {hyperparameter_space_size}")

    grid_nn, score_grid = GridSearch(epoch_nums, learning_rates, activation_functions)
    random_nn, score_random = RandomisedSearch(
        epoch_nums,
        learning_rates,
        loss_layers,
        batch_sizes,
        network_structures,
        activation_functions,
    )

    print(
        f"Best score using grid search: {score_grid}, best using random search: {score_random}"
    )
    if score_grid < score_random:
        save_regressor(grid_nn)
    else:
        save_regressor(random_nn)

    return  # Return the chosen hyper parameters

    #######################################################################
    #                       ** END OF YOUR CODE **
    #######################################################################


def example_main():
    # setting a predetermined random seed reproducible training
    np.random.seed(10)

    x_train, y_train = load_housing_dataset()

    # Training
    # This example trains on the whole available dataset.
    # You probably want to separate some held-out data
    # to make sure the model isn't overfitting
    regressor = Regressor(x_train, nb_epoch=40)
    regressor.fit(x_train, y_train)
    save_regressor(regressor)

    # Error
    error = regressor.score(x_train, y_train)
    print("\nRegressor error: {}\n".format(error))


if __name__ == "__main__":
    # example_main()
    RegressorHyperParameterSearch()
