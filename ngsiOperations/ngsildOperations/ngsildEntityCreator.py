import requests
import json
def ngsi_create_entity(d):#updates latest values
    url = 'http://orion:1026/ngsi-ld/v1/entityOperations/create'
    #url = 'http://localhost:1026/ngsi-ld/v1/entityOperations/create'
    headers = {
  'Content-Type': 'application/json',
  'Link': '<http://context:5051/ngsi-context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json", "Accept": "application/ld+json"'
    }

    response = requests.request("POST", url, headers=headers, data=d)
    return response
 
def ngsi_create_trial_UC2():
    d_hrp = {
    "id": "urn:ngsi-ld:HrvFeatures:001",
    "type": "HrvFeatures",
    "meanRR": {
      "type": "Property",
      "value": 0
      },
    "meanHR": {
      "type": "Property",
      "value": 0
      },
    "SDNN":{
      "type":"Property",
      "value":0
      },
    "SDSD":{
      "type":"Property",
      "value":0
      },
    "RMSSD":{
      "type":"Property",
      "value":0
      },
    "pNN50":{
      "type":"Property",
      "value":0
      },
    "pNN20":{
      "type":"Property",
      "value":0
      }
    }
    d_stress = {
    "id": "urn:ngsi-ld:EmgFrequencyDomainFeatures:001",
    "type": "EmgFrequencyDomainFeatures",
    "medianFrequencyState": {
      "type": "Property",
      "value": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]},
    "meanFrequencyState": {
      "type": "Property",
      "value": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] },
    "meanPowerFrequencyState": {
      "type": "Property",
      "value": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]},
    "zeroCrossingFrequencyState": {
      "type": "Property",
      "value": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]}
     }  
    d_emg = {
    "id": "urn:ngsi-ld:sEMG:EMG1000",
    "type": "sEMG",
    "timeStamp": {
      "type": "Property",
      "value": "132"
    },
    "index": {
      "type": "Property",
      "value": 0
    },
    "data":{
      "type":"Property",
      "value":[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
              },
    "feaisability":{
      "type":"Property",
      "value":[True,True,True,True,True,True,True,True]}
    }
    ar = 73*[0]
    d_ecg = {
    "id": "urn:ngsi-ld:PolarH10TopicECG:001",
    "type": "PolarH10TopicECG",
    "clientId": {
      "type": "Property",
      "value": "AA3_UC2"
      },
    "deviceId": {
      "type": "Property",
      "value": "0000"
      },
    "sessionId":{
      "type":"Property",
      "value":0
      },
    "timeStamp":{
      "type":"Property",
      "value":0
      },
    "sampleRate":{
      "type":"Property",
      "value":130
      },
    "sensorTimeStamp":{
      "type":"Property",
      "value":0
      },
    "ecg":{
      "type":"Property",
      "value":ar
      }
    }

    d_hr = {
    "id": "urn:ngsi-ld:PolarH10TopicHR:001",
    "type": "PolarH10TopicHR",
    "clientId": {
      "type": "Property",
      "value": "AA3_UC2"
      },
    "deviceId": {
      "type": "Property",
      "value": "0000"
      },
    "sessionId":{
      "type":"Property",
      "value":0
      },
    "timeStamp":{
      "type":"Property",
      "value":0
      },
    "sensorTimeStamp":{
      "type":"Property",
      "value":0
      },
    "hr":{
      "type":"Property",
      "value":0
      },
    "hrv":{
      "type":"Property",
      "value":0
      },
    "rr":{
      "type":"Property",
      "value":[0]
      }
    }
    ac = [[0,0,0]]*36
    d_acc = {
    "id": "urn:ngsi-ld:PolarH10TopicACC:001",
    "type": "PolarH10TopicACC",
    "clientId": {
      "type": "Property",
      "value": "AA3_UC2"
      },
    "deviceId": {
      "type": "Property",
      "value": "0000"
      },
    "sessionId":{
      "type":"Property",
      "value":0
      },
    "timeStamp":{
      "type":"Property",
      "value":0
      },
    "sampleRate":{
      "type":"Property",
      "value":25
      },
    "sensorTimeStamp":{
      "type":"Property",
      "value":0
      },
    "acc":{
      "type":"Property",
      "value":ac
      }
    }
    payload = json.dumps([d_stress,d_emg,d_acc,d_ecg,d_hr,d_hrp])
    resp= ngsi_create_entity(payload)
    return resp

def ngsi_create_trial_UC1():
    d_stress = {
    "id": "urn:ngsi-ld:EmgFrequencyDomainFeatures:001",
    "type": "EmgFrequencyDomainFeatures",
    "medianFrequencyState": {
      "type": "Property",
      "value": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]},
    "meanFrequencyState": {
      "type": "Property",
      "value": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] },
    "meanPowerFrequencyState": {
      "type": "Property",
      "value": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]},
    "zeroCrossingFrequencyState": {
      "type": "Property",
      "value": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]}
     }  
    d_emg = {
    "id": "urn:ngsi-ld:sEMG:EMG1000",
    "type": "sEMG",
    "timeStamp": {
      "type": "Property",
      "value": "132"
    },
    "index": {
      "type": "Property",
      "value": 0
    },
    "data":{
      "type":"Property",
      "value":[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
              },
    "feaisability":{
      "type":"Property",
      "value":[True,True,True,True,True,True,True,True]}
    }
    payload = json.dumps([d_stress,d_emg])

    resp= ngsi_create_entity(payload)
    return resp

#Done