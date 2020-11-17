import ctypes
import sys


class CrystalCore():
    pSpecCore = None

    def __init__(self):
        pass

    def initialize_core_api(self, crystal_core_library_path):

        self.pSpecCore = ctypes.CDLL(crystal_core_library_path)

        print ("[PythonPrism] CrystalCore Library Loaded Successfully!")

    def create_core_object(self):

        ret = self.pSpecCore.csCreate()

        if ret <= 0:
            print ("[PythonPrismError] Core Object Initialization Failed!")
            return -1;
        else:
            print ("[PythonPrism] Successfully created the core object!")
            return ret

    def close_core_object(self):

        ret = self.pSpecCore.csDestroy()

        if ret <= 0:
            print ("[PythonPrismError] Core API Closing Failed!")
            return -1;
        else:
            print ("[PythonPrism] Core API Closed Successfully!")
            return ret

    def load_sensor_file(self, sensor_file_path):

        ret = self.pSpecCore.csRegister(sensor_file_path)

        if ret <= 0:
            print ("[PythonPrismError] Sensor File Loading Failed!")
            return -1;
        else:
            print ("[PythonPrism] Sensor File Successfully Loaded!")
            return ret

    def get_capacity_sensor_data_list(self):

        ret = self.pSpecCore.csCapacity()

        if ret <= 0:
            print ("[PythonPrismError] Getting capacity list  Failed!")
            return -1;
        else:
            print ("[PythonPrism] Successfully got the capacity list:", ret)
            return ret

    def get_sensor_with_index(self, index=0):

        sensorIDBuffer = ctypes.c_char * 26
        sensorID = sensorIDBuffer()

        ret = self.pSpecCore.csGetSensorWithIndex(index, sensorID)

        if ret <= 0:
            print ("[PythonPrismError] Getting capacity list  Failed!")
            return -1;
        else:
            print ("[PythonPrism] Successfully got sensor ID with index:", sensorID.value)
            return sensorID.value

    def get_sensor_id_file(self):

        sensorIDBuffer = ctypes.c_char * 26
        sensorID = sensorIDBuffer()

        ret = self.pSpecCore.csGetSensorID(sensorID)

        if ret <= 10:
            print ("[PythonPrismError] UnKnown Sensor ID From File: ", sensorID.value)
            return (-1, -1)
        else:
            print ("[PythonPrism] SensorID From File: ", sensorID.value)
            return (ret, sensorID.value)

    def calibration_ID_activation(self, sensorID):

        ret = self.pSpecCore.csActivateSensorWithID(sensorID)

        if ret <= 0:
            print ("[PythonPrismError] Activating sensor with ID is Failed!")
            return -1;
        else:
            print ("[PythonPrism] Successfully activated the sensor with ID!")
            return ret

    def get_wavelength_information(self):

        Start_Wavelength = ctypes.c_double()
        End_Wavelength = ctypes.c_double()
        Interval_Wavelength = ctypes.c_double()

        ret = self.pSpecCore.csGetWavelengthInfo(ctypes.byref(Start_Wavelength), ctypes.byref(End_Wavelength),
                                                 ctypes.byref(Interval_Wavelength))

        if ret <= 0:
            print ("[PythonPrismError] Getting Wavelength Information Failed!")
            return (-1, -1, -1)
        else:
            print (
            "[PythonPrism] (StartWL, EndWL , IntervalWL) : (", Start_Wavelength.value, " , ", End_Wavelength.value,
            " , ", Interval_Wavelength.value, " )")
            return (Start_Wavelength.value, End_Wavelength.value, Interval_Wavelength.value)

    def get_resolution(self):

        resolution = ctypes.c_double()

        ret = self.pSpecCore.csGetResolution(ctypes.byref(resolution))

        if ret <= 0:
            print ("[PythonPrismError] Getting Resolution Failed!")
            return -1
        else:
            print ("[PythonPrism] Resolution For Sensor:  ", resolution.value)
            return resolution.value

    def get_num_of_valid_filters(self):

        ret = self.pSpecCore.csGetNumOfValidFilters()

        if ret <= 0:
            print ("[PythonPrismError] Failed to get num of Valid Filters!")
            return -1;
        else:
            print ("[PythonPrism] Num of Valid Filters: !", ret)
            return ret

    def get_valid_filters(self):

        valid_filters_buffer = ctypes.c_int()
        valid_filters = ctypes.pointer(valid_filters_buffer)
        valid_filters = self.pSpecCore.csGetValidFilters()
        ret = 1
        if ret <= 0:
            print ("[PythonPrismError] Failed to get Valid Filters!")
            return -1;
        else:
            print ("[PythonPrism] Valid Filters Got successfully !")
            return valid_filters

    def get_valid_filters2(self):

        valid_filters_buffer2 = ctypes.c_int * self.get_num_of_valid_filters()
        valid_filters2 = valid_filters_buffer2()

        ret = self.pSpecCore.csGetValidFilters2(ctypes.byref(valid_filters2))

        if ret != self.get_num_of_valid_filters():
            print ("[PythonPrismError] Failed to get Valid Filters!")
            return -1;
        else:
            print ("[PythonPrism] Valid Filters Got successfully !")
            return valid_filters2

    def get_spectrum_length(self):

        ret = self.pSpecCore.csGetSpectrumLength()

        if ret <= 0:
            print ("[PythonPrismError] Getting Spectrum Length Failed!")
            return ret
        else:
            print ("[PythonPrism] SpectrumLength: ", ret)
            return ret

    def get_sensor_parameters_from_calibration_file(self):

        adc_gain = ctypes.c_int()
        adc_range = ctypes.c_int()

        ret = self.pSpecCore.csGetSensorParameters(ctypes.byref(adc_gain), ctypes.byref(adc_range))

        if ret <= 0:
            print ("[PythonPrismError] Getting Register Settings Failed")
            return (-1, -1)
        else:
            print ("[PythonPrism] adcGain: ", adc_gain.value, ", adcRange: ", adc_range.value)
            return (adc_gain.value, adc_range.value)

    def set_background_data(self, filter_data):

        ret = self.pSpecCore.csSetBackground(filter_data)

        if ret <= 0:
            print ("[PythonPrismError] Setting Background data Failed!")
            return ret
        else:
            print ("[PythonPrism] Successfully Set the Background Data!")
            return ret

    def calculate_spectrum(self, filter_data, shutter_speed):

        specDataBuffer = ctypes.c_double * self.pSpecCore.csGetSpectrumLength()
        wavelengthDataBuffer = ctypes.c_double * self.pSpecCore.csGetSpectrumLength()
        specData = specDataBuffer()
        wavelengthData = wavelengthDataBuffer()

        ret = self.pSpecCore.csCalculateSpectrum(filter_data, shutter_speed, ctypes.byref(specData),
                                                 ctypes.byref(wavelengthData))

        if ret <= 0:
            print ("[PythonPrismError] Calculating Spectrum Data Failed!")
            return (-1, -1, -1)
        else:
            print ("[PythonPrism] Successfully Calculated Spectrum ")
            return (ret, specData, wavelengthData)


if __name__ == '__main__':
    CrystalCore().initialize_core_api("../Libs/libCrystalCore.so")
