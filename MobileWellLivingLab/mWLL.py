import logging
from logging.handlers import RotatingFileHandler
import mWLLUtilities
from Sensors import *
# from Sensors.ParticleMonitor import GroveCO2
# from Sensors.ParticleMonitor import Dylos
# from Sensors.Environmental import TempPresHum
# from Sensors.Audio import AudioRecorder
# from Sensors.Light import NanoLambda
# from Sensors.Camera import FLIRLepton
import os
import sys
import time
import traceback


if __name__ == "__main__":
    logging.warn("nStarting mWLL!")
    os.chdir(os.path.dirname(sys.argv[0]))
    # read master configuration file
    master_config = mWLLUtilities.read_config_as_json("./Configuration/MasterConfig.json")
    master_config["loggerId"] = master_config["DeviceId"]
    master_config["cwd"] = os.getcwd()
    log = logging.Logger(master_config["loggerId"])
    log.setLevel(logging.DEBUG)
    # fh = logging.FileHandler(master_config["cwd"] + master_config["logfile"])
    fh = RotatingFileHandler(master_config["cwd"] + master_config["logfile"], mode='a', maxBytes=250*1024, backupCount=20)
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)
    log.addHandler(fh)
    log.info("\n\n *** Logger configured! Starting mWLL *** \n\n")
    master_config["logger"] = log

    # Start all the sensors mentioned in the master configuration
    sensor_instances = []
    sensor_list = master_config["Sensors"]
    for sensor in sensor_list:
        klass = globals()[sensor["ClassName"]]
        try:
            instance = klass(master_config,sensor["ConfigLocation"], sensor["SensorId"])
            if instance.start_sensor() == True:
                sensor_instances.append(instance)
        except:
            continue
    
    log.info("Started sensors!")
    print("\n\n****Started sensors!****\n\n")
    keep_iterating = True
    with open(master_config["cwd"] + master_config["stopFile"], "w") as f:
        f.write("no")

    print("\n\nStarting file iteration\n\n")
    while keep_iterating:
        print("\n\n*** ITERATION!! ***\n\n")
        with open(master_config["cwd"] + master_config["stopFile"], "r") as f:
            file_data = f.read()
        if "yes" in file_data:
            log.info("Stop file has a yes! stopping everything")
            print("\n\nSTOP!!")
            try:
                # Stop all the sensors 
                for sensor_instance in sensor_instances:
                    sensor_instance.stop_sensor()
                log.info("Stopping done! Exiting mWLL!")
                print("Bye!!")
            except:
                err_msg = traceback.format_exc()
                log.error(err_msg + "\nExiting mWLL.")
                print("ugh! whatever!")
            keep_iterating = False
            exit(0)
        else:
            time.sleep(60)

