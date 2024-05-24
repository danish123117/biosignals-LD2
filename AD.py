import time
import json
import os
import numpy as np
import ngsiOperations.ngsildOperations.ngsildCrudOperations as v1
import helperFunctions.helperFunctions as hp
import bioTools.emgTools as emg
import bioTools.heartTools as heart


def anomaly_detector():
    '''The looped part has an execution time of ~0.065 seconds'''
    window_length = 30000
    window_length_h = 30
    script_dir = os.path.dirname(os.path.abspath(__file__))
    params_path = os.path.join(script_dir, 'parms.json')
    with open(params_path, 'r') as json_file:
        parms = json.load(json_file)
      
    time.sleep(30)
    while True:
        start_time = time.time()
        data = v1.ngsi_get_historical('urn:ngsi-ld:sEMG:EMG1000',window_length,attribute='data')
        data_h = v1.ngsi_get_historical('urn:ngsi-ld:PolarH10TopicHR:001',window_length_h,attribute='rr')
        #if data ==0:     # case when the there is no data transmission
            # do something when error code is returned probably skip the code   
        #print(data)
        data_arr= hp.data_to_np(data) # convert data from timescaleDB to np array shape (6, window length) this is transposed
        list_rr = hp.rr_array(data_h) 

        filter_data = emg.data_filter(data_arr,sampling_frequency=1000,band_lower=20,band_upper=450) # applies band pass filter shape is still (6,window lenght) check if it works
        median_frequency , mean_frequency, mean_power_frequency, zero_cross_frequency = emg.out_stft(np.transpose(filter_data),sampling_frequency=1000) # extracted features , these should be 3 (1x8) lists 
        s_mean, s_med, s_mpower, s_zcf = emg.stress_out(mean_frequency, median_frequency, mean_power_frequency,zero_cross_frequency, parms) # stress level 
        payload_raw = v1.stress_payload(s_mean.tolist(), s_med.tolist(), s_mpower.tolist(), s_zcf.tolist() ) 
        json_data = json.dumps(payload_raw)
        print(payload_raw)


        heart_parms = heart.timeDomainFeatures(list_rr)
        payload_hr_raw = v1.hr_payload(heart_parms)
        json_data_hr = json.dumps(payload_hr_raw)
        print(payload_hr_raw)

        resp = v1.ngsi_patch(payload_raw,"urn:ngsi-ld:EmgFrequencyDomainFeatures:001")
        print(resp.status_code)
        print(resp.text)

        resp2 = v1.ngsi_patch(payload_hr_raw,"urn:ngsi-ld:HrvFeatures:001")
        print(resp2.status_code)
        print(resp2.text)

        #print(time.time() - start_time)
        if (time.time() - start_time) < 30:
            time.sleep(5- (time.time() - start_time))

if __name__ =="__main__":
    print("Welcome to UC1_AD")
