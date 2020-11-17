import ctypes
import sys


class CrystalColor():
    pSpecColor = None

    def __init__(self):
        pass

    def initialize_color_api(self, crystal_core_library_path):

        self.pSpecColor = ctypes.CDLL(crystal_core_library_path)

        ret = self.pSpecColor.acInitialize()

        if ret <= 0:
            print ("[PythonPrismError] CrystalColor API Initialization  Failed!")
            return -1;
        else:
            print ("[PythonPrism] CrystalColor API Initializated Successfully!")
            return ret

    def calculate_color_data(self, specData, wavelengthData, specSize):

        Color_Red = ctypes.c_double()
        Color_Green = ctypes.c_double()
        Color_Blue = ctypes.c_double()
        large_X = ctypes.c_double()
        large_Y = ctypes.c_double()
        large_Z = ctypes.c_double()
        small_x = ctypes.c_double()
        small_y = ctypes.c_double()
        small_z = ctypes.c_double()
        CCT = ctypes.c_double()

        ret = self.pSpecColor.acCalculateColor(specData, wavelengthData, specSize,
                                               ctypes.byref(large_X), ctypes.byref(large_Y), ctypes.byref(large_Z),
                                               ctypes.byref(Color_Red), ctypes.byref(Color_Green),
                                               ctypes.byref(Color_Blue),
                                               ctypes.byref(small_x), ctypes.byref(small_y), ctypes.byref(small_z),
                                               ctypes.byref(CCT))

        if ret <= 0:
            print ("[PythonPrismError] Calculating Color Data Failed!")
            return (-1, -1, -1, -1, -1, -1, -1, -1, -1, -1);
        else:
            print (
            "[PythonPrism] (R , G , B) : (", Color_Red.value, " , ", Color_Green.value, " , ", Color_Blue.value, " )")
            print ("[PythonPrism] (X , Y , Z) : (", large_X.value, " , ", large_Y.value, " , ", large_Z.value, " )")
            print ("[PythonPrism] (x , y , z) : (", small_x.value, " , ", small_y.value, " , ", small_z.value, " )")
            print ("[PythonPrism] (CCT) : (", CCT.value, " )")
            return (Color_Red.value, Color_Green.value, Color_Blue.value, large_X.value, large_Y.value, large_Z.value,
                    small_x.value, small_y.value, small_z.value, CCT.value)

    def close_color_api(self):

        ret = self.pSpecColor.acFinalize()

        if ret <= 0:
            print ("[PythonPrismError] Color API Closing Failed!")
            return -1;
        else:
            print ("[PythonPrism] Color API Closed Successfully!")
            return ret


if __name__ == '__main__':
    CrystalColor().initialize_color_api("../Libs/libCrystalCore.so")
