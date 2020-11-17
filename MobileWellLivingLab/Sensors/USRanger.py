from Sensors import Sensor
from Storages import SensorStorage
"""
from Storages.SensorStorage import LowFrequencyStorage
"""
from datetime import datetime
import mWLLUtilities
import serial
import time
import traceback
import threading
import logging
import serial
import struct
import grovepi



class GroveUSRanger(Sensor.GenericSensor):
    def initialize_sensor(self, config, sensor_id):
        """
        Inititalize the I2C sensor object and setup the sample time
        :param config:
        :param sensor_id:
        :return:
        """
        super(GroveUSRanger, self).initialize_sensor(config, sensor_id)
        self.__log.info("Entered initialize_sensor")
        try:
            #ultrasonic_ranger = 3
            self.__sample_port = int(self.__sensor_config["samplePort"])
            self.__sample_time = float(self.__sensor_config["sampleTime"])
            self.__distance = 0.0
            self.__distance = grovepi.ultrasonicRead(self.__sample_port)

            print("Distance: ",self.__distance)
            print("Prev Distance: ", self.__prev_distance)
            print("\n")
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
        super(GroveUSRanger, self).push_value_to_store(data_payload)
        self.__storage.push(data_payload)

    def get_last_value(self):
        """
        :return:
        """
        super(GroveUSRanger, self).get_last_value()
        raise NotImplementedError

    def extract_value(self):
        """
        Extract the temperature, pressure, humidity from the I2C grove sensor
        :return:
        """
        super(GroveUSRanger, self).extract_value()
        self.__log.info("Entered extract value, keep_extracting={}".format(self.__keep_extracting))
        while self.__keep_extracting:
            try:
                current_time = datetime.utcnow()
                timediff = current_time - self.__last_push_to_cloud
                seconds = timediff.seconds
                #timestamp = str(datetime.utcnow())
                timestamp = str(current_time.strftime('%Y-%m-%dT%H:%M:%S.%f') +'Z')
                self.__distance = 0.0
                self.__distance = grovepi.ultrasonicRead(self.__sample_port)
                distance = self.__distance
                prev_distance = self.__prev_distance
                data = (timestamp, {"values": [str(prev_distance), str(distance)],
                                    "Previous distance": str(distance),
                                    "Distance":str(prev_distance)})
                if (seconds >= 10.0 or prev_distance <> distance): 
                    self.push_value_to_store(data)
                    self.__last_push_to_cloud = current_time
                    self.__prev_distance = self.__distance
            except:
                err_msg = traceback.format_exc()
                self.__log.error(err_msg)
            time.sleep(self.__sample_time)
            
        self.__log.info("Outside the extract value loop, keep_extracting={}".format(self.__keep_extracting))

    def stop_sensor(self):
        """
        Stops a running sensor
        :return: True if the stopping process was succesful, otherwise False
        """
        super(GroveUSRanger, self).stop_sensor()
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

    def start_sensor(self):
        """
        starts the sensor, collects values in a separate thread
        :return: True if the sensor was started without a problem, False otherwise
        """
        super(GroveUSRanger, self).start_sensor()
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
        Create the Ultrasonic Ranger Sensor object
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
        self.__distance = None
        self.__prev_distance = None
        self.__sample_time = None
        self.__sample_port = None
        self.__keep_extracting = False
        self.__last_push_to_cloud = datetime.utcnow()
        self.__storage = SensorStorage.LowFrequencyStorage(self.__master_config, self.__sensor_config, self.__sensor_id)
        self.__log.info("Initializing sensor")
        success = self.initialize_sensor(self.__master_config, self.__sensor_id)
        if not success:
            raise Exception("Could not initialize the THP sensor! Check log")
