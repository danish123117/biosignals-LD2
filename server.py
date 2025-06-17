from flask import Flask , render_template, request, jsonify
from ngsiOperations.ngsildOperations.ngsildEntityCreator import*
from ngsiOperations.ngsildOperations.ngsildSensorProvision import*
#from ngsiOperations.ngsildOperations.ngsildSubscriptions import createSubscriptions
from AD import*
from CEP import*
from waitress import serve
import threading
import queue
import os
import ngsiOperations.ngsildOperations.ngsildCrudOperations as v1
import helperFunctions.helperFunctions as hp
import bioTools.emgTools as emg
import bioTools.heartTools as heart
import requests
import json
import paho.mqtt.client as mqtt
import time
import numpy as np
#client = None
#client_queue = queue.Queue()

IOTA_NAME= os.getenv("IOTA_CONTAINER_NAME","localhost")
IOTA_PORT = os.getenv("IOTA_CONTAINER_PORT","4041")
ORION_NAME = os.getenv("ORION_NAME","localhost")
ORION_PORT = os.getenv("ORION_PORT","1026")
MINTAKA_NAME= os.getenv("MINTAKA_NAME","localhost")
MINTAKA_PORT= os.getenv("MINTAKA_PORT","8080")
CONTEXT_NAME = os.getenv("CONTEXT_CONTAINER_NAME","context")
CONTEXT_PORT = os.getenv("CONTEXT_PORT","5051")
BROKER_IP = os.getenv("MOSQUITTO_CONTAINER_NAME","localhost")
BROKER_PORT = os.getenv("MOSQUITTO_CONTAINER_PORT",1883)
TOPIC = os.getenv("TOPIC","json/danishabbas1/Robotstate")
ENTITY_FATIGUE = os.getenv("ENTITY_FATIGUE","urn:ngsi-ld:EmgFrequencyDomainFeatures:002")
ARKITE_URL = os.getenv("ARKITE_URL","http://10.250.3.30")
#ARKITE_URL = os.getenv("ARKITE_URL","http://localhost:2001/test")

app = Flask(__name__)


def mqtt_payload(Rob_state):
    current_time = time.strftime("%Y-%m-%dT%H:%M:%S.", time.localtime()) + '{:03d}'.format(int(round(time.time() * 1000)) % 1000)
    payload = {
        "timeStamp": current_time,
        "automatic": Rob_state
    }
    return payload

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
    else:
        print(f"Connection failed with code {rc}")

def on_disconnect(client, userdata, rc):
    print("Disconnected from MQTT broker")




@app.route('/')
@app.route('/index')

def index():
    return render_template('index.html')

@app.route('/setup', methods=['GET', 'POST', 'PATCH'])

def create_Trial():
    trial_name = request.args.get("trial_name")
    orion = ORION_NAME
    orion_port = ORION_PORT
    context = CONTEXT_NAME
    context_port = CONTEXT_PORT
    resp_entities_patch  = ngsi_start_trial_UC2(trial_name,orion,orion_port,context,context_port=context_port)
    
    if resp_entities_patch.status_code==201:
        entity_status ="OK!"
    else: 
        entity_status = "Failed!"
    
    return render_template(
        '2_run_AD.html',
        entity_create_code= entity_status)

             

@app.route('/setup_0', methods=['GET', 'POST'])
def day_0():
    iota_container_name= IOTA_NAME
    iota_container_port = IOTA_PORT
    orion = ORION_NAME
    orion_port = ORION_PORT
    context = CONTEXT_NAME
    context_port = CONTEXT_PORT
    resp_entities_create  = ngsi_create_trial_UC2(orion,orion_port,context,context_port=context_port)
    
    if resp_entities_create.status_code==201:
        entity_status ="OK!"
    else: 
        entity_status = "Failed!"

    servicepath_provision_response , sensor_provision_response = sensor_provision_UC2(iota_container_name,iota_container_port,orion, orion_port) ##
    
    if servicepath_provision_response.status_code==201:
        servicepath_status ="OK!"
    else: 
        servicepath_status = "Failed!"
    
    if sensor_provision_response.status_code==201:
        sensor_provision_status ="OK!"
    else: 
        sensor_provision_status = "Failed!"
    
    return jsonify({
        'entity_create_code': entity_status,
        'prov_servicepath_status': servicepath_status,
        'prov_sensor_status': sensor_provision_status
    })

