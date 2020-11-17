#!/usr/bin/env python
"""
The utility code we need to make mWLL happen!
"""
import Queue
import json
import csv
import threading
import logging
import socket

__author__ = "Syed Shabih Hasan"
__copyright__ = "Copyright 2018, Well Living Lab"
__credits__ = ["Syed Shabih Hasan"]
__license__ = "Well Living Lab Proprietary and Confidential"
__version__ = "0.1.0"
__maintainer__ = "Syed Shabih Hasan"
__email__ = "syed.shabih.hasan@delos.com"
__status__ = "Development"


def read_config_as_json(filename):
    config = {}
    with open(filename, "r") as data_file:
        config = json.load(data_file)
    return config

def read_config_as_csv(filename):
    config = {}
    with open(filename, "r") as f:
        csv_obj = csv.reader(f, delimiter=",")
        for csv_row in csv_obj:
            config[csv_row[0]] = csv_row[1]
    return config

def read_config(filename):
    config = {}
    with open(filename, "r") as f:
        csv_obj = csv.reader(f, delimiter=",")
        for csv_row in csv_obj:
            config[csv_row[0]] = csv_row[1]
    return config

def check_connection():
    try:
        s = socket.create_connection(("www.google.com",80))
        s.close()
        return True
    except OSError:
        pass
    return False

def check_internet(host="8.8.8.8", port=53, timeout=3):
  """
  Host: 8.8.8.8 (google-public-dns-a.google.com)
  OpenPort: 53/tcp
  Service: domain (DNS/TCP)
  """
  try:
    socket.setdefaulttimeout(timeout)
    socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
    return True
  except socket.error as ex:
    print(ex)
    return False

class Constants:
    # Extraction OK
    DYLOS_EXTRACTION_OK = "DY-OK"


class Logger:
    """
    DEPRECATED
    DO NOT USE!
    push data to a single synchronzied queue, tuple (boolean: true = error, message). A continuously running write
    function
    """

    def __push_message(self, msg_type, message):
        self.__log.put((msg_type, message))
        if not self.__event.isSet():
            self.__event.set()

    def close_logger(self):
        self.__keep_writing = False
        if not self.__event.isSet():
            self.__event.set()

    def __write_log(self):
        while self.__keep_writing:
            while self.__event.isSet():
                while self.__log.qsize() > 0:
                    (msg_type, msg) = self.__log.get()
                    if msg_type == "normal":
                        with open(self.__normal_log_file, "a") as f_n:
                            f_n.write(msg + "\n")
                    elif msg_type == "error":
                        with open(self.__error_log_file, "a") as f_e:
                            f_e.write(msg + "\n")
                    else:
                        # Place holder for any other type of message
                        pass
                self.__event.clear()
            self.__event.wait()
        if self.__log.qsize() > 0:
            with open(self.__normal_log_file, "a") as f_n, open(self.__error_log_file, "a") as f_e:
                (msg_type, msg) = self.__log.get()
                if msg_type == "normal":
                    f_n.write(msg + "\n")
                elif msg_type == "error":
                    f_e.write(msg + "\n")
                else:
                    # place holder
                    pass
        return

    def push(self, log_type, message):
        threading.Thread(target=self.__push_message, args=(log_type, message,)).start()

    def __init__(self, error_file, normal_log_file):
        self.__error_log_file = error_file
        self.__normal_log_file = normal_log_file
        self.__log = Queue.Queue()
        self.__keep_writing = True
        self.__event = threading.Event()
        self.__event.clear()
        self.__write_log()


class CustomLog:
    def __init__(self, logger, prefix_id):
        self.__log = logger
        self.__prefix_ID = prefix_id

    def debug(self, message):
        self.__log.debug("{}-{}".format(self.__prefix_ID, message))

    def info(self, message):
        self.__log.info("{}-{}".format(self.__prefix_ID, message))

    def warning(self, message):
        self.__log.warning("{}-{}".format(self.__prefix_ID, message))

    def error(self, message):
        self.__log.error("{}-{}".format(self.__prefix_ID, message))

    def critical(self, message):
        self.__log.critical("{}-{}".format(self.__prefix_ID, message))


