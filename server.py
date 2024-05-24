from flask import Flask , render_template, request
from ngsiOperations.ngsildOperations.ngsildEntityCreator import*
from ngsiOperations.ngsildOperations.ngsildSensorProvision import*
#from ngsiOperations.ngsildOperations.ngsildSubscriptions import createSubscriptions
from AD import*
from CEP import*
from waitress import serve
import threading
import queue
#client = None
#client_queue = queue.Queue()
app = Flask(__name__)

@app.route('/')
@app.route('/index')

def index():
    return render_template('index.html')

@app.route('/setup')

def create_Trial():
    # could add health check as a route to render failure message
    #trial_name = request.args.get("trial name")
    # this could create potential issues in subscriptions
    resp_entities_create  = ngsi_create_trial_UC2()
    #if resp_stress.status_code !=200 or resp_sensor.status_code != 200: 
        #add parameters for response code and messsage related to failure mode 
        # add success message from trial name : Correct
       # return render_template('trial_fail.html')
    
    servicepath_provision_response , sensor_provision_response = sensor_provision_UC2()
    #if servicepath_provision_response.status_code !=200 or sensor_provision_response.status_code != 200: 
        # thete could be other return codes probably better to return something else instead which 
        # circumvents the issue of response codes where the entity/subscription already exists 
        # case for sensor provision 
        #return render_template('trial_fail.html')
    
 #  subscription_sensor_response, subscription_stress_response = createSubscriptions(trial_name) 
    #if subscription_sensor_response.status_code !=200 or subscription_stress_response.status_code != 200: 
        # some parameters for the response codes
        #return render_template('trial_fail.html')
    
    return render_template(
        '2_run_AD.html',
        entity_create_code= resp_entities_create.status_code,
        #entity_create_message=resp_entities_create.text,
        prov_servicepath_status=servicepath_provision_response.status_code ,
        #prov_servicepath_message=servicepath_provision_response.text ,
        prov_sensor_status=sensor_provision_response.status_code,
        #prov_sensor_message =sensor_provision_response.text,
             
                           )
@app.route('/runAD')
def run_AD():
    #anomaly_detector(sensor_entity,stress_entity)
    client_thread_1 = threading.Thread(target=anomaly_detector_thread)
    client_thread_1.start()
# how to do this becauee client wont be returned unless you stop the trial
    return render_template('CEP.html' )
def anomaly_detector_thread():
    anomaly_detector()

@app.route('/runCEP')
def run_CEP():
    client_thread_2 = threading.Thread(target=CEP_UC1_thread, args=("urn:ngsi-ld:EmgFrequencyDomainFeatures:001",))
    client_thread_2.start()
    return render_template('3_stop_trial.html' )
def CEP_UC1_thread(entityStress):
    CEP_UC1(entityStress)

@app.route('/stop')
def stop():
    #stop_trial(client)
    return render_template('index.html')
# something to get data from previus trials this button should be availible on Index 

@app.route('/historypage')
def go_to_history():
    print("this gives me a list of historical")

@app.route('/download')
def download_trial_data():
    print('this downloads the data of a trial')


if __name__ == "__main__":
    serve(app, host= "0.0.0.0", port= 3002)


# change port as environmental variable