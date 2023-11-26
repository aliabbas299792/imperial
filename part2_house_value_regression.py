#import torch
import pickle
import numpy as np
import pandas as pd
import sklearn
from sklearn.preprocessing import LabelBinarizer
from sklearn.metrics import mean_squared_error
from part1_nn_lib import MultiLayerNetwork, Trainer


class Regressor:
    def __init__(self, x, nb_epoch=1000):
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
        self.nb_epoch = nb_epoch

        self.input_columns = None
        self.input_columns_types = None

        neurons = [64, 32, 1]
        activations = ["relu", "relu", "linear"]

        self.model = MultiLayerNetwork(self.input_size, neurons, activations)
        self.trainer = Trainer(self.model,
                                batch_size=32,
                                nb_epoch=self.nb_epoch,
                                learning_rate=0.001,
                                loss_fun="mse",
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

        for col, t in zip(self.input_columns, self.input_columns_types):
            df[col] = df[col].astype(t)

        return df

    def _preprocessor(self, x, y=None, training=False):
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

        IsYADataframe = isinstance(y, pd.DataFrame)

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
        if IsYADataframe:
            preprocessed_y = input_y.to_numpy()

        # i.e we can recover the original dataframe from the numpy array since we've saved both column names and datatypes
        # print(flattened_data.equals(self._recover_dataframe_from_input_numpy_array(preprocessed_x)))

        return preprocessed_x, preprocessed_y

        #######################################################################
        #                       ** END OF YOUR CODE **
        #######################################################################

    def fit(self, x, y):
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

        #I think this uses functions from part 1
        # which layer do we use?
        #for i in range self.nb_epoch: ?
        #input_x = x
        #new_x = layer.forward_pass(input_x)
        #loss = trainer.eval_loss(x,y) not sure if this is right actually
        #alternative way for computing loss:
        #forward_loss = 0
        #for i in range batch_size:
        #    forward_loss += 0.5*(new_x[i] - y[i])*(new_x[i] - y[i])
        
        #grad_loss_wrt_to_inputs = layer.backward_pass(forward_loss) 
        #need to find out what learning_rate is
        #layer.update_params(learning_rate)
        #optional functions and which trainer to use?


        X, Y = self._preprocessor(x, y, True) # Do not forget
        X_np, Y_np = X, Y

        for epoch in range(self.nb_epoch):
            nn_output = self.model.forward(X_np)
            loss = self.trainer._loss_layer.forward(nn_output, Y_np)
            print(f"Loss: {loss}")
            #TODO: Change grad
            grad = nn_output / loss
            nn_grad = self.model.backward(grad)
            self.model.update_params(self.trainer.learning_rate)
        return self

        #######################################################################
        #                       ** END OF YOUR CODE **
        #######################################################################

            
    def predict(self, x):
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

        #X is the preprocessed input array
        X, _ = self._preprocessor(x, None) # Do not forget
        #what do they mean do not forget??
        #regressor = self.fit(X,y)
        #remove pass
        #return predicted value for given input       
        # MSE = 0
        # batch_size,_ = shape(X)
        # for i in range(batch_size):
        #     MSE+= (y[i] - y_hat[i])*(y[i] - y_hat[i])
        # MSE = MSE * (1/batch_size)
        # #cross-entropy
        # #define C
        # L = 0
        # for i in range(batch_size):
        #     for c range(C):

        return self.model.forward(X)

        #######################################################################
        #                       ** END OF YOUR CODE **
        #######################################################################

    def score(self, x, y):
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

        X, Y = self._preprocessor(x, y = y, training = False) # Do not forget
        pred_y = self.predict(X)
        rmse = mean_squared_error(y.to_numpy(),pred_y, squared=False)
        
        return rmse

        #######################################################################
        #                       ** END OF YOUR CODE **
        #######################################################################


def save_regressor(trained_model): 
    """ 
    Utility function to save the trained regressor model in part2_model.pickle.
    """
    # If you alter this, make sure it works in tandem with load_regressor
    with open('part2_model.pickle', 'wb') as target:
        pickle.dump(trained_model, target)
    print("\nSaved model in part2_model.pickle\n")


def load_regressor(): 
    """ 
    Utility function to load the trained regressor model in part2_model.pickle.
    """
    # If you alter this, make sure it works in tandem with save_regressor
    with open('part2_model.pickle', 'rb') as target:
        trained_model = pickle.load(target)
    print("\nLoaded model in part2_model.pickle\n")
    return trained_model



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

    return  # Return the chosen hyper parameters

    #######################################################################
    #                       ** END OF YOUR CODE **
    #######################################################################



def example_main():

    output_label = "median_house_value"

    # Use pandas to read CSV data as it contains various object types
    # Feel free to use another CSV reader tool
    # But remember that LabTS tests take Pandas DataFrame as inputs
    data = pd.read_csv("housing.csv") 

    # Splitting input and output
    x_train = data.loc[:, data.columns != output_label]
    y_train = data.loc[:, [output_label]]

    # Training
    # This example trains on the whole available dataset. 
    # You probably want to separate some held-out data 
    # to make sure the model isn't overfitting
    regressor = Regressor(x_train, nb_epoch = 10)
    regressor.fit(x_train, y_train)
    save_regressor(regressor)

    # Error
    error = regressor.score(x_train, y_train)
    print("\nRegressor error: {}\n".format(error))


if __name__ == "__main__":
    example_main()

