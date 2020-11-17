import ctypes
import sys


class CrystalBase():

    def __init__(self):
        pass

    def initialize_base_api(self, crystal_base_library_path):
        """
        Initialize Function
        This function loaded the needed libraries
        """
        if sys.platform == 'win32':
            ctypes.CDLL("..\Libs\pthreadVC2.dll")

        ctypes.CDLL(crystal_base_library_path)
        print ("[PythonPrism] CrystalBase Library Loaded Successfully!")

        return 1


if __name__ == '__main__':
    CrystalBase().initialize("../Libs/libCrystalBase.so")
