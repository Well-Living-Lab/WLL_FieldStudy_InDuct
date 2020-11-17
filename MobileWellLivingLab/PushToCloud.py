#!/usr/bin/env python
"""
Push to Cloud: Class to push data to the Azure backend
"""
import requests
import json
import uuid
import traceback
import mWLLUtilities
import threading

__author__ = "Syed Shabih Hasan"
__copyright__ = "Copyright 2018, Well Living Lab"
__credits__ = ["Syed Shabih Hasan"]
__license__ = "Well Living Lab Proprietary and Confidential"
__version__ = "0.1.0"
__maintainer__ = "Syed Shabih Hasan"
__email__ = "syed.shabih.hasan@delos.com"
__status__ = "Development"


class PushToCloud:

    def __init__(self, master_config, sensor_config, sensor_id):
        """
        :param master_config:
        :param sensor_id:
        """
        self.__master_config = master_config
        self.__sensor_config = sensor_config
        self.__sensor_id = sensor_id
        self.__log = mWLLUtilities.CustomLog(self.__master_config["logger"], self.__sensor_id + "." + __name__)
        self.__log.info("Initializing push to cloud")
        self.__cloud_config = mWLLUtilities.read_config(self.__master_config["cwd"] + self.__sensor_config["cloud"])
        self.__log.info("Cloud configuration read")

    def __create_data_payload(self, simple_data, is_complex=False):
        """
        :param: simple_data:
        :param: is_complex
        :return:
        """
        packet_id = uuid.uuid3(uuid.NAMESPACE_DNS,
                               (self.__master_config["DeviceId"] +
                               "," +
                               self.__sensor_id +
                               "," +
                               simple_data["timestamp"]).encode('utf-8'))
        payload = {
            "WLLJSONVersion": "1.0",
            "DataValue": "-1",
            "DataUnits": self.__sensor_config["units"],
            "EventTimeStamp": simple_data["timestamp"],
            "DataId": str(packet_id),
            "id": str(packet_id),
            "DeviceId": self.__master_config["DeviceId"],
            "DeviceType": self.__sensor_config["deviceType"],
            "DeviceName": self.__sensor_config["deviceName"],
            "DeviceDescription": self.__sensor_config["deviceDescription"],
            "DataType": self.__sensor_config["dataType"],
            "DataDetail": self.__sensor_id,
            "DataSource": self.__cloud_config["deviceSource"],
            "Location": self.__sensor_config["location"]
        }
        if not is_complex:
            payload["DataValue"] = simple_data["value"]
        else:
            payload["VendorData"] = {}
            if type(simple_data["value"]) == list:
                for idx in range(len(simple_data["value"])):
                    payload["VendorData"]["Value_{}".format(idx+1)] = simple_data["value"][idx]
            elif type(simple_data["value"]) == dict:
                for key in simple_data["value"]:
                    if not key == "values":
                        payload["VendorData"][key] = simple_data["value"][key]
        return payload

    def __push_packet_to_cloud(self, payload):
        """
        :param payload:
        :return:
        """
        try:
            header = {
                "Authorization": "SharedAccessSignature sr={}&sig={}&se={}&skn={}".format(
                    self.__cloud_config["URI"],
                    self.__cloud_config["connection"],
                    self.__cloud_config["expiry"],
                    self.__cloud_config["policy"]),
                "Content-Type": "application/json",
                "Content-Length": str(len(json.dumps(payload)))
            }
            URL = self.__cloud_config["URL"]
            request_response = requests.post(URL, data=json.dumps(payload), headers=header)
            if not request_response.ok:
                raise Exception("Response is not OK: Code = {}".format(str(request_response.status_code)))
            else:
                self.__log.info("Cloud Response OK")
                return True
        except:
            trace = traceback.format_exc()
            self.__log.error(trace)
            return False

    def push_local_to_cloud(self, payload):
        return self.__push_packet_to_cloud(payload)
  

    def create_and_push_to_cloud(self, payload, is_complex=False):
        try:
            payload = self.__create_data_payload(payload, is_complex)
            push_result = self.__push_packet_to_cloud(payload)
            return push_result
            # threading.Thread(target=self.__push_packet_to_cloud, args=(payload,)).start()
            # return True
        except:
            err_msg = traceback.format_exc()
            self.__log.error(err_msg)
            return False

    def create_data_payload_to_save(self, payload, is_complex=False):
        try:
            payload = self.__create_data_payload(payload, is_complex)
            return payload
        except:
            err_msg = traceback.format_exc()
            self.__log.error(err_msg)
            return False


    def __repr__(self):
        print("Push to cloud: " + str(self.__sensor_id))