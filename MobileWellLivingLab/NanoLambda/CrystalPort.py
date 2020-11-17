import ctypes
import sys


class CrystalPort():
    pSpecDevice = None

    def __init__(self):
        pass

    def initialize_device_api(self, crystal_port_library_path):

        self.pSpecDevice = ctypes.CDLL(crystal_port_library_path)
        print ("[PythonPrism] CrystalPort Library Loaded Successfully!")

    def connect_device(self):

        ret = self.pSpecDevice.duConnect()

        if ret <= 0:
            print ("[PythonPrismError] Device not Connected!")
            return -1;
        else:
            print ("[PythonPrism] Device Connected Successfully!")
            return ret

    def disconnect_device(self):

        ret = self.pSpecDevice.duDisconnect()

        if ret <= 0:
            print ("[PythonPrismError] Device not Connected!")
            return -1;
        else:
            print ("[PythonPrism] Device disConnected Successfully!")
            return ret

    def get_sensor_list(self):

        sensorList1DBuffer = ctypes.c_char * 26
        sensorList1D = sensorList1DBuffer()

        print("In List")
        sensorList2D = self.pSpecDevice.duGetSensorList()

        for i in sensorList2D:
            print(i)

    def index_activation(self, sensor_index=0):

        ret = self.pSpecDevice.duActivateSensorWithIndex(sensor_index)

        if ret <= 0:
            print ("[PythonPrismError] Activating Sensor with Index failed!")
            return -1;
        else:
            print ("[PythonPrism] Successfully Activated the sesnor with specific index: ", sensor_index)
            return ret

    def total_sensors_supported(self):

        ret = self.pSpecDevice.duGetMaxSensorCount()

        if ret <= 0:
            print ("[PythonPrismError] Failed to get total number of sensors supported")
            return -1;
        else:
            print ("[PythonPrism] Total number of sensors supported in this version of SDK: ", ret)
            return ret

    def device_ID_activation(self, sensorID):

        ret = self.pSpecDevice.duActivateSensorWithID(sensorID)

        if ret <= 0:
            print ("[PythonPrismError] Activating Sensor with device failed:", sensorID)
            return -1;
        else:
            print ("[PythonPrism] Successfully Activated the sesnor with specific device ID: ", sensorID)
            return ret

    def total_sensors_connected(self):

        ret = self.pSpecDevice.duGetTotalSensors()

        if ret <= 0:
            print ("[PythonPrismError] No Device Attached to the system!")
            return -1;
        else:
            print ("[PythonPrism] Total Device/s Attached: ", ret)
            return ret

    def get_sensor_id_device(self):

        sensorIDBuffer = ctypes.c_char * 26
        sensorID = sensorIDBuffer()
        ret = self.pSpecDevice.duGetSensorID(sensorID)

        if ret <= 0:
            print ("[PythonPrismError] UnKnown Sensor ID From Device", sensorID.value)
            return (-1, -1)
        else:
            print ("[PythonPrism] SensorID From Device: ", sensorID.value)
            return (ret, sensorID.value)

    def get_shutter_speed(self):

        ret = self.pSpecDevice.duGetShutterSpeed()

        print ("[PythonPrism] Current Shutter Speed is:  ", ret)
        return ret

    def get_shutter_speed_limits(self):

        min_ss = ctypes.c_int()
        max_ss = ctypes.c_int()

        ret = self.pSpecDevice.duGetShutterSpeedLimits(ctypes.byref(min_ss), ctypes.byref(max_ss))

        if ret <= 0:
            print ("[PythonPrismError] Getting shutter speed limits From Device Failed")
            return (-1, -1, -1)
        else:
            print ("[PythonPrism-FromDevice]  Min SS: ", min_ss.value, ", Max SS: ", max_ss.value)
            return (min_ss.value, max_ss.value)

    def ss_to_exposure_time(self, shutter_speed, master_clock=5.0):

        exposure_time_value = ctypes.c_double()

        ret = self.pSpecDevice.duShutterSpeedToExposureTime(master_clock, shutter_speed,
                                                            ctypes.byref(exposure_time_value))

        if ret <= 0:
            print ("[PythonPrismError] Converting shutter speed value to exposure time failed")
            return -1
        else:
            print ("[PythonPrism-FromDevice]  ShutterSpeed: ", shutter_speed, " with master clock: ", master_clock,
                   " equals to Exposure Time: ", exposure_time_value.value)
            return (exposure_time_value.value)

    def exposure_time_to_ss(self, exposure_time_value, master_clock=5.0):

        shutter_speed = ctypes.c_int()

        ret = self.pSpecDevice.duExposureTimeToShutterSpeed(master_clock, exposure_time_value,
                                                            ctypes.byref(shutter_speed))

        print(shutter_speed.value)

        if ret <= 0:
            print ("[PythonPrismError] Converting Exposure Time value to shutter speed failed")
            return -1
        else:
            print (
            "[PythonPrism-FromDevice]  Exposure time: ", exposure_time_value, " with master clock: ", master_clock,
            " equals to SS: ", shutter_speed.value)
            return (exposure_time_value.value)

    def set_shutter_speed(self, newSS=1):

        ret = self.pSpecDevice.duSetShutterSpeed(newSS)

        if ret <= 0:
            print ("[PythonPrismError] Setting New Shutter Speed to the Device Failed")
            return -1;
        else:
            print ("[PythonPrism] New Shutter Speed ( ", newSS, ") Successfully set to the Device")
            return ret

    def get_optimal_shutter_speed(self, valid_filters, valid_filters_num):

        print ("[PythonPrism] Getting Optimal Shutter Speed.......")

        ret = self.pSpecDevice.duGetOptimalShutterSpeed(valid_filters, valid_filters_num)

        if ret <= 0:
            print ("[PythonPrismError] Getting Optimal Shutter Speed from the Device Failed!")
            return -1
        else:
            print ("[PythonPrism] Optimal Shutter Speed: ", ret)
            return ret

    def get_filter_data(self, averages=20):

        filterDataBuffer = ctypes.c_double * 1024
        filterData = filterDataBuffer()
        ret = self.pSpecDevice.duGetFilterData(ctypes.byref(filterData), averages)

        if ret <= 0:
            print ("[PythonPrismError] Getting Filter Data from the Device Failed")
            return -1;
        else:
            print ("[PythonPrism] Successfully Got Filter Data from the Device")
            return filterData

    def get_sensor_parameters_from_device(self):

        adc_gain = ctypes.c_int()
        adc_range = ctypes.c_int()

        ret = self.pSpecDevice.duGetSensorParameters(ctypes.byref(adc_gain), ctypes.byref(adc_range))

        if ret <= 0:
            print ("[PythonPrismError] Getting Register Settings From Device Failed")
            return (-1, -1, -1)
        else:
            print ("[PythonPrism-FromDevice] adcGain: ", adc_gain.value, ", adcRange: ", adc_range.value)
            return (adc_gain.value, adc_range.value)

    def set_sensor_parameters_to_device(self, adc_gain, adc_range):

        print ("[PythonPrism] (ADC Gain ,  ADC Range) : (", adc_gain, " , ", adc_range, " )")

        ret = self.pSpecDevice.duSetSensorParameters(adc_gain, adc_range)

        if ret <= 0:
            print ("[PythonPrismError] Setting Register Settings Failed")
            return -1;
        else:
            print ("[PythonPrism] Setting Register Settings Successful")
            return ret


if __name__ == '__main__':
    device = CrystalPort()
    device.initialize_device_api('../Libs/libCrystalPort.so')
    device.connect_device()
    ret, sensorID = device.get_sensor_id_device()
    device.get_sensor_list()
    device.device_ID_activation(sensorID)
    filterData = device.get_filter_data()
    # print(len(list(filterData)))
    # print(list(filterData))
    device.total_sensors_connected()
    device.index_activation()
    device.get_optimal_shutter_speed(None, None)
    adc_gain, adc_range = device.get_sensor_parameters_from_device()
    device.set_shutter_speed(50)
    device.get_shutter_speed()
    device.get_shutter_speed_limits()
    device.set_sensor_parameters_to_device(adc_gain, adc_range)
    device.ss_to_exposure_time(22)
    # device.exposure_time_to_ss(4)
    device.disconnect_device()
