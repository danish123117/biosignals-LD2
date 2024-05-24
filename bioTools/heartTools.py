import numpy as np 
from scipy import signal
from scipy import stats
def timeDomainFeatures(rr_list):
    '''
    Takes a list or rr intervals as input and outputs
    a dictionary of time domain features 
    '''
    hrv_tdf ={}
    rr_list_np = np.array(rr_list) # this results in order of magnitude difference in processing times 
    meanRR = np.mean(rr_list_np) #1
    hrv_tdf['meanRR']
    meanHR = 60000/meanRR #2
    hrv_tdf['meanHR']= meanHR
    SDNN = np.std(rr_list_np, ddof=1)#3 # N-1 in denominator so ddof =1, we treat the readings as a sample
    hrv_tdf['SDNN'] = SDNN
    diffs = np.diff(rr_list_np)
    SDSD = np.std(diffs, ddof=1)
    hrv_tdf['SDSD'] = SDSD
    NN = len(diffs)
    RMSSD = np.sqrt(np.mean(diffs**2))#4
    hrv_tdf['RMSSD']= RMSSD
    NN50 = np.sum(diffs >50)#5
    NN20 = np.sum(diffs >20)#6
    pNN50 =(NN50*100)/(NN-1) #7
    hrv_tdf['pNN50'] = pNN50
    pNN20 = (NN20*100)/(NN-1)#8
    hrv_tdf['pNN20']= pNN20
    
    return hrv_tdf 

def frequencyDomainFeatures(rr_list): 
    return 0 

def nonlinearDomainFeatures(rr_list):
    return 0

def timeDomainLongtermMeasures(rr_list):
    dict_ltd = {}
    rr_list_np = np.array(rr_list)
    #TINN Triangular index # min(20 mins) ideal(24 hr)
    bin_width = 1000/128 # https://doi.org/10.1161/01.CIR.93.5.1043
    hist, bins = np.histogram(rr_list_np, bins=np.arange(min(rr_list_np), max(rr_list_np) + bin_width, bin_width))
    peaks, _ = signal.find_peaks(hist)
    TINN = (len(peaks) - 1) * bin_width if len(peaks) >= 2 else np.nan  
    dict_ltd['TINN'] = TINN
   
    #HRV triangulat index https://doi.org/10.1161/01.CIR.93.5.1043 --> min(20 mins) ideal(24 hr)
    
    HRVti =1  
    dict_ltd['HRVti'] = HRVti

    # Baevsky’s stress index --> add detrending --> How to normalise for sliding windows
    bin_width_si = 50 # https://www.kubios.com/hrv-analysis-methods/#Mifflin1990
    hist, bins = np.histogram(rr_list_np, bins=np.arange(min(rr_list_np), max(rr_list_np) + bin_width_si, bin_width_si))
    modebinindex = np.argmax(hist)
    mode_value = (bin[modebinindex] + bin[modebinindex + 1]) / 2
    AMO = hist[modebinindex]/len(rr_list) # mode bin frequency/length of rr list  
    MxDMn = np.max(rr_list_np) - np.min(rr_list_np)
    SI =AMO/(2*hist[modebinindex]*MxDMn)
    dict_ltd['BaevskyStressIndex'] = SI
    return dict_ltd


