import pandas as pd



def get_summary_tables(df, ethcat_mapping, real_ethcat_df, real_gender_df):
    df['ethcat'] = df['ethcat'].replace(ethcat_mapping)
    df_waiting_time = ((df.groupby(by=['replicate', 'ethcat'])
                    .agg(
                        waiting_time=('waiting_time', 'mean'), 
                        count=('waiting_time', 'size'), 
                        mean_survival_time=('mean_survival_time', 'mean'))
                    .reset_index())
    )#.to_csv('simulation_results.csv')
    df_waiting_time = df_waiting_time[['ethcat', 'waiting_time', 'count', 'mean_survival_time']].groupby('ethcat').agg(['mean', 'std'])
    df_waiting_time.columns = [f"{col[0]}_{col[1]}" for col in df_waiting_time.columns] 
    df_waiting_time['prop_simu'] = df_waiting_time['count_mean'] / df_waiting_time['count_mean'].sum()
    df_waiting_time = df_waiting_time.merge(real_ethcat_df, on='ethcat').round(3)
    df_waiting_time.columns = ['ethcat', 'wt_mean', 'wt_std', 'count_mean', 'count_std', 'st_mean', 'st_std', 'prop_simu', 'sample_proportion']

    df_gender = ((df.groupby(by=['replicate', 'gender'])
                    .agg(
                        waiting_time=('waiting_time', 'mean'), 
                        count=('waiting_time', 'size'),
                        mean_survival_time=('mean_survival_time', 'mean'))
                    .reset_index())
    )#.to_csv('simulation_results.csv')
    df_gender = df_gender[['gender', 'waiting_time', 'count', 'mean_survival_time']].groupby('gender').agg(['mean', 'std'])
    df_gender.columns = [f"{col[0]}_{col[1]}" for col in df_gender.columns] 
    df_gender['proportion_sim'] = df_gender['count_mean'] / df_gender['count_mean'].sum()
    df_gender.reset_index(inplace=True)
    df_gender = df_gender.merge(real_gender_df, on = 'gender')
    df_gender.columns = ['gender', 'wt_mean', 'wt_std', 'count_mean',
        'count_std', 'st_mean', 'st_std',
        'prop_sim', 'sample_proportion']
    return df_waiting_time, df_gender

def load_data():
    df_base = pd.read_csv('data/data_to_simulate.csv', index_col=0)
    df_base.dropna(inplace=True)
    #print(df_base.columns)
    #columns = ['GTIME_KI', 'GSTATUS_KI', 'AGE_DON', 'HCV_SEROSTATUS', 'GENDER_DON', 'AGE', 'DIAB',
    #                'BMI_CALC', 'ETHCAT', 'GENDER', 'COLD_ISCH_KI', 'SERUM_CREAT',
    #                'CREAT_TRR', 'delta_age', 'HIST_DIABETES_DON', 'HGT_CM_DON_CALC','CREAT_TRRg1.5', 'SERUM_CREATg1.2',
    #                'COD_CAD_DON', 'WGT_KG_DON_CALC', 'CREAT_DON', 'ETHCAT_DON',
    #                'HIST_HYPERTENS_DON', 'NON_HRT_DON', 'DIALYSIS_DATE','TX_DATE', 'PT_CODE', 'ABO', 'ABO_DON']

    #predictors = ['AGE_DON', 'CREAT_TRR', 'HGT_CM_DON_CALC', 'HCV_SEROSTATUS', 'WGT_KG_DON_CALC',
    #                    'HIST_DIABETES_DON', 'HIST_HYPERTENS_DON', 'COD_CAD_DON', 'ETHCAT_DON', 'ABO_MAT', 
    #                    'HLAMIS', 'DIALYSIS_DATE', 'AGE', 'DIAB', 'DIALYSIS_DATEle0.0', 'CREAT_TRRg1.5', 'SERUM_CREATg1.2']

    donor = df_base[['AGE_DON', 'CREAT_TRR', 'CREAT_TRRg1.5', 'HGT_CM_DON_CALC', 'HCV_SEROSTATUS', 'HIST_DIABETES_DON', 
                'HIST_HYPERTENS_DON', 'ABO_DON', 'AGE_DONge50', 'WGT_KG_DON_CALCl80', 'COD_CAD_DON_2', 'ETHCAT_DON_2']]
    #print(donor.columns)
    donor.to_csv('data/donors.csv')
    recipient = df_base[[ 'DIALYSIS_DATE', 'AGE', 'DIAB', 'ETHCAT', 'GENDER', 'ABO', 'DIALYSIS_DATEle0.0']]
    recipient.to_csv('data/recipients.csv')
    return df_base