@app.route("/processEMG", methods=['POST', 'GET'])
def anomaly_detector():
    '''The looped part has an execution time of ~0.065 seconds'''
    window_length = 5000
    window_length_h = 180
    script_dir = os.path.dirname(os.path.abspath(__file__))
    params_path = os.path.join(script_dir, 'parms.json')
    params_path_h = os.path.join(script_dir, 'ecgbase.json')

    with open(params_path, 'r') as json_file:
        parms = json.load(json_file)
    with open(params_path_h, 'r') as json_file_h:
        parms_h = json.load(json_file_h)
      # add context/ context port here
    data = v1.ngsi_get_historical(entity='urn:ngsi-ld:sEMG:EMG1001',window_length=window_length,mintaka=MINTAKA_NAME,mintaka_port=MINTAKA_PORT,context=CONTEXT_NAME,context_port=CONTEXT_PORT,attribute='data')
    data_h = v1.ngsi_get_historical('urn:ngsi-ld:PolarH10TopicHR:001',window_length=window_length_h,attribute='rr',mintaka=MINTAKA_NAME,mintaka_port=MINTAKA_PORT,context=CONTEXT_NAME,context_port=CONTEXT_PORT)
    if data:
        data_arr= hp.data_to_np(data) # convert data from timescaleDB to np array shape (6, window length) this is transposed
        #print(data_h)
        list_rr = hp.rr_array(data_h)
        
        filter_data = emg.data_filter(data_arr,sampling_frequency=1000,band_lower=20,band_upper=450) # applies band pass filter shape is still (6,window lenght) check if it works
        median_frequency , mean_frequency, mean_power_frequency, zero_cross_frequency = emg.out_stft(np.transpose(filter_data),sampling_frequency=1000) # extracted features , these should be 3 (1x6) lists 
        s_mean, s_med, s_mpower, s_zcf = emg.stress_out(mean_frequency, median_frequency, mean_power_frequency,zero_cross_frequency, parms) # stress level 
        #print(s_mean, s_med, s_mpower, s_zcf)
        payload_raw = v1.stress_payload(s_mean.tolist(), s_med.tolist(), s_mpower.tolist(), s_zcf.tolist() )    
        json_data = json.dumps(payload_raw)

        #print(payload_raw)
        #print(list_rr)

        heart_parms_t = heart.timeDomainFeatures(list_rr)
        heart_parms_f = heart.frequencyDomainFeatures(list_rr)
        heart_parms = {**heart_parms_t, **heart_parms_f}  # Combine time and frequency domain features
        payload_hr_raw = v1.hr_payload(heart_parms, parms_h) # this is the payload for HRV features
        json_data_hr = json.dumps(payload_hr_raw)
        #print(payload_hr_raw)

     
        resp = v1.ngsi_patch(data=payload_raw,entity="urn:ngsi-ld:EmgFrequencyDomainFeatures:002", orion=ORION_NAME,orion_port=ORION_PORT,context=CONTEXT_NAME,context_port=CONTEXT_PORT)

        resp2 = v1.ngsi_patch(data=payload_hr_raw,entity="urn:ngsi-ld:HrvFeatures:001", orion=ORION_NAME,orion_port=ORION_PORT,context=CONTEXT_NAME,context_port=CONTEXT_PORT)
        #print(resp.status_code)
        if resp2.status_code == 204 and resp.status_code == 204:
            return jsonify({"status": "OK"})
        else:
            return jsonify({"status": "Failed"})
    else:
        return jsonify({"status": "No data available"}) 

@app.route('/get_emg_data', methods=['GET'])
def get_emg_data(orion=ORION_NAME, orion_port=ORION_PORT, context=CONTEXT_NAME, context_port=CONTEXT_PORT):
    entity_id = "urn:ngsi-ld:sEMG:EMG1001"
    url = f"http://{orion}:{orion_port}/ngsi-ld/v1/entities/{entity_id}"
    payload = {}
    headers = {
  'Link': f'<http://{context}:{context_port}/ngsi-context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"',
  'Fiware-service': 'openiot',
  'servicepath': '/'
    }
    try:
        response = requests.get(url, headers=headers, data=payload)
        response.raise_for_status()
        entity_data = response.json()
        data_values = entity_data.get('data', {}).get('value', ["---"] * 6)  # Default to "---" if unavailable
    except Exception:
        data_values = ["---"] * 6  

    return jsonify({"data": data_values})

