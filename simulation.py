import pandas as pd
import numpy as np
import scipy as sc
import donor as don
import recipient as rec
import prediction as pred 
import yaml
from event import Event
from tqdm import tqdm

yaml_file_path = "C:/Users/HP/Desktop/UNOS data/codes/simulation-waitline-unos/mapping_data.yaml"
with open(yaml_file_path, "r") as file:
    loaded_data = yaml.safe_load(file)

# Separate the loaded data back into individual dictionaries
ethcat_mapping = loaded_data["ethcat_mapping"]
blood_type_compatibility = loaded_data["blood_type_compatibility"]
    

def initialize_waitlist(wait_list, next_in_leave_the_list, time_before_starting_simulation, recipients_for_initialization=300):
    for i in range(recipients_for_initialization):
                    new_recipient = rec.Recipient(time_before_starting_simulation) 
                    new_recipient.create_recipient(i)
                    wait_list.append(new_recipient)
                    next_in_leave_the_list.append((new_recipient.time_to_leave_list, new_recipient.reason_to_leave_list, new_recipient.ID))
                    next_in_leave_the_list = sorted(next_in_leave_the_list)
    return next_in_leave_the_list

def create_list_of_events(n_events = 10000, replications=1):
    events_per_replication = {}
    for r in range(replications):
        events = Event(number_of_events= n_events, 
                    time_between_arrivals_recipients=4.2, 
                    time_between_arrivals_donor= 6) #average time in days
        events.create_events(r)
        events_per_replication[r] = events
    return events_per_replication

def get_expected_life(predicted_survival_function): 
    return sum((predicted_survival_function[0].x[i + 1] - predicted_survival_function[0].x[i]) *
    predicted_survival_function[0].y[i] for i in range(len(predicted_survival_function[0].x) - 1))

def get_probability_by_ethinicy(df_waiting_time_no, df_waiting_time_ll, df_waiting_time_fl):
    # Fill missing values with 0 for each DataFrame to ensure all indices are aligned
    df_waiting_time_no.set_index('ethcat', inplace=True)
    df_waiting_time_ll.set_index('ethcat', inplace=True)
    df_waiting_time_fl.set_index('ethcat', inplace=True)

    df_no_filled = df_waiting_time_no['count_mean'].reindex(
        df_waiting_time_no.index.union(df_waiting_time_ll.index).union(df_waiting_time_fl.index), fill_value=0
    )
    df_ll_filled = df_waiting_time_ll['count_mean'].reindex(df_no_filled.index, fill_value=0)
    df_fl_filled = df_waiting_time_fl['count_mean'].reindex(df_no_filled.index, fill_value=0)

    # Perform the calculation
    result = df_no_filled / (df_no_filled + df_ll_filled + df_fl_filled)

    # Add result back to the DataFrame if needed
    df_result = pd.DataFrame({'result': result})
    return df_result

