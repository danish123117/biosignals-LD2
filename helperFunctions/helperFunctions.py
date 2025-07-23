import numpy as np
import json
import ast

def data_to_np(data, key="data"):
    """
    The purpose of this function is to convert single attribute data list values 
    from string dataType to text dataType.
    And then convert it to a transposed np array. This allows for batch processing 
    of multichannel EMG data when extracting features.
    """
    #data2 = json.loads(dataa)
    #print(dataa)
    parsed_data = [np.array(element[0]) for element in data["data"]["values"]]
    #intlist =[ast.literal_eval(string) for string in parsed_data]
   # print(parsed_data)
    numpy_arr  = np.array(parsed_data)
    return numpy_arr

# def rr_array(data_h):
#     appended_list = []
#     appended_list = [item for sublist in data_h["rr"]["values"] for item in sublist[0]]
#     return appended_list
def rr_array(data):
    if isinstance(data, list):
        data = data[0]

    # ---- 4. Extract & flatten rr values -----------------------------------------
    flat_values = []
    for value_entry in data.get("rr", {}).get("values", []):
        raw_val = value_entry[0]        # first element = the numeric (or list) value
        if isinstance(raw_val, list):   # e.g., [438, 1050]
            flat_values.extend(raw_val)
        else:
            flat_values.append(raw_val)
    
    return flat_values


def generate_baseline_emg(data):
    
    baseline ={
    "medianFrequency":{"ch1": data["medianFrequency"][0],"ch2": data["medianFrequency"][1],"ch3": data["medianFrequency"][2],"ch4": data["medianFrequency"][3],"ch5": data["medianFrequency"][4],"ch6": data["medianFrequency"][5]},

    "meanFrequency":{"ch1": data["meanFrequency"][0],"ch2": data["meanFrequency"][1],"ch3": data["meanFrequency"][2],"ch4": data["meanFrequency"][3],"ch5": data["meanFrequency"][4],"ch6": data["meanFrequency"][5]},

    "meanPowerFrequency": {"ch1": data["meanPowerFrequency"][0],"ch2": data["meanPowerFrequency"][1],"ch3": data["meanPowerFrequency"][2],"ch4": data["meanPowerFrequency"][3],"ch5": data["meanPowerFrequency"][4],"ch6": data["meanPowerFrequency"][5]},

    "zeroCrossingFrequency": {"ch1": data["zeroCrossingFrequency"][0],"ch2": data["zeroCrossingFrequency"][1],"ch3": data["zeroCrossingFrequency"][2],"ch4": data["zeroCrossingFrequency"][3],"ch5": data["zeroCrossingFrequency"][4],"ch6": data["zeroCrossingFrequency"][5]}
    }
    return baseline


def generate_baseline_hrv(data):
    baseline = {
        "meanRR": data["meanRR"],
        "meanHR": data["meanHR"],
        "sdnn": data["sdnn"],
        "sdsd": data["sdsd"],
        "rmssd": data["rmssd"],
        "pnn20": data["pnn20"],
        "pnn50": data["pnn50"],
        "TINN": data["TINN"],
        "vlfp": data["vlfp"],
        "lfp": data["lfp"],
        "hfp": data["hfp"],
        "vlf": data["vlf"],
        "lf": data["lf"],
        "hf": data["hf"],
        "lfhfratio": data["lfhfratio"],
        "totalPower": data["totalPower"]
    }
    return baseline