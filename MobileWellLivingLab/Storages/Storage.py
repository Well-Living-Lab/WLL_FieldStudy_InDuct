#!/usr/bin/env python
"""
Abstract class to model storage handling for mWLL
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


class GenericStorage:
    __metaclass__ = ABCMeta

    @abstractmethod
    def initialize_storage(self):
        return

    @abstractmethod
    def push_to_cloud(self):
        return

    @abstractmethod
    def push(self, data):
        return

    @abstractmethod
    def write_to_disk(self):
        return

    @abstractmethod
    def push_to_process(self):
        return
