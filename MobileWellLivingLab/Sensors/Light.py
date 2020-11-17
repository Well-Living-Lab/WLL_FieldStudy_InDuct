from Sensors import Sensor
from Storages.SensorStorage import LowFrequencyStorage
from NanoLambda.CrystalBase import *
from NanoLambda.CrystalColor import *
from NanoLambda.CrystalCore import *
from NanoLambda.CrystalPort import *
import mWLLUtilities
import traceback
import time
import threading
from datetime import datetime


class NanoLambda(Sensor.GenericSensor):
    def initialize_sensor(self, config, sensor_id):
        super(NanoLambda, self).initialize_sensor(config, sensor_id)
        try:
            self.__log.info("Initializing the sensor: " + self.__sensor_id)
            self.__base = CrystalBase()
            self.__core = CrystalCore()
            self.__device = CrystalPort()
            self.__color = CrystalColor()
            self.__sample_time = float(self.__sensor_config["sampleTime"])
            self.__max_files_upload = int(self.__sensor_config["maxFilesUpload"])

            # use the so files
            self.__log.info("Initializing APIs")
            self.__base.initialize_base_api(self.__master_config["cwd"] + self.__sensor_config["libBase"])
            self.__core.initialize_core_api(self.__master_config["cwd"] + self.__sensor_config["libCore"])
            self.__device.initialize_device_api(self.__master_config["cwd"] + self.__sensor_config["libPort"])
            self.__color.initialize_color_api(self.__master_config["cwd"] + self.__sensor_config["libCore"])

            no_of_devices = self.__device.connect_device()

            if no_of_devices > 0:
                (ret, sensorID) = self.__device.get_sensor_id_device()
                self.__core.create_core_object()
                self.__log.info("Calibration")
                calibration_file_path = b"{}sensor_".format(self.__master_config["cwd"] +
                                                            self.__sensor_config["calibration"]) + sensorID + b".dat"
                ret = self.__core.load_sensor_file(calibration_file_path)
                (ret, sensorID) = self.__core.get_sensor_id_file()
                self.__device.get_sensor_parameters_from_device()
                (adcGain, adcRange) = self.__core.get_sensor_parameters_from_calibration_file()
                ret = self.__device.set_sensor_parameters_to_device(adcGain, adcRange)
                self.__no_of_sensors = self.__device.total_sensors_connected()
                self.__core.get_capacity_sensor_data_list()
            else:
                raise Exception("Number of devices == 0 (Actual: {})".format(no_of_devices))
            return True
        except:
            err_msg = traceback.format_exc()
            self.__log.error(err_msg)
            return False

    def stop_sensor(self):
        super(NanoLambda, self).stop_sensor()
        try:
            self.__log.info("Entered stop_sensor, clearing flag and waiting")
            self.__keep_extracting = False
            self.__sensor_thread.join(timeout=self.__sample_time + 0.)
            self.__sensor_thread = None
            return True
        except:
            err_msg = traceback.format_exc()
            self.__log.error(err_msg)
            return False

    def start_sensor(self):
        super(NanoLambda, self).start_sensor()
        try:
            self.__log.info("Entered start_sensor")
            self.__keep_extracting = False
            if self.__sensor_thread is not None:
                if self.__sensor_thread.isAlive():
                    self.__log.info(
                        "Sensor thread is still alive, waiting for {}s before stopping".format(self.__sample_time))
                    self.__sensor_thread.join(timeout=self.__sample_time + 0.)
                    self.__log.info("Thread timed out, clearing it")
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

    def get_last_value(self):
        super(NanoLambda, self).get_last_value()
        raise NotImplementedError

    def extract_value(self):
        super(NanoLambda, self).extract_value()
        self.__log.info("Entered extract value, keep_extracting={}".format(self.__keep_extracting))
        while self.__keep_extracting:
            try:
                for index in range(self.__no_of_sensors):
                    data_json = {}
                    #timestamp = str(datetime.utcnow())
                    timestamp = str(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f') +'Z')

                    # activate sensor
                    ret = self.__device.index_activation(index)

                    # get the sensor id
                    (ret, sensorID) = self.__device.get_sensor_id_device()

                    # get and set shutter speed
                    self.__device.get_shutter_speed()
                    self.__device.set_shutter_speed(1)

                    # get a filter output
                    filterData = self.__device.get_filter_data(20)

                    # set background data
                    self.__core.set_background_data(filterData)

                    # get and set shutter speed
                    self.__device.get_shutter_speed()
                    valid_filter_num = self.__core.get_num_of_valid_filters()
                    valid_filters = self.__core.get_valid_filters2()

                    # get shutter speed
                    newSS = self.__device.get_optimal_shutter_speed(valid_filters, valid_filter_num)
                    data_json["OptimalSS"] = newSS
                    self.__device.set_shutter_speed(newSS)

                    # convert SS to exposure time (ms)
                    self.__device.ss_to_exposure_time(newSS, 5)

                    # start extracting the data
                    filterData = self.__device.get_filter_data(20)
                    data_json["RawFilterData"] = list(filterData)
                    self.__core.get_resolution()
                    specSize = self.__core.get_spectrum_length()
                    (ret, specData, wavelengthData) = self.__core.calculate_spectrum(filterData, newSS)
                    data_json["SpectrumData"] = list(specData)
                    data_json["WavelengthData"] = list(wavelengthData)
                    (start_wavelength, end_wavelength, interval_wavelength) = self.__core.get_wavelength_information()
                    wavelength_dict = {"StartWL": start_wavelength,
                                       "EndWL": end_wavelength,
                                       "IntervalWL": interval_wavelength}
                    data_json["WavelengthData"] = wavelength_dict
                    color_data = self.__color.calculate_color_data(specData, wavelengthData, specSize)
                    color_dict = {
                        "Red": color_data[0],
                        "Green": color_data[1],
                        "Blue": color_data[2],
                        "large_X": color_data[3],
                        "large_Y": color_data[4],
                        "large_Z": color_data[5],
                        "small_x": color_data[6],
                        "small_y": color_data[7],
                        "small_z": color_data[8],
                        "CCT": color_data[9],
                    }
                    data_json["Color"] = color_dict
                    val_list = [str(x) for x in list(specData)]
                    data_json["values"] = val_list

                    # push to storage and cloud
                    self.push_value_to_store((timestamp, data_json))
            except:
                err_msg = traceback.format_exc()
                self.__log.error(err_msg)
            time.sleep(self.__sample_time)
        self.__log.info("Outside the extract_value while loop, keep_extracting={}".format(self.__keep_extracting))

    def push_value_to_store(self, data_payload):
        super(NanoLambda, self).push_value_to_store(data_payload)
        self.__storage.push(data_payload)

    def __init__(self, master_config, sensor_config_location, sensor_id):
        self.__master_config = master_config
        self.__sensor_id = sensor_id
        self.__sensor_config = mWLLUtilities.read_config(
            self.__master_config["cwd"] + sensor_config_location)
        self.__log = mWLLUtilities.CustomLog(self.__master_config["logger"], self.__sensor_id)
        self.__log.info("Entered NanoLambda")
        self.__core = None
        self.__base = None
        self.__color = None
        self.__device = None
        self.__no_of_sensors = None
        self.__keep_extracting = False
        self.__sensor_thread = None
        self.__sample_time = None
        self.__max_files_upload = None
        self.__storage = LowFrequencyStorage(self.__master_config, self.__sensor_config, self.__sensor_id)
        self.__log.info("Initializing the sensor")
        success = self.initialize_sensor(self.__master_config, self.__sensor_id)
        if not success:
            raise Exception("Could not initialize NanoLambda, check log!")
