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

def rr_array(data_h):
    appended_list = []
    appended_list = [item for sublist in data_h["rr"]["values"] for item in sublist[0]]
    return appended_list
