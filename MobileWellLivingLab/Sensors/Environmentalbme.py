from Sensors import Sensor
from Storages import SensorStorage
import mWLLUtilities
from datetime import datetime
import time
import threading
import logging
import traceback
from Sensors import bme280

class BME_TempPresHum(Sensor.GenericSensor):
    def initialize_sensor(self, config, sensor_id):
        """
        Inititalize the I2C sensor object and setup the sample time
        :param config:
        :param sensor_id:
        :return:
        """
        super(BME_TempPresHum, self).initialize_sensor(config, sensor_id)
        self.__log.info("Entered initialize_sensor")
        try:
            """

            self.__bus = smbus2.SMBus(1)
            self.__address = 0x77
            self.__i2c_obj = bme280.load_calibration_params(self.__bus,self.__address)
            self.__THP_obj = bme280.sample(self.__bus,self.__address,self.__i2c_obj)
            
            """
	    temperature = pressure = humidity = 0.0

            #print "Temperature : ", temperature, "C"
            #print "Pressure : ", pressure, "hPa"
            #print "Humidity : ", humidity, "%"

	    temperature,pressure,humidity = bme280.readBME280All()

            print "Temperature : ", temperature, "C"
            print "Pressure : ", pressure, "hPa"
            print "Humidity : ", humidity, "%"

            self.__temperature = temperature
            self.__pressure = pressure
            self.__humidity = humidity
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
        super(BME_TempPresHum, self).push_value_to_store(data_payload)
        self.__storage.push(data_payload)

    def get_last_value(self):
        """
        :return:
        """
        super(BME_TempPresHum, self).get_last_value()
        raise NotImplementedError

    def extract_value(self):
        """
        Extract the temperature, pressure, humidity from the I2C Bosch sensor
        :return:
        """
        super(BME_TempPresHum, self).extract_value()
        self.__log.info("Entered extract value, keep_extracting={}".format(self.__keep_extracting))
        while self.__keep_extracting:
            try:
                timestamp = str(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f') +'Z')
    	        
                temperature,pressure,humidity = bme280.readBME280All()
                self.__temperature = temperature
                self.__pressure = pressure
                self.__humidity = humidity
                self.__sample_time = float(self.__sensor_config["sampleTime"])


                print "Temperature : ", temperature, "C"
                print "Pressure : ", pressure, "hPa"
                print "Humidity : ", humidity, "%"
                """
                temperature = self.__temperature
                humidity = self.__humidity
                pressure = self.__pressure
                """
                data = (timestamp, {"values": [str(temperature), str(humidity), str(pressure)],
                                    "Temperature": str(temperature),
                                    "Humidity": str(humidity),
                                    "Pressure": str(pressure)})
                self.push_value_to_store(data)
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
        super(BME_TempPresHum, self).stop_sensor()
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
        super(BME_TempPresHum, self).start_sensor()
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
        Create the I2C Temperature Pressure Humidity Sensor object
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
        self.__bus = None
        self.address = None
        self.__THP_obj = None
        self.__i2c_obj = None
        self.__sample_time = None
        self.__max_files_upload = None
        self.__keep_extracting = False
        self.__storage = SensorStorage.LowFrequencyStorage(self.__master_config, self.__sensor_config, self.__sensor_id)
        self.__log.info("Initializing sensor")
        success = self.initialize_sensor(self.__master_config, self.__sensor_id)
        if not success:
            raise Exception("Could not initialize the THP sensor! Check log")