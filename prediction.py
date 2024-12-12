import pandas as pd
from sksurv.util import Surv
from sksurv.ensemble import RandomSurvivalForest
from sksurv.tree import SurvivalTree
import pickle 
import numpy as np

class SurvivalPredictionModel:
    def __init__(self, model_path=None):
        """
        Initialize the SurvivalPredictionModel.
        :param model_path: Path to the pre-trained model file (optional).
        """
        self.model = None
        if model_path:
            self.load_model(model_path)

    def load_model(self, model_path):
        """
        Load a pre-trained model from a file.
        :param model_path: Path to the model file.
        """
        try:
            with open(model_path, 'rb') as file:
                print(model_path)
                self.model = pickle.load(file)
            print(f"Model loaded successfully from {model_path}.")
        except Exception as e:
            print(f"Error loading model: {e}")

    def predict_survival_prob(self, patient, donor, target_time, verbose=True, surv_function=False):
        """
        Predict survival probability based on patient and donor compatibility.
        :param patient: Patient data (e.g., features or characteristics).
        :param donor: Donor data (e.g., features or characteristics).
        :return: Survival probability (float).
        """
        if self.model:
            # If a model is loaded, use it to make predictions
            input_features = np.concatenate((donor.predictors, patient.predictors)).reshape(1, -1)
            input_features_df = pd.DataFrame(input_features, columns=self.model.feature_names_in_)

            surv_prob = self.model.predict_survival_function(input_features_df)
            
            if verbose:
                print("Combined input features:", input_features)
                print(input_features)
                print('Type:', type(surv_prob))
                print('Time points:', surv_prob[0].x)
                print('Survival probabilities:', surv_prob[0].y)

            # Find the closest time to 5 years in `surv_prob[0].x`
            closest_index = np.abs(surv_prob[0].x - target_time).argmin()
            closest_time = surv_prob[0].x[closest_index]
            survival_prob_5_years = surv_prob[0].y[closest_index]
            if verbose:
                print(f'Surv prob: {survival_prob_5_years}  at {closest_time}')
            
            if surv_function:
                return survival_prob_5_years, surv_prob
            else:
                return  survival_prob_5_years # Assuming the model provides probabilities
        else:
           raise TypeError('There is not a loaded model.')