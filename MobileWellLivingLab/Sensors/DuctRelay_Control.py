from Sensors import Sensor
from Storages import SensorStorage
import mWLLUtilities
from datetime import datetime
import time
import threading
import logging
import traceback
import RPi.GPIO as GPIO

class DuctRelay_Control(Sensor.GenericSensor):
    def initialize_sensor(self, config, sensor_id):
        
        super(DuctRelay_Control, self).initialize_sensor(config, sensor_id)
        self.__log.info("Entered initialize_sensor")
        try:
            GPIO.setmode(GPIO.BCM)
            # pin 4 did not work
            # Set Pins that will be used
            pinlist = [2,3,27,17]

            # pin 2 is relay 1
            # pin 3 is relay 2
            # pin 17 is relay 3
            # pin 27 is relay 4

            # Loop and set state to high
            GPIO.setup(pinlist,GPIO.OUT, initial=GPIO.LOW)
            GPIO.output(pinlist,GPIO.HIGH)

            self.__sample_time = float(self.__sensor_config["sampleTime"])
            self.__max_files_upload = int(self.__sensor_config["maxFilesUpload"])

            return True
        except:
            err_msg = traceback.format_exc()
            self.__log.error(err_msg)
            return False

    def push_value_to_store(self, data_payload):
        """
        pushes the data to the storage and further to the cloud
        :param data_payload:
        :return:
        """
        super(DuctRelay_Control, self).push_value_to_store(data_payload)
        self.__storage.push(data_payload)

    def get_last_value(self):
        """
        :return:
        """
        super(DuctRelay_Control, self).get_last_value()
        raise NotImplementedError

    def send_relay_status_to_cloud(self):
    
        #super(DuctRelay_Control, self).send_relay_status_to_cloud()

        timestamp = str(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f') +'Z')

        relay1State = relay2State = relay3State = 0
        relay1State = GPIO.input(2)
        relay2State = GPIO.input(3)
        relay3State = GPIO.input(17)

        print "Relay 1 Status : ", relay1State
        print "Relay 2 Status : ", relay2State
        print "Relay 3 Status : ", relay3State,"\n"
                
        data = (timestamp, {"values": [str(relay1State), str(relay2State), str(relay3State)],
                            "Relay 1 Status ": str(relay1State),
                            "Relay 2 Status ": str(relay2State),
                            "Relay 3 Status ": str(relay3State)})
        
        self.push_value_to_store(data)

    def extract_value(self):
        """
        Set Relays on GPIO and save values with time to Cloud
        :return:
        """
        super(DuctRelay_Control, self).extract_value()
        self.__log.info("Entered extract value, keep_extracting={}".format(self.__keep_extracting))
        while self.__keep_extracting:
            try:
                self.__log.info("Loop Starts")

                #time.sleep(10)
                #time.sleep(5)
                GPIO.output(17,GPIO.LOW)
    
                self.__log.info("Begin Duct Switch: Ball Open / Opening  Pinch Valve")
                self.send_relay_status_to_cloud()
                
                time.sleep(5)
                GPIO.output(2,GPIO.HIGH) 
                GPIO.output(3,GPIO.LOW)
                self.__log.info("Begin Ball Valve Switch: Ball changing/ Pinch open")
                time.sleep(20)
                #time.sleep(5)
                
                
                GPIO.output(17, GPIO.HIGH)
                self.send_relay_status_to_cloud()
                
                self.__log.info("Duct switch complete: Ball Closed / Pinch closed")
                time.sleep(575)
                #time.sleep(5)
                GPIO.output(17, GPIO.LOW)
                self.__log.info("Begin Duct Switch: Ball Open / Opening Pinch")
                self.send_relay_status_to_cloud()

                time.sleep(5);
                GPIO.output(2,GPIO.LOW)
                GPIO.output(3,GPIO.HIGH)
                self.__log.info("Begin Ball Switch: Ball Changing / Pinch Open")
        
                time.sleep(20);
                #time.sleep(5);
                GPIO.output(17, GPIO.HIGH)
                self.send_relay_status_to_cloud()

                self.__log.info("Duct switch complete: Ball Closed / Pinch Closed")
                time.sleep(575);
                #time.sleep(5);
                self.__log.info("End loop")
        
            except:
                err_msg = traceback.format_exc()
                self.__log.error(err_msg)
            #time.sleep(self.__sample_time)
                self.__log.info("Outside the extract value loop, keep_extracting={}".format(self.__keep_extracting))

    def stop_sensor(self):
        """
        Stops a running sensor
        :return: True if the stopping process was succesful, otherwise False
        """
        super(DuctRelay_Control, self).stop_sensor()
        try:
            self.__log.info("Entered stop_sensor, setting the flag to false and waiting")
            self.__keep_extracting = False
            self.__sensor_thread.join(timeout=self.__sample_time + 0.0)
            self.__log.info("Either timeout expired or the thread terminated")
            self.__sensor_thread = None
            return True
        except:
            err_msg = traceback.format_exc()
            self.__log.error(err_msg)
            return False
        finally:
            GPIO.cleanup()

    def start_sensor(self):
        """
        starts the sensor, collects values in a separate thread
        :return: True if the sensor was started without a problem, False otherwise
        """
        super(DuctRelay_Control, self).start_sensor()
        self.__log.info("Entered start_sensor")
        try:
            self.__log.info("Starting sensor thread")
            self.__keep_extracting = False
            if self.__sensor_thread is not None:
                if self.__sensor_thread.isAlive():
                    self.__log.info(
                        "The sensor thread is still running, wait for {}s to stop".format(self.__sample_time))
                    self.__sensor_thread.join(timeout=self.__sample_time + 0.0)
            self.__sensor_thread = None
            self.__keep_extracting = True
            self.__sensor_thread = threading.Thread(target=self.extract_value)
            self.__sensor_thread.start()
            self.__log.info("Thread started")
            return True
        except:
            err_msg = traceback.format_exc()
            self.__log.error(err_msg)
            return False

    def __init__(self, master_config, sensor_config_location, sensor_id):
        """
        Create the Duct Air Quality Control Relay Sensor object
        :param master_config:
        :param sensor_id:
        """
        self.__master_config = master_config
        self.__sensor_id = sensor_id
        self.__sensor_config = mWLLUtilities.read_config(
            self.__master_config["cwd"] + sensor_config_location)
        self.__log = mWLLUtilities.CustomLog(self.__master_config["logger"], self.__sensor_id)
        self.__log.info("Entered {}, setting up storage".format(self.__sensor_id))
        self.__sensor_thread = None
        self.__pin2Val = None
        self.__pin3Val = None
        self.__pin17Val = None
        #self.__sample_time = None
        self.__max_files_upload = None
        self.__keep_extracting = False
        self.__storage = SensorStorage.LowFrequencyStorage(self.__master_config, self.__sensor_config, self.__sensor_id)
        self.__log.info("Initializing sensor")
        success = self.initialize_sensor(self.__master_config, self.__sensor_id)
        if not success:
            raise Exception("Could not initialize the THP sensor! Check log")