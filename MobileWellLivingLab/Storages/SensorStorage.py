import os
import traceback
import wave
import time
from collections import deque
import json
import mWLLUtilities
import uuid
from PushToCloud import PushToCloud
from Storages import Storage


class LowFrequencyStorage(Storage.GenericStorage):
    def push_to_cloud(self):
        super(LowFrequencyStorage, self).push_to_cloud()
#        print("push to cloud called")        
        payload = {"timestamp": self.__last_value[0], "value": self.__last_value[1]}
        try:
            if type(self.__last_value[1]) == str:
                is_complex = False
            elif type(self.__last_value[1]) == list or type(self.__last_value[1]) == dict:
                is_complex = True
            else:
                is_complex = None
                raise Exception("The data values are not recognized. Data Type: {}"
                                .format(type(self.__last_value[1])))
            push_success = True
            filename = time.strftime("%Y%m%d-%H%M%S") +"-"+str(uuid.uuid4()) + ".json"
            isInternetAvailable = mWLLUtilities.check_internet()
            if isInternetAvailable:
                push_success = self.__cloud_var.create_and_push_to_cloud(payload, is_complex)
                #internet available so lets try to check and upload few offline files
                if push_success:
                    self.upload_files()
            else:
                self.__log.warning("No Internet connectivity detected. Saving payload to disk.")
                data_to_write = self.__cloud_var.create_data_payload_to_save(payload, is_complex)
                if not os.path.exists(self.__folder_to_write):
                    os.makedirs(self.__folder_to_write)
                with open(self.__folder_to_write + filename, "w") as f:
                    json.dump(data_to_write,f)
                    
            # date_file = self.__last_value[0].split(" ")[0]
            
            return push_success
        except:
            err_msg = traceback.format_exc()
            self.__log.error(err_msg)
            return False

    def push_to_process(self):
        super(LowFrequencyStorage, self).push_to_process()
        return

    def upload_files(self):
        self.__log.info("Checking and uploading any data files for {}".format(self.__sensor_id))
        upload_success = False
        if mWLLUtilities.check_internet():
            filesUploaded = 0
            max_files_upload = int(self.__sensor_config["maxFilesUpload"])
            for file in os.listdir(self.__folder_to_write):
                if (filesUploaded < max_files_upload) == True:
                    if file.endswith(".json"):
                        
                        file_to_open = self.__folder_to_write + file
                        if os.path.getsize(file_to_open) > 0:
                            try:
                               #Only process if file is NOT empty - otherwise json reader throws exception 
                                with open(file_to_open,"r") as read_file:
                                    #print("Opening the file to upload"+file_to_open)
                                    #self.__log.info("Filename {}".format(file_to_open))
                                    payload = json.load(read_file)
                                    push_success = self.__cloud_var.push_local_to_cloud(payload)
                                    upload_success = True
                                    if (push_success):
                                        read_file.close()
                                        os.remove(file_to_open)
                                        filesUploaded += 1
                                    else:
                                        self.__log.warning("Could not push value to cloud, Aborting local file uploads")
                                        upload_success = False
                                        break
                            #If some error in reading file in json format, log error message,
                            #delete file- so it does not continue throwing errors - then continue
                            except: 
                                err_msg = traceback.format_exc()
                                self.__log.error(err_msg)
                                os.remove(file_to_open)
                                continue
                        else: #if file is somehow 0 bytes (or less) delete it so it does not throw exceptions
                            os.remove(file_to_open)
                            
                else:
                    break
        if upload_success == True:
            self.__log.info("Found and successfully uploaded files for {}".format(self.__sensor_id))
                    

    def write_to_disk(self):
        """
        Write the last_value to disk
        :return: True if the writing was successful, otherwise False
        """
        super(LowFrequencyStorage, self).write_to_disk()
        try:
            # check to see if the folder does not exist, create one
            if not os.path.exists(self.__folder_to_write):
                os.makedirs(self.__folder_to_write)
            if type(self.__last_value[1]) == str:
                to_write = "{},{}\n".format(self.__last_value[0], self.__last_value[1])
            elif type(self.__last_value[1]) == list:
                sensor_values = ",".join(self.__last_value[1])
                to_write = "{},{}\n".format(self.__last_value[0], sensor_values)
            elif type(self.__last_value[1]) == dict:
                if "values" not in self.__last_value[1]:
                    return True
                sensor_values = ",".join(self.__last_value[1]["values"])
                to_write = "{},{}\n".format(self.__last_value[0], sensor_values)
            else:
                raise Exception("The data values are not a recognized type. Data Type: {}"
                                .format(type(self.__last_value[1])))
            date_file = self.__last_value[0].split(" ")[0]
            with open(self.__folder_to_write + date_file + ".csv", "a") as f:
                f.write(to_write)
            self.__log.info("{} OK".format(self.__sensor_id))
            return True
        except:
            err_msg = traceback.format_exc()
            self.__log.error(err_msg)
            return False

    def push(self, data):
        """
        Push the data for writing, and push the data to the cloud
        :param data: Tuple with (timestamp, data) format, data can be a string or a list of strings, or a dict with the
        ordered values in a list of string with key "values" and the remaining key-value pairs representing the actual
        value and keys.
        """
        super(LowFrequencyStorage, self).push(data)
        self.__last_value = data
        push_result = self.push_to_cloud()
        if not push_result:
            self.__log.warning("Could not push value to cloud, writing to disk")
            # self.write_to_disk()
        # self.write_to_disk()
        # self.push_to_cloud()

    def initialize_storage(self):
        super(LowFrequencyStorage, self).initialize_storage()
        self.__folder_to_write = self.__master_config["cwd"] + self.__master_config["storage"] + self.__sensor_id + "/"
        self.__cloud_var = PushToCloud(self.__master_config, self.__sensor_config, self.__sensor_id)
        self.__last_value = None
        self.__log.info("Storage initialization done for {}".format(self.__sensor_id))
        # self.upload_files()

    def __init__(self, master_config, sensor_config, sensor_id):
        self.__master_config = master_config
        self.__sensor_config = sensor_config
        self.__sensor_id = sensor_id
        self.__log = mWLLUtilities.CustomLog(self.__master_config["logger"], self.__sensor_id + "." + __name__)
        # self.__checkconnection = mWLLUtilities.check_connection()
        # self.__log = self.__master_config["logger"]
        self.__log.info("init LowFrequencyStorage for {}, initializing variables".format(self.__sensor_id))
        self.__folder_to_write = None
        self.__last_value = None
        self.__cloud_var = None
        self.initialize_storage()


class HighFrequencyStorage(Storage.GenericStorage):
    # TODO

    def initialize_storage(self):
        super(HighFrequencyStorage, self).initialize_storage()

    def push_to_cloud(self):
        super(HighFrequencyStorage, self).push_to_cloud()

    def push(self, data):
        super(HighFrequencyStorage, self).push(data)

    def write_to_disk(self):
        super(HighFrequencyStorage, self).write_to_disk()

    def push_to_process(self):
        super(HighFrequencyStorage, self).push_to_process()

    def __init__(self):
        pass


class ImageStorage(Storage.GenericStorage):
    """
    This is what DevTest/WriteLeptonImage.py will become
    """
    def initialize_storage(self):
        super(ImageStorage, self).initialize_storage()
        raise NotImplementedError

    def push_to_cloud(self):
        super(ImageStorage, self).push_to_cloud()
        raise NotImplementedError

    def push(self, data):
        super(ImageStorage, self).push(data)
        raise NotImplementedError

    def write_to_disk(self):
        super(ImageStorage, self).write_to_disk()
        raise NotImplementedError

    def push_to_process(self):
        super(ImageStorage, self).push_to_process()
        raise NotImplementedError

    def __init__(self):
        pass
