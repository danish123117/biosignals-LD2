import json 
import requests 
from ngsiOperations.ngsildOperations.ngsildCrudOperations import ngsi_get_current
import time 
import numpy as np 

url = "10.250.3.30"

def mqtt_payload(Rob_state):
    current_time = time.strftime("%Y-%m-%dT%H:%M:%S.", time.localtime()) + '{:03d}'.format(int(round(time.time() * 1000)) % 1000)
    payload = {
        "timeStamp": current_time,
        "automatic": Rob_state
    }
    return payload

def CEP_UC1(entityStress):
    time.sleep(31)
    indices = np.array([0, 1, 4, 5])
    #client = mqtt.Client()
    try:
        while True:
            start_time = time.time()
            Rob_state = False 
            stress_state = ngsi_get_current(entityStress)
            #print(stress_state)
            mean = np.array(stress_state["meanFrequencyState"]['value'])[indices]
            median = np.array(stress_state["medianFrequencyState"]['value'])[indices]
            pow = np.array(stress_state["meanPowerFrequencyState"]['value'])[indices]
            zcf = np.array(stress_state["zeroCrossingFrequencyState"]['value'])[indices]
            cumulative = (pow+ mean) / 2
            Rob_state = not np.any(cumulative > 1)

            hr_state = ngsi_get_current("urn:ngsi-ld:HrvFeatures:001")
#            ml_model = 
#            x = [hr_state['meanRR'],hr_state['meanHR'],hr_state['SDNN'],hr_state['SDSD'],hr_state['RMSSD'],hr_state['pNN50'],hr_state['pNN20']]                
#            prediction = ml_model.predict(x) 
            prediction = 0 

            if Rob_state == False:
                if prediction == 1:
                    Rob_state = True           
            payload = json.dumps(mqtt_payload(Rob_state))
            resp = requests.request("POST",url, headers={}, data=mqtt_payload)
            remaining_time = 30 if not Rob_state else 5*60
            remaining_time = time.time() - start_time
            if remaining_time > 0:
                time.sleep(remaining_time)
    except KeyboardInterrupt:
        print('stopping..')


if __name__ == "__main__": 
    CEP_UC1("Stress:005")




            

