import numpy as np 
import pandas as pd 

class Donor:
    def __init__(self, t):
        """
        Initialize the Donor object with relevant attributes.        
        Parameters:
        """
        self.predictors = None
        self.ethcat = None
        self.gender = None
        self.blood = None
        self.arrival_time = t
        self.column_names = [ 'AGE_DON', 'CREAT_TRR', 'HGT_CM_DON_CALC', 'HCV_SEROSTATUS', 'HIST_DIABETES_DON', 
                              'HIST_HYPERTENS_DON', 'AGE_DONge50', 'CREAT_TRRg1.5', 
                              'WGT_KG_DON_CALCl80', 'COD_CAD_DON_2', 'ETHCAT_DON_2']


    def show(self):
        """
        Display the information of the donor.
        """
        print(f"Donor ID: {self.ID}")
        print(f"Predictors: {self.predictors}")
        print(f"ethcat: {self.ethcat}")
        print(f"gender: {self.gender}")
        

        
    def create_donor(self, seed):
        new_donor = pd.read_csv('data/donors.csv').sample(1, random_state=seed)
        self.predictors = new_donor[self.column_names].values[0]
        self.blood = new_donor['ABO_DON'].values[0]
        self.ID = new_donor.index.values[0] 
