import numpy as np

class Event: 
    def __init__(self, number_of_events= 10, 
                 time_between_arrivals_recipients=5, 
                 time_between_arrivals_donor=10):
        self.number_of_events = number_of_events
        self.time_between_arrivals_recipients = time_between_arrivals_recipients
        self.time_between_arrivals_donor = time_between_arrivals_donor
        self.arrivals_recipients = None
        self.arrivals_donors = None
        self.list_of_events = None
        
    def generate_arrivals_recipients(self): 
        self.arrivals_recipients = list(np.random.exponential(scale=self.time_between_arrivals_recipients, 
                                                         size=self.number_of_events))
          
    def generate_arrivals_donors(self): 
        self.arrivals_donors = list(np.random.exponential(scale=self.time_between_arrivals_donor, 
                                                          size=self.number_of_events))
        
    def generate_events(self, r): 
        np.random.seed(r)
        self.generate_arrivals_recipients()
        self.generate_arrivals_donors()
    
    def sort_events(self): 
        event1 = [(time, "new_recipient") for time in self.arrivals_recipients]
        event2 = [(time, "new_donor") for time in self.arrivals_donors]
        all_events = []
        counter = 0
        while len(event1+event2)>0:
            counter = counter + 1
            (t1, next_event1), (t2, next_event2) = event1[0], event2[0]
            
            tmin = np.min([t1, t2])
            
            if tmin == t1:
                all_events.append((t1, next_event1, counter))
                event1.pop(0)
                event2.pop(0)
                
            if tmin == t2: 
                all_events.append((t2, next_event2, counter))
                event2.pop(0)
                event1.pop(0)
        
        #return all_events
        sorted_events = []
        current_t = 0
        for e in all_events:
            (t, event, counter) = e
            current_t = current_t + t
            sorted_events.append((current_t, event, counter))
            
        return sorted_events
    
    def create_events(self, r):
        self.generate_events(r)
        self.list_of_events = self.sort_events()
    