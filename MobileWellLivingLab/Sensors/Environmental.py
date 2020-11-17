from Sensors import Sensor
from Storages import SensorStorage
import mWLLUtilities
from datetime import datetime
import time
import threading
import logging
import traceback
from di_sensors import temp_hum_press


class TempPresHum(Sensor.GenericSensor):
    def initialize_sensor(self, config, sensor_id):
        """
        Inititalize the I2C sensor object and setup the sample time
        :param config:
        :param sensor_id:
        :return:
        """
        super(TempPresHum, self).initialize_sensor(config, sensor_id)
        self.__log.info("Entered initialize_sensor")
        try:
            self.__THP_obj = temp_hum_press.TempHumPress()
            self.__sample_time = float(self.__sensor_config["sampleTime"])
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
        super(TempPresHum, self).push_value_to_store(data_payload)
        self.__storage.push(data_payload)

    def get_last_value(self):
        """
        :return:
        """
        super(TempPresHum, self).get_last_value()
        raise NotImplementedError

    def extract_value(self):
        """
        Extract the temperature, pressure, humidity from the I2C grove sensor
        :return:
        """
        super(TempPresHum, self).extract_value()
        self.__log.info("Entered extract value, keep_extracting={}".format(self.__keep_extracting))
        while self.__keep_extracting:
            try:
                timestamp = str(datetime.utcnow())
                temperature = self.__THP_obj.get_temperature_fahrenheit()
                humidity = self.__THP_obj.get_humidity()
                pressure = self.__THP_obj.get_pressure()
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
        super(TempPresHum, self).stop_sensor()
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
        super(TempPresHum, self).start_sensor()
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
        self.__THP_obj = None
        self.__sample_time = None
        self.__keep_extracting = False
        self.__storage = SensorStorage.LowFrequencyStorage(self.__master_config, self.__sensor_config, self.__sensor_id)
        self.__log.info("Initializing sensor")
        success = self.initialize_sensor(self.__master_config, self.__sensor_id)
        if not success:
            raise Exception("Could not initialize the THP sensor! Check log")
