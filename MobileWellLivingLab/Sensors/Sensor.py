#!/usr/bin/env python
"""
Abstract class modeling the generic sensor to be used in mWLL
"""

from abc import ABCMeta, abstractmethod

__author__ = "Syed Shabih Hasan"
__copyright__ = "Copyright 2018, Well Living Lab"
__credits__ = ["Syed Shabih Hasan"]
__license__ = "Well Living Lab Proprietary and Confidential"
__version__ = "0.1.0"
__maintainer__ = "Syed Shabih Hasan"
__email__ = "syed.shabih.hasan@delos.com"
__status__ = "Development"


class GenericSensor:
    __metaclass__ = ABCMeta

    @abstractmethod
    def initialize_sensor(self, config, sensor_id):
        pass

    @abstractmethod
    def stop_sensor(self):
        pass

    @abstractmethod
    def start_sensor(self):
        pass

    @abstractmethod
    def get_last_value(self):
        pass

    @abstractmethod
    def extract_value(self):
        pass

    @abstractmethod
    def push_value_to_store(self, data_payload):
        pass