def run_simulation(events_per_replication,  replicates, predictor, policy='p1', T=365.25*30,
                   TARGET_TIME=5*365.25, verbose=False, 
                   time_before_starting_simulation=0):
    
    df = pd.DataFrame(columns=['replicate', 'ethcat', 'gender', 'waiting_time', 'mean_survival_time', 'current_time'])
    df_leaves = pd.DataFrame(columns=['replicate', 'ethcat', 'gender', 'waiting_time', 'mean_survival_time', 'current_time'])
    df_final_list = pd.DataFrame(columns=['replicate', 'ethcat', 'gender', 'waiting_time', 'mean_survival_time', 'current_time'])

    waiting_time_convergence = []
    wait_list_length = []
    leave_list_global = []
    waiting_time_convergence_r = []
    wait_list_length_r = []
    average_waiting_times = []
    number_of_matches_list = []
    released_recipients = []
    
    for r in range(replicates):
        events = events_per_replication[r] 
        print('Replicate #', str(r))
        wait_list = []  # Initialize an empty waitlist for each replicate
        leave_list = []
        next_in_leave_the_list = []
        total_waiting_time = 0  # Track the total waiting time for this replicate
        num_matched_patients = 0  # Track the number of matched patients
        current_t = 0  # Start time    
                    
        next_in_leave_the_list = initialize_waitlist(wait_list, next_in_leave_the_list, time_before_starting_simulation)
        
        with tqdm(total=T, desc=f"Progress replication {r}", unit="time unit") as pbar:
            while current_t < T:                  
                (time_aux, _, _)  = events.list_of_events[0]
                (time2_aux, _, _) = next_in_leave_the_list[0]
                
                if time_aux  < time2_aux:
                    (time, event_type, counter)  = events.list_of_events.pop(0)
                    ID = None
                    pbar.update(time-current_t)
                    if verbose:
                        print(time, event_type, ID)
                else: 
                    (time, event_type, ID) = next_in_leave_the_list.pop(0)
                    if verbose: 
                        print(time, event_type, ID)
                    pbar.update(time-current_t)
                    
                #print(time, event_type)         
                match event_type:
                    case "new_donor":
                        current_t = time
                        donor = don.Donor(current_t)
                        donor.create_donor(counter)
                        
                        if len(wait_list) < 1:
                            raise TypeError('The waitlist length is 0, check the setup please')             
                        
                        match policy: 
                            case "p1":
                                survival_probs = []
                                for recipient in wait_list: 
                                    if donor.blood in blood_type_compatibility[recipient.blood]: 
                                        new_prediction = predictor.predict_survival_prob(recipient, donor, TARGET_TIME)
                                        survival_probs.append(new_prediction)
                                        del new_prediction
                                    else: 
                                        survival_probs.append(0)
                                #print(survival_probs)
                                if verbose: 
                                    print('survival_probs: ', survival_probs)
                                best_match_index = np.argmax(survival_probs)
                                
                            case "p2":                
                                arrival_times = []
                                for recipient in wait_list: 
                                    if donor.blood in blood_type_compatibility[recipient.blood]:
                                        arrival_times.append(recipient.arrival_time)
                                    else: 
                                        arrival_times.append(current_t)
                                if verbose: 
                                    print('arrival_times: ', arrival_times)
                                best_match_index = np.argmin(arrival_times)
                                
                            case "p3":        
                                total_times = []           
                                for recipient in wait_list:
                                    if donor.blood in blood_type_compatibility[recipient.blood]:
                                        _, function_pred = predictor.predict_survival_prob(recipient, donor, TARGET_TIME, surv_function=True)
                                        expected_l = 6*get_expected_life(function_pred)
                                        total_ind = (current_t-recipient.arrival_time) + expected_l
                                        total_times.append(total_ind)
                                    else: 
                                        total_times.append(-1)
                                if verbose: 
                                    print('total_times: ', total_times)
                                best_match_index = np.argmax(total_times)
                            
                        recipient_best = wait_list[best_match_index]
                        
                        _, predicted_survival_function = predictor.predict_survival_prob(recipient_best, donor, 
                                                                                            TARGET_TIME, surv_function=True)
                        
                        mean_survival_time = get_expected_life(predicted_survival_function)
                        #if current_t > 8*365.25:
                        #    print(mean_survival_time, current_t-recipient_best.arrival_time, recipient_best.blood)
                        
                        best_patient = wait_list.pop(best_match_index)
                        
                        next_leave_time = [(a, b, c) for (a, b, c) in next_in_leave_the_list if c==best_patient.ID]
                        
                        _index = next_in_leave_the_list.index(next_leave_time[0])   
                        
                        _ = next_in_leave_the_list.pop(_index)
                        
                        if verbose:
                            print(f'A donation was done with expected life {mean_survival_time}. Day: ', str(current_t))
                        waiting_time = current_t - best_patient.arrival_time
                        
                        if current_t > 8*365.25:
                            total_waiting_time += waiting_time
                            
                        best_patient.waiting_time = waiting_time
                        
                        
                        if current_t > 8*365.25:
                            initial_size = len(df)
                            df.loc[len(df)] = [r, best_patient.ethcat, best_patient.gender, best_patient.waiting_time, mean_survival_time, current_t]
                            released_recipients.append(best_patient)
                            num_matched_patients += 1
                            if initial_size==len(df): 
                                raise ValueError('There is not an increment in the data frame len.')
                    
                    case "new_recipient":            
                        current_t = time
                        new_recipient = rec.Recipient(current_t) 
                        new_recipient.create_recipient(counter)
                        wait_list.append(new_recipient)
                        next_in_leave_the_list.append((new_recipient.time_to_leave_list, new_recipient.reason_to_leave_list, new_recipient.ID))
                        next_in_leave_the_list = sorted(next_in_leave_the_list)
                        
                        if verbose: 
                            print('A new recipient has arrived. Day: ', str(current_t))
                    
                    case "leave_list":
                        current_t = time
                        next_leave_time = [p for p in wait_list if p.ID==ID]
                        _index = wait_list.index(next_leave_time[0])   
                        out_of_list = wait_list.pop(_index)
                        leave_list.append(out_of_list)
                        waiting_time = current_t - out_of_list.arrival_time   
                        out_of_list.waiting_time = waiting_time
                        
                        
                        if current_t > 8*365.25:
                            df_leaves.loc[len(df_leaves)] = [r, out_of_list.ethcat, out_of_list.gender, out_of_list.waiting_time, 0, current_t]
                            if verbose:
                                print('----------------------- One patient left the waitlist. Day: ', str(current_t), out_of_list.ID) 
                if num_matched_patients>0:
                    if current_t > 8*365.25:
                        average_time = total_waiting_time / num_matched_patients
                        #we collect data after 8 years
                        waiting_time_convergence_r.append([current_t, average_time])
                    wait_list_length_r.append([current_t, len(wait_list)])
                else: 
                    average_time = 'INF'
                if verbose:
                    print(f'Number of matches: {num_matched_patients}, recipients in wait list: {len(wait_list)},'
                        f'average time in waitlist {average_time}, patients which leave the list {len(leave_list)}')
            
            for patient in wait_list:
                waiting_time = current_t - patient.arrival_time   
                patient.waiting_time = waiting_time
                df_final_list.loc[len(df_final_list)] = [r, patient.ethcat, patient.gender, patient.waiting_time, 0, current_t] 
                
                    
        if num_matched_patients > 0:
            average_waiting_times.append(total_waiting_time / num_matched_patients)
            waiting_time_convergence.append(waiting_time_convergence_r)
            wait_list_length.append(wait_list_length_r)
            number_of_matches_list.append(num_matched_patients)
            leave_list_global.append(leave_list)
        else:
            average_waiting_times.append(0)
            
    return average_waiting_times, number_of_matches_list, df, df_leaves, df_final_list
