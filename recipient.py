
import numpy as np 
import pandas as pd 

class Recipient:
    def __init__(self, t, time_to_sick_to_transplant= 365*10):
        """
        Initialize the Donor object with relevant attributes.        
        Parameters:
        """
        self.predictors = None
        self.ethcat = None
        self.gender = None
        self.blood = None
        self.arrival_time = t
        self.column_names = [ 'DIALYSIS_DATE', 'AGE', 'DIAB', 'DIALYSIS_DATEle0.0']
        self.waiting_time = None
        self.time_to_leave_list = None
        self.reason_to_leave_list = None
        self.time_to_sick_to_transplant = time_to_sick_to_transplant
        
    def show(self):
        """
        Display the information of the recipient.
        """
        print(f"Recipient ID: {self.ID}")
        print(f"Predictors: {self.predictors}")
        print(f"ethcat: {self.ethcat}")
        print(f"gender: {self.gender}")
        
        
    def create_recipient(self, seed):
        np.random.seed(seed)
        new_recipient = pd.read_csv('data/recipients.csv').sample(1, random_state=seed)
        self.predictors = new_recipient[self.column_names].values[0]
        self.ethcat = new_recipient[ 'ETHCAT'].values[0]
        self.gender = new_recipient['GENDER'].values[0]
        self.blood = new_recipient['ABO'].values[0]
        #_time_to_leave = #np.min([np.random.lognormal(mean=self.time_to_sick_to_transplant, 
                         #                            sigma=(1)*365, size=1)[0], 365.25*5])
        _time_to_leave = np.random.exponential(scale=self.time_to_sick_to_transplant, size=1)[0]           
        #exponenential 
        self.time_to_leave_list = self.arrival_time + _time_to_leave
        self.reason_to_leave_list = "leave_list"
        self.ID = new_recipient.index.values[0] 
        

        