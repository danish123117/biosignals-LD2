import requests
import json
def stress_payload(frequency_median_norm, frequency_mean_norm, frequency_meanPower_norm, frequency_zeroCrossing_norm):# this one remains same
    payload_raw = {
        "medianFrequencyState": {
        "type": "Property",
        "value": frequency_median_norm},
        "meanFrequencyState": {
         "type": "Property",
         "value": frequency_mean_norm },
       "meanPowerFrequencyState": {
          "type": "Property",
          "value": frequency_meanPower_norm
        },
        "zeroCrossingFrequencyState": {
          "type": "Property",
          "value": frequency_zeroCrossing_norm
        },
     }
    return json.dumps(payload_raw)

def hr_payload(hr_features: dict, baseline: dict) -> str:
    keys = [
        "meanRR", "meanHR",
        "sdnn", "sdsd", "rmssd",
         "pnn20",
        "lfp", "hfp", "vlf", "lf", "hf",
        "lfhfratio", "totalPower","vlfp"
    ]

    payload_raw = {
        k: {
            "type": "Property",
            "value": hr_features.get(k, 0) - baseline.get(k, 0)
        } for k in keys
    }

    return json.dumps(payload_raw)

def ngsi_get_historical(entity,  mintaka, mintaka_port, context, context_port, attribute, window_length=5000):  # double check on EMG sensor entity what attribute reprements the signal values
    """
    The function queries historical data from TimescaleDB using mintaka API 
    """
    url = f"http://{mintaka}:{mintaka_port}/temporal/entities/{entity}"
    payload ={}
    headers = {
        'NGSILD-Tenant': 'openiot',
        'Link': f'<http://{context}:{context_port}/ngsi-context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"',
        'NGSILD-Path': '/'
    }
    params = {
        'lastN': window_length,
        'attrs': attribute,
        'options': 'temporalValues'
        }
    response = requests.request("GET",url, headers=headers, params=params,data= payload)
   # if response.status_code == 200:
    return response.json()

def ngsi_patch(data,entity,orion,orion_port,context,context_port): # this is fine
    """
    The function update the value on an NGSI-ld entity using patch to orion context broker
    """
    url = f"http://{orion}:{orion_port}/ngsi-ld/v1/entities/{entity}/attrs"
    headers = {
        'Content-Type':"application/json",
        "Link": f'<http://{context}:{context_port}/ngsi-context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"'
     }
    response = requests.request("PATCH", url, headers=headers, data=data)
    return response


def ngsi_get_current(entity, orion,orion_port,context,context_port): # this should be ok
    url = f"http://{orion}:{orion_port}/ngsi-ld/v1/entities/{entity}"

    payload = {}
    headers = {
  'Link': f'<http://{context}:{context_port}/ngsi-context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"',
  'Accept': 'application/json'
}

    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()


def ngsi_get_current_hrv(entity, orion,orion_port,context,context_port): # this should be ok
    url = f"http://{orion}:{orion_port}/ngsi-ld/v1/entities/{entity}?options=keyValues"

    payload = {}
    headers = {
  'Link': f'<http://{context}:{context_port}/ngsi-context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"',
  'Accept': 'application/json'
}

    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()

def ngsi_get_current_canis(entity, canis_major,canis_major_port,context,context_port,wallet_address): # this should be ok
    url = f"http://{canis_major}:{canis_major_port}/ngsi-ld/v1/entities/{entity}?options=keyValues"

    payload = {}
    headers = {
  'Link': f'<http://{context}:{context_port}/ngsi-context-canism-uc2.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"',
  'Accept': 'application/json',
  'Wallet-Type': 'vault',
   'Wallet-Token': 'vault-plaintext-root-token',
   'Wallet-Address': wallet_address,
   'NGSILD-TENANT': 'orion',
   'Content-Type': 'application/json'

}

    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()


def ngsi_patch_canis(data,entity,canis_major,canis_major_port,context,context_port,wallet_address): # this should be ok
    """
    The function update the value on an NGSI-ld entity using patch to canis major context broker
    """
    url = f"http://{canis_major}:{canis_major_port}/ngsi-ld/v1/entities/{entity}/attrs"
    headers = {
        'Content-Type': "application/json",
        "Link": f'<http://{context}:{context_port}/ngsi-context-canism-uc2.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"',
        'Wallet-Type': 'vault',
        'Wallet-Token': 'vault-plaintext-root-token',
        'Wallet-Address': wallet_address,
        'NGSILD-TENANT': 'orion',
        'Accept': 'application/json'
     }
    response = requests.request("POST", url, headers=headers, data=data) # by default it is PAtch is not supported by canis major but will be updated in multiphen 
    return response 

def ngsi_post_canis(data, canis_major, canis_major_port, context, context_port, wallet_address):
    """
    The function creates a new NGSI-ld entity using post to canis major context broker
    """
    url = f"http://{canis_major}:{canis_major_port}/ngsi-ld/v1/entities"
    headers = {
        'Content-Type': "application/ld+json",
        "Link": f'<http://{context}:{context_port}/ngsi-context-canism-uc2.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"',
        'Wallet-Type': 'vault',
        'Wallet-Token': 'vault-plaintext-root-token',
        'Wallet-Address': wallet_address,
        'NGSILD-TENANT': 'orion',
        'Accept': 'application/json'
     }
    response = requests.request("POST", url, headers=headers, data=data)
    return response