@app.route('/get_hr_data', methods=['GET'])
def get_hr_data(orion=ORION_NAME, orion_port=ORION_PORT, context=CONTEXT_NAME, context_port=CONTEXT_PORT):
    entity_id = "urn:ngsi-ld:PolarH10TopicHR:001"
    url = f"http://{orion}:{orion_port}/ngsi-ld/v1/entities/{entity_id}"
    headers = {
        'Link': f'<http://{context}:{context_port}/ngsi-context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"',
        'Fiware-service': 'openiot',
        'servicepath': '/'
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        entity = response.json()
        
        # Handle HR data
        hr_value = entity.get('hr', {}).get('value', 0)
        
        # Handle RR data (can be single value or array)
        rr_raw = entity.get('rr', {}).get('value', [])
        if isinstance(rr_raw, list):
            # Get first RR value if array, or 0 if empty
            rr_value = rr_raw[0] if rr_raw else 0
        else:
            # If RR is single value
            rr_value = rr_raw or 0
        
        return jsonify({
            'status': 'OK',
            'hr_value': hr_value,
            'rr_value': rr_value
        })

    except requests.exceptions.RequestException as e:
        print(f"Error fetching HR data: {str(e)}")
        return jsonify({
            'status': 'Error',
            'error': str(e),
            'hr_value': 0,
            'rr_value': 0
        }), 500


@app.route("/send_robot_state", methods=["GET", "POST"])
def send_robot_state():
    entityStress = ENTITY_FATIGUE
    orion = ORION_NAME
    orion_port = ORION_PORT
    broker_address = BROKER_IP
    broker_port = int(BROKER_PORT)
    topic = TOPIC

    try:
        indices = np.array([0, 1, 4, 5])
        Rob_state = False

        stress_state = ngsi_get_current(entity=entityStress, orion=orion, orion_port=orion_port, context=CONTEXT_NAME, context_port=CONTEXT_PORT)

        mean = np.array(stress_state["meanFrequencyState"]['value'])[indices]
        median = np.array(stress_state["medianFrequencyState"]['value'])[indices]
        pow = np.array(stress_state["meanPowerFrequencyState"]['value'])[indices]
        zcf = np.array(stress_state["zeroCrossingFrequencyState"]['value'])[indices]
        cumulative = (pow + mean) / 2

        Rob_state = not np.any(cumulative > 1)
        print(f"Robot state: {Rob_state}")
        payload = json.dumps(mqtt_payload(Rob_state))

        resp = requests.request("POST",ARKITE_URL,  headers={}, data=payload)
        print(f"Response from MQTT broker: {resp.status_code}")
        return jsonify({"status": "MQTT message sent", "robot_state": Rob_state})
    except Exception as e:
        return jsonify({"status": "Error", "error": str(e)})



@app.route('/stopTrial', methods=['GET', 'POST'])
def stop_trial():
    response = ngsi_stop_trial_UC2(orion=ORION_NAME, orion_port=ORION_PORT, context=CONTEXT_NAME, context_port=CONTEXT_PORT)
    if response.status_code == 204:
        return jsonify({"status": "Trial stopped successfully"})
    else:
        return jsonify({"status": "Failed to stop trial", "error": response.text}), response.status_code
##########old code#####

                           
# def run_AD():
#     #anomaly_detector(sensor_entity,stress_entity)
#     client_thread_1 = threading.Thread(target=anomaly_detector_thread)
#     client_thread_1.start()
# # how to do this becauee client wont be returned unless you stop the trial
#     return render_template('CEP.html' )
# def anomaly_detector_thread():
#     anomaly_detector()

# @app.route('/runCEP')
# def run_CEP():
#     client_thread_2 = threading.Thread(target=CEP_UC1_thread, args=("urn:ngsi-ld:EmgFrequencyDomainFeatures:001",))
#     client_thread_2.start()
#     return render_template('3_stop_trial.html' )
# def CEP_UC1_thread(entityStress):
#     CEP_UC1(entityStress)

# @app.route('/stop')
# def stop():
#     #stop_trial(client)
#     return render_template('index.html')
# # something to get data from previus trials this button should be availible on Index 

# @app.route('/historypage')
# def go_to_history():
#     print("this gives me a list of historical")

# @app.route('/download')
# def download_trial_data():
#     print('this downloads the data of a trial')


if __name__ == "__main__":
    serve(app, host= "0.0.0.0", port= 3002)


# change port as environmental variable