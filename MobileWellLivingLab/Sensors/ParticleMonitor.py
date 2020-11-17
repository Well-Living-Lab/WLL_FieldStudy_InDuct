from Sensors import Sensor
from Storages.SensorStorage import LowFrequencyStorage
from datetime import datetime
import mWLLUtilities
import serial
import time
import traceback
import threading
import logging
import serial
import struct


class Dylos(Sensor.GenericSensor):
    def extract_value(self):
        """
        Extracts the data values from the Dylos particle counter and pushes them to the storage
        :return: Nothing
        """
        super(Dylos, self).extract_value()
        self.__log.info("Entered extract value, keep_extracting={}".format(self.__keep_extracting))
        while self.__keep_extracting:
            try:
                if self.__serial_conn.inWaiting() > 0:
                    data = self.__serial_conn.read(self.__serial_conn.inWaiting())
                    #timestamp = str(datetime.utcnow())
                    timestamp = str(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f') +'Z')
                    data = data.splitlines()[0]
                    data = data.split(",")
                    self.push_value_to_store((timestamp, data))
            except:
                err_msg = traceback.format_exc()
                self.__log.error(err_msg)
            time.sleep(self.__sample_time)
        self.__log.info("Outside the extract_value loop, keep_extracting={}".format(self.__keep_extracting))

    def push_value_to_store(self, data_payload):
        """
        :param data_payload: pushes the data to the storage
        :return: Nothing
        """
        super(Dylos, self).push_value_to_store(data_payload)
        self.__storage.push(data_payload)

    def get_last_value(self):
        super(Dylos, self).get_last_value()
        # Will not be implemented in Dylos
        raise NotImplementedError

    def initialize_sensor(self, config, sensor_id):
        """
        Initialize the Dylos by setting up the serial connection, getting the sensor configuration, and sampling rate
        :param config: master configuration in the dictionary format
        :param sensor_id: id string identifying the sensor
        :return: True if initialization was successful, otherwise False
        """
        super(Dylos, self).initialize_sensor(config, sensor_id)
        try:
            self.__log.info("Establish serial connection, setup sensor configuration, sample time")
            self.__serial_conn = serial.Serial("/dev/ttyUSB0")
            self.__sample_time = float(self.__sensor_config["sampleTime"])
            self.__max_files_upload = int(self.__sensor_config["maxFilesUpload"])
            return True
        except:
            err_msg = traceback.format_exc()
            self.__log.error(err_msg)
            return False

    def start_sensor(self):
        """
        Starts the sensor, collects values in a separate thread
        :return: True if starting is successful, otherwise False
        """
        super(Dylos, self).start_sensor()
        try:
            self.__log.info("Checking if connection is open")
            if not self.__serial_conn.isOpen():
                self.__log.info("Not open, opening")
                self.__serial_conn.open()
            self.__log.info("Starting the sensor thread")
            # set to false to stop any other thread that might have been running
            self.__keep_extracting = False
            if self.__sensor_thread is not None:
                if self.__sensor_thread.isAlive():
                    self.__log.info(
                        "There is a thread that is running, wait for {}s to stop".format(self.__sample_time))
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

    def stop_sensor(self):
        """
        Stop the Dylos sensor
        :return: True if successful, False otherwise
        """
        super(Dylos, self).stop_sensor()
        try:
            self.__log.info("Entered stop_sensor, setting flag to false and waiting for thread to stop")
            self.__keep_extracting = False
            self.__sensor_thread.join(timeout=self.__sample_time + 0.0)
            self.__log.info("Either timeout expired or the thread terminated")
            self.__sensor_thread = None
            self.__serial_conn.close()
            return True
        except:
            err_msg = traceback.format_exc()
            self.__log.error(err_msg)
            return False

    def __init__(self, master_config, sensor_config_location, sensor_id):
        """
        Initialize the Dylos Class
        :param master_config: master configuration file in the dictionary format
        """
        logging.info("Entered Dylos!")
        self.__sensor_id = sensor_id
        self.__master_config = master_config
        self.__sensor_config = mWLLUtilities.read_config(
            self.__master_config["cwd"] + sensor_config_location)
        self.__log = mWLLUtilities.CustomLog(self.__master_config["logger"], self.__sensor_id)
        # self.__log = self.__master_config["logger"]
        self.__log.info("Entered Dylos, setting up variables")
        self.__serial_conn = None
        self.__keep_extracting = False
        self.__sample_time = None
        self.__max_files_upload = None
        self.__sensor_thread = None
        # the storage variable
        self.__log.info("Setting up storage, low frequency")
        self.__storage = LowFrequencyStorage(self.__master_config, self.__sensor_config, self.__sensor_id)
        # initialize the sensor
        self.__log.info("Initializing sensor")
        success = self.initialize_sensor(master_config, self.__sensor_id)
        if not success:
            raise Exception("Could not initialize Dylos! Check log")


class GroveCO2(Sensor.GenericSensor):
    def initialize_sensor(self, config, sensor_id):
        """
        :param config:
        :param sensor_id:
        :return:
        """
        super(GroveCO2, self).initialize_sensor(config, sensor_id)
        try:
            self.__serial_conn = serial.Serial("/dev/ttyAMA0", 9600)
            self.__serial_conn.flush()
            self.__sample_time = float(self.__sensor_config["sampleTime"])
            self.__max_files_upload = int(self.__sensor_config["maxFilesUpload"])
            self.__commands = {
                "get": "\xff\x01\x86\x00\x00\x00\x00\x00\x79",
                "zero": "\xff\x01\x87\x00\x00\x00\x00\x00\x78",
                "span": "\xff\x01\x88\x00\x00\x00\x00\x00\xA0"
            }
            return True
        except:
            err_msg = traceback.format_exc()
            self.__log.error(err_msg)
            return False

    def get_last_value(self):
        """
        :return:
        """
        super(GroveCO2, self).get_last_value()
        raise NotImplementedError

    def extract_value(self):
        """
        :return:
        """
        super(GroveCO2, self).extract_value()
        self.__log.info("Entered extract value, keep_extracting: {}".format(self.__keep_extracting))
        while self.__keep_extracting:
            try:
                self.__serial_conn.write(self.__commands["get"])
                time.sleep(float(self.__sensor_config["readDelay"]))
                n = self.__serial_conn.inWaiting()
                if n > 0:
                    # timestamp = str(datetime.utcnow())
                    timestamp = str(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f') +'Z')
                    raw_data = self.__serial_conn.read(n)
                    high_concentration = struct.unpack('B', raw_data[2])[0]
                    low_concentration = struct.unpack('B', raw_data[3])[0]
                    co2_conc = high_concentration * 256 + low_concentration
                    temperature = struct.unpack('B', raw_data[4])[0] - 40
                    data = {"values": [str(co2_conc), str(temperature), str(high_concentration),
                                       str(low_concentration)],
                            "CO2": str(co2_conc),
                            "HighConcentration": str(high_concentration),
                            "LowConcentration": str(low_concentration),
                            "Temperature": str(temperature)}
                    self.push_value_to_store((timestamp, data))
                else:
                    self.__log.info("Extract value: n=0")
            except:
                err_msg = traceback.format_exc()
                self.__log.error(err_msg)
            time.sleep(self.__sample_time)
        self.__log.info("Outside the main loop, keep_extracting={}".format(self.__keep_extracting))

    def push_value_to_store(self, data_payload):
        """
        :param data_payload:
        :return:
        """
        super(GroveCO2, self).push_value_to_store(data_payload)
        self.__storage.push(data_payload)

    def stop_sensor(self):
        """
        :return:
        """
        super(GroveCO2, self).stop_sensor()
        try:
            self.__log.info("Entered stop_sensor, setting flag to false and waiting for {}s".format(self.__sample_time))
            self.__keep_extracting = False
            self.__sensor_thread.join(timeout=self.__sample_time+0.)
            self.__sensor_thread = None
            return True
        except:
            err_msg = traceback.format_exc()
            self.__log.error(err_msg)
            return False

    def start_sensor(self):
        """
        :return:
        """
        super(GroveCO2, self).start_sensor()
        self.__log.info("Entered start_sensor")
        try:
            self.__log.info("Starting sensor thread")
            self.__keep_extracting = False
            if self.__sensor_thread is not None:
                if self.__sensor_thread.isAlive():
                    self.__log.info(
                        "Sensor thread is still alive, waiting for {}s for it to finish".format(self.__sample_time))
                    self.__sensor_thread.join(timeout=self.__sample_time + 0.)
                    self.__log.info("Sensor thread join timed out, setting it to None")
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
        """
        # TODO
        self.__sensor_id = sensor_id
        self.__master_config = master_config
        self.__sensor_config = mWLLUtilities.read_config(
            self.__master_config["cwd"] + sensor_config_location)
        self.__log = mWLLUtilities.CustomLog(self.__master_config["logger"], self.__sensor_id)
        self.__log.info("Entered the CO2 Sensor")
        self.__keep_extracting = False
        self.__serial_conn = None
        self.__sample_time = None
        self.__max_files_upload = None
        self.__sensor_thread = None
        self.__commands = None
        self.__storage = LowFrequencyStorage(self.__master_config, self.__sensor_config, self.__sensor_id)
        self.__log.info("Initializing Sensor")
        success = self.initialize_sensor(self.__master_config, self.__sensor_id)
        if not success:
            raise Exception("Could not initialize the "+sensor_id+" sensor! Check log")
