"""
Canary LIB
-------------------

Based on code by hbldh <henrik.blidh@nedomkull.com>

"""
import shutil
import platform
import asyncio
import logging
import json
import numpy as np
from pathlib import Path
import qasync
import cbor2
import binascii
from random import random
from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic
from array import array

import struct
import time, sys

import os

logger = logging.getLogger(__name__)

CurrentTimeServiceUuidString = "00001805-0000-1000-8000-00805f9b34fb"
CurrentTimeCharacteristicUuidString = "00002a2b-0000-1000-8000-00805f9b34fb"

CommandServiceUUIDString = "0bb52dda-d431-40cc-8a41-a666a25254b6"
commandCharacteristicUUIDString = "ac7bf687-7a30-4336-a6f6-b8030930854d"

DataServiceUUIDString = "bf289137-78a3-4c60-b381-25558e78e252"
DataCharacteristicUUIDString = "b5d1f9be-b0bb-4059-9cb7-c2fffd184770"

DeviceInformationServiceUuidString = "0000180A-0000-1000-8000-00805f9b34fb"
FirmwareRevisionCharacteristicUuidString = "00002A26-0000-1000-8000-00805f9b34fb"
HardwareRevisionCharacteristicUuidString = "00002A27-0000-1000-8000-00805f9b34fb"
SerialNumberCharacteristicUuidString = "00002A25-0000-1000-8000-00805f9b34fb"

TestingServiceUUIDString = "53cdde50-a736-4793-a0dd-a818fbbd3fd0"
TestingCharacteristicUUIDString = "54f5aab5-5ebf-40b1-a819-e49bf3024048"

PacketsExpected = 0
PacketsArrived = 0
DataBytesExpected = 0
DataBytesArrived = 0
DataBuffer = bytearray()
MetaDataBuffer = bytearray()
DataNotificationState = 0

serial_number = 0
hw_revision = 0
fw_revision = 0

meta_sensor_id = 0
meta_temp_avg = 0
meta_sampling_freq = 0
meta_timestamp = 0
meta_num_of_samples = 0
meta_overrun = 0
meta_channel = 0
meta_data_format = 0
meta_data_unit = 0
meta_scale = 0

data_received_event = asyncio.Event()
all_data_received = False

verbose = True
mac_addr = ""
output_path = None

data_units = {
    0: "g",
    1: "milli-Gauss",
    2: "Celsius"
}

data_format = {
    0: "fp16",
    1: "int16"
}

data_channel = {
    0: "Acceleration_X",
    1: "Acceleration_Y",
    2: "Acceleration_Z",
    3: "Magnetic_X",
    4: "Magnetic_Y",
    5: "Magnetic_Z",
    6: "Temperature",
    7: "Ambient_Temperature",
}

sensor_id_map = {
    0: "iis3dwb",
    1: "magnetic",
    2: "tmp1075",
    3: "nrf52840",
}


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    CBLACK = '\33[30m'
    CRED = '\33[31m'
    CGREEN = '\33[32m'
    CYELLOW = '\33[33m'
    CBLUE = '\33[34m'
    CVIOLET = '\33[35m'
    CBEIGE = '\33[36m'
    CWHITE = '\33[37m'

    CBLACKBG = '\33[40m'
    CREDBG = '\33[41m'
    CGREENBG = '\33[42m'
    CYELLOWBG = '\33[43m'
    CBLUEBG = '\33[44m'
    CVIOLETBG = '\33[45m'
    CBEIGEBG = '\33[46m'
    CWHITEBG = '\33[47m'

    CGREY = '\33[90m'
    CRED2 = '\33[91m'
    CGREEN2 = '\33[92m'
    CYELLOW2 = '\33[93m'
    CBLUE2 = '\33[94m'
    CVIOLET2 = '\33[95m'
    CBEIGE2 = '\33[96m'
    CWHITE2 = '\33[97m'

    CGREYBG = '\33[100m'
    CREDBG2 = '\33[101m'
    CGREENBG2 = '\33[102m'
    CYELLOWBG2 = '\33[103m'
    CBLUEBG2 = '\33[104m'
    CVIOLETBG2 = '\33[105m'
    CBEIGEBG2 = '\33[106m'
    CWHITEBG2 = '\33[107m'


class sensors:
    SENSOR_IIS3DWB = 0
    SENSOR_MAGNETIC = 1
    SENSOR_TMP1075 = 2
    SENSOR_TMP_AMBIENT = 3
    ALL = 99


def drawProgressBar(percent, barLen=20):
    global verbose
    if verbose:
        sys.stdout.write("\r")
        progress = ""
        for i in range(barLen):
            if i < int(barLen * percent):
                progress += "="
            else:
                progress += " "
        sys.stdout.write("[ %s ] %.2f%%" % (progress, percent * 100))
        sys.stdout.flush()


def print_color(string, color=bcolors.CWHITE):
    global verbose
    if verbose:
        print(color + string + bcolors.ENDC)


def print_err(string):
    global verbose
    if verbose:
        print("\n")
        print(bcolors.FAIL + "Error: " + string + bcolors.ENDC)


def to_hex(bytes_date):
    hex_data = ','.join(format(x, '02X') for x in bytes_date)
    return hex_data


async def waiter(event):
    await event.wait()


def command_notification_handler(sender, data):
    global data_received_event
    #print("get somthing - > data_notification_handler ")
    """
    Simple notification handler which prints the data received.
    """
    logger.info("Notify {0}: {1}".format(sender, to_hex(data)))
    data_received_event.set()


def testing_notification_handler(_sender, data):
    global all_data_received
    global PacketsExpected
    global PacketsArrived
    global DataBytesExpected
    global DataBytesArrived
    global DataBuffer
    print("get somthing - > data_notification_handler ")
    PacketsArrived += 1
    logger.info("testing_notification_handler")
    if PacketsArrived == 1:
        data_as_json = cbor2.loads(binascii.a2b_hex(data.hex()))
        logger.info(json.dumps(data_as_json, indent=4, sort_keys=True))
        DataBytesExpected = data_as_json["len"]
        logger.info("DataBytesExpected={}".format(DataBytesExpected))
        DataBuffer.clear()
        DataBytesArrived = 0
        logger.info(data_as_json)
    else:
        DataBytesArrived += len(data)
        DataBuffer += data
        if DataBytesExpected == DataBytesArrived:
            all_data_received = True


def data_notification_handler(_sender, data):
    global DataBytesExpected
    global DataBuffer
    global MetaDataBuffer
    global data_received_event
    global all_data_received
    global DataNotificationState
    global meta_sensor_id, meta_temp_avg, meta_sampling_freq, meta_timestamp, meta_num_of_samples, meta_overrun, meta_channel, meta_data_format, meta_data_unit, meta_scale


    #print("get somthing - > data_notification_handler !!!!  ")
    if DataNotificationState == 0:  # meta header
        DataNotificationState = 1
        data_as_json = cbor2.loads(binascii.a2b_hex(data.hex()))
        DataBytesExpected = data_as_json["len"]
        DataType = data_as_json["typ"]

        logger.info("DataBytesExpected: {0}".format(DataBytesExpected))
        logger.info("DataType: {0}".format(DataType))

        MetaDataBuffer.clear()

        if DataBytesExpected == 0:
            all_data_received = True
            logger.error("no data available")

    elif DataNotificationState == 1:  # meta-data

        MetaDataBuffer += data

        if len(MetaDataBuffer) == DataBytesExpected:
            DataNotificationState = 2
            meta_data_as_json = cbor2.loads(binascii.a2b_hex(data.hex()))
            meta_sensor_id = meta_data_as_json["sid"]
            meta_temp_avg = meta_data_as_json["tmp"]
            meta_sampling_freq = meta_data_as_json["frq"]
            meta_timestamp = meta_data_as_json["tsp"]
            meta_num_of_samples = meta_data_as_json["num"]
            meta_overrun = meta_data_as_json["ovr"]
            meta_channel = meta_data_as_json["ch"]
            meta_data_format = meta_data_as_json["fmt"]
            meta_data_unit = meta_data_as_json["unt"]
            meta_scale = meta_data_as_json["scl"]

    elif DataNotificationState == 2:  # data-header
        DataNotificationState = 3

        data_as_json = cbor2.loads(binascii.a2b_hex(data.hex()))
        DataBytesExpected = data_as_json["len"]
        DataType = data_as_json["typ"]

        logger.info("DataBytesExpected: {0}".format(DataBytesExpected))
        logger.info("DataType: {0}".format(DataType))

        DataBuffer.clear()

    elif DataNotificationState == 3:  # data
        for x in data:
            DataBuffer.append(x)

        if DataBytesExpected:
            drawProgressBar(len(DataBuffer) / DataBytesExpected, 100)

        if len(DataBuffer) == DataBytesExpected:
            DataNotificationState = 4
            print('')

            logger.info("All data was received successfully!!! ({0} Bytes)".format(len(DataBuffer)))
            parse_data(DataBuffer)


def parse_data(data):
    global all_data_received
    global mac_addr
    global hw_revision
    global fw_revision
    global output_path
    global serial_number

    logger.info("Parsing data ...")

    data_vector = []

    sample_size = 2
    logger.info("num_of_samples: {0}".format(meta_num_of_samples))

    for i in range(meta_num_of_samples):
        x_tuple = struct.unpack_from('h', data, (i * sample_size))
        x = x_tuple[0]
        data_vector.append(x)


    sensitivity = meta_scale

    if data_channel[meta_channel] == "Acceleration_X" or data_channel[meta_channel] == "Acceleration_Y" or data_channel[
        meta_channel] == "Acceleration_Z":

        print(hw_revision)
        print(type(hw_revision))
        try :
            if "apus_alpha" in hw_revision:
                sensor_id = "ads8866-ADXL1002-50_1"
                scaling_factor = 0.0019073486328125
            else:
                sensor_id = "iis3dwb"
                scaling_factor = float(sensitivity) / 2.0 ** 15 / np.sqrt(2)
        except:
            sensor_id = "iis3dwb"
            scaling_factor = float(sensitivity) / 2.0 ** 15 / np.sqrt(2)

    elif data_channel[meta_channel] == "Magnetic_X" or data_channel[meta_channel] == "Magnetic_Y" or data_channel[
        meta_channel] == "Magnetic_Z":
        if ("apus_alpha" in hw_revision) or ("halo_ep2" in hw_revision):
            sensor_id = "ads8866-HONEYWELL_SS495A"
            scaling_factor = 0.0244140625
        if ("canary_proto_rev_3" in hw_revision) or (("canary_proto_rev_4" in hw_revision) and ("fxos" in hw_revision)):
            sensor_id = "fxos8700"
            scaling_factor = 0.001
        elif (("canary_proto_rev_4" in hw_revision) or ("canary_ea00019.rev_a" in hw_revision)) and (
                "lis3" in hw_revision):
            sensor_id = "lis3mdl"
            scaling_factor = 1.0 / 2281
        else:
            sensor_id = "unknown"
            scaling_factor = 1
    elif data_channel[meta_channel] == "Temperature":
        if ("apus_alpha" in hw_revision) or ("halo_ep2" in hw_revision):
            scaling_factor = 1
            sensor_id = "NCP15WB473F03RC"
        if ("canary_proto_rev_3" in hw_revision):
            scaling_factor = 0.0625
            sensor_id = "tmp1075"
        elif ("canary_proto_rev_4" in hw_revision) or ("canary_ea00019.rev_a" in hw_revision):
            scaling_factor = 1
            sensor_id = "iis3dwb"
        else:
            scaling_factor = np.NaN
            sensor_id = "unknown"
    elif data_channel[meta_channel] == "Ambient_Temperature":
        scaling_factor = 1
        sensor_id = "nrf52840"
    else:
        logger.error("unknown data_channel")

    # JSON
    json_data = {}
    json_data['Serial_Number'] = serial_number
    json_data['HW_Version'] = hw_revision
    json_data['FW_Version'] = fw_revision
    json_data['Sensor_ID'] = sensor_id
    json_data['Data_Channel'] = data_channel[meta_channel]
    json_data['Data_Format'] = data_format[meta_data_format]
    json_data['Data_Unit'] = data_units[meta_data_unit]
    json_data['Sampling_Frequency'] = meta_sampling_freq
    json_data['Sensitivity'] = meta_scale
    json_data['Scaling_Factor'] = scaling_factor
    json_data['Timestamp_utc'] = meta_timestamp
    json_data['Sensor_Temperature'] = meta_temp_avg
    json_data['Overflow'] = meta_overrun
    json_data['Calibration_Vector'] = 'TBD'
    json_data['Num_Of_Samples'] = meta_num_of_samples
    json_data['Data'] = data_vector

    if os.name == "nt":
        # in windows, ":" is not allowed
        mac_str = mac_addr.replace(':', '.')
    else:
        mac_str = mac_addr
    filename = '{}_{}_{}_{}_{}.json'.format(str(hw_revision),
                                            mac_str,
                                            str(meta_timestamp),
                                            str(meta_sensor_id),
                                            str(meta_channel))
    path = output_path

    print(path)
    print(filename)
    print(hw_revision)
    print("try to write to file")
    try:
        f = open("{path}/{filename}".format(path=path, filename=filename), "x")
    except Exception as e:
        logger.error(str(e))
        return

    with open("{path}/{filename}".format(path=path, filename=filename), 'w') as outfile:
        json.dump(json_data, outfile)
    f.close()
    logger.info("Output file created successfully: " + filename)
    logger.info("Put the last sample in the file    !!!!!!!!!!!!!!!! ")
    print(data_received_event.is_set())
    print(data_received_event)
    data_received_event.set()
    all_data_received = True

async def run_service_explorer(device, address, loop, debug=False):
    log = logging.getLogger(__name__)
    if debug:
        loop.set_debug(True)
        log.setLevel(logging.DEBUG)
        h = logging.StreamHandler(sys.stdout)
        h.setLevel(logging.DEBUG)
        log.addHandler(h)

    async with BleakClient(address, device=device, loop=loop) as client:
        x = await client.is_connected()
        logger.info("Connected: {0}".format(x))

        for service in client.services:
            logger.info("[Service] {0}: {1}".format(service.uuid, service.description))
            for char in service.characteristics:
                if "read" in char.properties:
                    try:
                        _value = bytes(await client.read_gatt_char(char.uuid))
                    except Exception as e:
                        _value = str(e).encode()
                else:
                    _value = None

                logger.info(
                    "\t[Characteristic] {0}: ({1}) | Name: {2}, Value: {3} ".format(
                        char.uuid, ",".join(char.properties), char.description, _value
                    )
                )
                for descriptor in char.descriptors:
                    _value = await client.read_gatt_descriptor(descriptor.handle)

                    logger.info(
                        "\t\t[Descriptor] {0}: (Handle: {1}) | Value: {2} ".format(
                            descriptor.uuid, descriptor.handle, bytes(_value)
                        )
                    )


async def run_read_cts(device, address, loop, debug=False):
    global CurrentTimeServiceUuidString, CurrentTimeCharacteristicUuidString

    log = logging.getLogger(__name__)
    if debug:
        loop.set_debug(True)
        log.setLevel(logging.DEBUG)
        h = logging.StreamHandler(sys.stdout)
        h.setLevel(logging.DEBUG)
        log.addHandler(h)

    async with BleakClient(address, device=device, loop=loop) as client:
        x = await client.is_connected()
        logger.info("Connected: {0}".format(x))

        logger.info("[Service CTS          ] {0}: {1}".format(CurrentTimeServiceUuidString, "CTS"))
        logger.info("[Characteristic CTS   ] {0}: {1}".format(CurrentTimeCharacteristicUuidString, "CTS"))

        try:
            _value = bytes(await client.read_gatt_char(CurrentTimeCharacteristicUuidString))
        except Exception as e:
            _value = str(e).encode()

        logger.info("[Characteristic CTS   ] Read Value: {0} ".format(to_hex(_value)))


async def run_sample(device,
                     address,
                     loop,
                     sensor_id,
                     odr,
                     scale,
                     duration ='4' ,
                     sample_delay=0,
                     _verbose=True,
                     path=None,
                     return_sample_at_ts=False,
                     clear_fs=True):
    global CurrentTimeServiceUuidString, CurrentTimeCharacteristicUuidString
    global CommandServiceUUIDString, commandCharacteristicUUIDString
    global data_received_event
    global verbose
    global mac_addr
    global output_path

    verbose = _verbose
    if verbose:
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    mac_addr = address
    output_path = path

    logger.info("[Service CTS          ] {0}: {1}".format(CurrentTimeServiceUuidString, "CTS"))
    logger.info("[Characteristic CTS   ] {0}: {1}".format(CurrentTimeCharacteristicUuidString, "CTS"))

    milliseconds_since_epoch = (round(time.time() * 1000))
    write_data = bytearray(struct.pack('q', milliseconds_since_epoch))

    logger.info("Sending Set-Time command to EP (CT={0})".format(milliseconds_since_epoch))

    try:
        _value = bytes(await device.write_gatt_char(CurrentTimeCharacteristicUuidString, write_data))
    except Exception as e:
        _value = str(e).encode()

    logger.info("[Characteristic CTS   ] Write Value: {0} ".format(to_hex(write_data)))

    logger.info("[Service Command          ] {0}: {1}".format(CommandServiceUUIDString, "Command"))
    logger.info("[Characteristic Command   ] {0}: {1}".format(commandCharacteristicUUIDString, "Command"))


    command_id = 2  # Delete all files command
    logger.info("======== Delete all samples request ========")
    write_data = bytearray(struct.pack('=H', command_id))

    logger.info("Sending Delete all samples request command to EP (command_id={0})".format(command_id))

    try:
        _value = await device.write_gatt_char(commandCharacteristicUUIDString, write_data)
    except Exception as e:
        _value = str(e).encode()
    logger.info("[Characteristic Command   ] Write Value: {0} ".format(to_hex(write_data)))

    time.sleep(100)
    # logger.info("=========start Sample from here - original code only - connect is ok  =========")
    # logger.info("[Service CTS          ] {0}: {1}".format(CurrentTimeServiceUuidString, "CTS"))
    # logger.info("[Characteristic CTS   ] {0}: {1}".format(CurrentTimeCharacteristicUuidString, "CTS"))
    #
    # milliseconds_since_epoch = (round(time.time() * 1000))
    # write_data = bytearray(struct.pack('q', milliseconds_since_epoch))
    #
    # logger.info("Sending Set-Time command to EP (CT={0})".format(milliseconds_since_epoch))

    try:
        _value = bytes(await device.write_gatt_char(CurrentTimeCharacteristicUuidString, write_data))
    except Exception as e:
        _value = str(e).encode()

    logger.info("[Characteristic CTS   ] Write Value: {0} ".format(to_hex(write_data)))

    print(f'out put path :  {output_path}')
    client = BleakClient(address, device=device, loop=loop)
    err = ""
    connected = False
    conn_timeout = 10
    milliseconds_since_epoch = (round(time.time() * 1000))
    write_data = bytearray(struct.pack('q', milliseconds_since_epoch))
    logger.info("Sending Set-Time command to EP (CT={0})".format(milliseconds_since_epoch))

    try:
        _value = bytes(await device.write_gatt_char(CurrentTimeServiceUuidString, write_data))
        print("write")
    except Exception as e:
        _value = str(e).encode()

    #data_to_send - >  [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    command_id = 2  # Delete all files command
    logger.info("======== Delete all samples request ========")
    write_data = bytearray(struct.pack('=HHHHHI', command_id ,0 ,0 ,0 ,0 ,0 ))
    try:
        # client & device -> send
        logger.info("[Characteristic Command   ] Write Value: {0} ".format(to_hex(write_data)))
        logger.info("[Characteristic Command   ] Write Value: {0} ".format(write_data))
        _value = await device.write_gatt_char(commandCharacteristicUUIDString, write_data)

    except :
        print("somthin happen")

    write_data = bytearray(struct.pack('=HHHHHI', command_id, 0, 0, 0, 0, 0))
    try:
        # client & device -> send
        logger.info("[Characteristic Command   ] Write Value: {0} ".format(to_hex(write_data)))
        logger.info("[Characteristic Command   ] Write Value: {0} ".format(write_data))
        _value = await device.write_gatt_char(commandCharacteristicUUIDString, write_data)


    except:
        print("somthin happen")

    write_data = bytearray(struct.pack('=HHHHHI', 0, 0, 0, 0, 0, command_id))
    try:
        # client & device -> send
        logger.info("[Characteristic Command   ] Write Value: {0} ".format(to_hex(write_data)))
        logger.info("[Characteristic Command   ] Write Value: {0} ".format(write_data))
        _value = await device.write_gatt_char(commandCharacteristicUUIDString, write_data)

    except:
        print("somthin happen")

    write_data = bytearray(struct.pack('=bbbbbbb', command_id, 0, 0, 0, 0, 0, 0 ))
    try:
        # client & device -> send
        logger.info("[Characteristic Command   ] Write Value: {0} ".format(to_hex(write_data)))
        logger.info("[Characteristic Command   ] Write Value: {0} ".format(write_data))
        _value = await device.write_gatt_char(commandCharacteristicUUIDString, write_data)

    except:
        print("somthin happen")
    # this is the pack 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    logger.info("Sending Delete all samples request command to EP (command_id={0})".format(command_id))

    write_data = bytearray(struct.pack('=bbbbbbb',  0, 0, 0, 0, 0, 0,command_id ))
    try:
        # client & device -> send
        logger.info("[Characteristic Command   ] Write Value: {0} ".format(to_hex(write_data)))
        logger.info("[Characteristic Command   ] Write Value: {0} ".format(write_data))
        _value = await device.write_gatt_char(commandCharacteristicUUIDString, write_data)

    except:
        print("somthin happen")
    # this is the pack 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    logger.info("Sending Delete all samples request command to EP (command_id={0})".format(command_id))

    write_data = bytearray(struct.pack('=H', command_id))
    try:
        # client & device -> send
        logger.info("[Characteristic Command   ] Write Value: {0} ".format(to_hex(write_data)))
        logger.info("[Characteristic Command   ] Write Value: {0} ".format(write_data))

        print("1")
        _value = await client.write_gatt_char(commandCharacteristicUUIDString, write_data)
        print("2")
        _value = await client.write_gatt_char(DataServiceUUIDString, write_data)
        print("3")
        _value = await client.write_gatt_char(DataCharacteristicUUIDString, write_data)

        logger.info("[Characteristic Command   ] Write Value: {0} ".format(to_hex(write_data)))
        _value = await device.write_gatt_char(commandCharacteristicUUIDString, write_data)


        logger.info("[Characteristic Command   ] Write Value: {0} ".format(write_data))
        _value = await client.write_gatt_char(commandCharacteristicUUIDString, write_data)

        logger.info("[Characteristic Command   ] Write Value: {0} ".format(to_hex(write_data)))
        _value = await device.write_gatt_char(commandCharacteristicUUIDString, write_data)

        logger.info("[Characteristic Command   ] Write Value: {0} ".format(to_hex(write_data)))
        _value = await client.write_gatt_char(CommandServiceUUIDString, write_data)

        logger.info("[Characteristic Command   ] Write Value: {0} ".format(to_hex(write_data)))
        _value = await device.write_gatt_char(CommandServiceUUIDString, write_data)


        # delete all the Sam[ple
        command_id = 2  # Delete all files command
        logger.info("======== Delete all samples request ========")
        write_data = bytearray(struct.pack('=H', command_id))
        logger.info("Sending Delete all samples request command to EP (command_id={0})".format(command_id))

        try:
            _value = await client.write_gatt_char(commandCharacteristicUUIDString, write_data)
        except Exception as e:
            _value = str(e).encode()


        command_id = 2  # Delete all files command
        logger.info("======== Delete all samples request ========")
        write_data = bytearray(struct.pack('=b', command_id))
        logger.info("Sending Delete all samples request command to EP (command_id={0})".format(command_id))

        try:
            _value = await client.write_gatt_char(commandCharacteristicUUIDString, write_data)
        except Exception as e:
            _value = str(e).encode()



        logger.info("[Characteristic Command   ] Write Value: {0} ".format(to_hex(write_data)))
        print("11111111111111111")
        write_data = bytearray([2,0,0,0,0,0,0,0,0,0,0,0,0,0])
        print(write_data)
        print(to_hex(write_data))
        print("----------------------------------")
        try:
            _value = await client.write_gatt_char(commandCharacteristicUUIDString, write_data)
        except Exception as e:
            _value = str(e).encode()
        logger.info("[Characteristic Command   ] Write Value: {0} ".format(to_hex(write_data)))

        print("222222222222222")
        write_data = bytearray([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2])
        print(write_data)
        print(to_hex(write_data))
        print("----------------------------------")
        try:
            _value = await client.write_gatt_char(commandCharacteristicUUIDString, write_data)
        except Exception as e:
            _value = str(e).encode()
        logger.info("[Characteristic Command   ] Write Value: {0} ".format(to_hex(write_data)))

        write_data = bytearray(struct.pack('=hhhhhhhhhhhhhh', command_id , 0,0,0,0,0,0,0,0,0,0,0,0))
        print(write_data)
        print(to_hex(write_data))
        print("----------------------------------")
        try:
            _value = await client.write_gatt_char(commandCharacteristicUUIDString, write_data)
        except Exception as e:
            _value = str(e).encode()
        logger.info("[Characteristic Command   ] Write Value: {0} ".format(to_hex(write_data)))




    except Exception as e:
        _value = str(e).encode()
    logger.info("[Characteristic Command   ] Write Value: {0} ".format(to_hex(write_data)))

    milliseconds_since_epoch = (round(time.time() * 1000))
    write_data = bytearray(struct.pack('q', milliseconds_since_epoch))
    logger.info("Sending Set-Time command to EP (CT={0})".format(milliseconds_since_epoch))

    try:
        _value = bytes(await device.write_gatt_char(CurrentTimeServiceUuidString, write_data))
        print("write")
    except Exception as e:
        _value = str(e).encode()

    write_data = bytearray(struct.pack('=bbbbbbbbbbbbbb', command_id, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0))
    print(write_data)
    print(to_hex(write_data))
    print("----------------------------------")
    try:
        _value = await client.write_gatt_char(commandCharacteristicUUIDString, write_data)
    except Exception as e:
        _value = str(e).encode()
    logger.info("[Characteristic Command   ] Write Value: {0} ".format(to_hex(write_data)))

    logger.info("============          Delete Until Here FS          ================")
    time.sleep(100)
    logger.info("============          sample now send          ================")
    command_id = 0  # SampleNow Command
    sample_at_ts = round(time.time()) + sample_delay
    logger.info("======== Sample at: {} [{}] ========".format(
        sample_at_ts, time.strftime('%H-%M-%S', time.localtime(sample_at_ts))))
    write_data = bytearray(struct.pack('=HHHHHI', command_id, 1, odr, scale, 4, sample_at_ts))

    logger.info("Sending Sample-All command to EP (command_id={0} ;"
                "sensor_id={1} ; odr={2} ; scale={3} ; duration={4} ; sample_at_ts={5})".
                format(command_id, sensor_id, odr, scale, duration, sample_at_ts))

    try:
        _value = await client.write_gatt_char(commandCharacteristicUUIDString, write_data)
    except Exception as e:
        _value = str(e).encode()
    logger.info("[Characteristic Command   ] Write Value: {0} ".format(to_hex(write_data)))

    print("to fix again")
        # while not client.is_connected:
        #
        #     print(time.strftime('%H-%M-%S'))
        #
        #     try:
        #         connected = await client.connect(timeout=conn_timeout)
        #
        #     except asyncio.CancelledError:
        #         logger.error("CancelledError - sample")
        #         await client.disconnect()
        #     except Exception as e:
        #         err = str(e)
        #         await client.disconnect()
        #
        # if connected == False:
        #     logger.error('wasn\'t able to connect :( {}'.format(err))
        #     return False
        # else:
        #     logger.info("Connected: {0}".format(connected))
        #     logger.info("[Service CTS          ] {0}: {1}".format(CurrentTimeServiceUuidString, "CTS"))
        #     logger.info("[Characteristic CTS   ] {0}: {1}".format(CurrentTimeCharacteristicUuidString, "CTS"))
        #
        #     milliseconds_since_epoch = (round(time.time() * 1000))
        #     write_data = bytearray(struct.pack('q', milliseconds_since_epoch))
        #     logger.info("Sending Set-Time command to EP (CT={0})".format(milliseconds_since_epoch))
        #
        #     try:
        #         _value = bytes(await client.write_gatt_char(CurrentTimeServiceUuidString, write_data))
        #     except Exception as e:
        #         _value = str(e).encode()
        #
        #     logger.info("[Characteristic CTS   ] Write Value: {0} ".format(to_hex(write_data)))
        #     logger.info("[Service Command          ] {0}: {1}".format(CommandServiceUUIDString, "Command"))
        #     logger.info("[Characteristic Command   ] {0}: {1}".format(commandCharacteristicUUIDString, "Command"))
        #
        #     if clear_fs:
        #         command_id = 2  # Delete all files command
        #         logger.info("======== Delete all samples request ========")
        #         write_data = bytearray(struct.pack('=H', command_id))
        #
        #         logger.info("Sending Delete all samples request command to EP (command_id={0})".format(command_id))
        #
        #         try:
        #             _value = await client.write_gatt_char(commandCharacteristicUUIDString, write_data)
        #         except Exception as e:
        #             _value = str(e).encode()
        #         logger.info("[Characteristic Command   ] Write Value: {0} ".format(to_hex(write_data)))
        #
        #     logger.info("============          sample now send          ================")
        #     command_id = 0  # SampleNow Command
        #     sample_at_ts = round(time.time()) + sample_delay
        #     logger.info("======== Sample at: {} [{}] ========".format(
        #         sample_at_ts, time.strftime('%H-%M-%S', time.localtime(sample_at_ts))))
        #     write_data = bytearray(struct.pack('=HHHHHI', command_id, 1, odr, scale, 4, sample_at_ts))
        #
        #     logger.info("Sending Sample-All command to EP (command_id={0} ;"
        #                 "sensor_id={1} ; odr={2} ; scale={3} ; duration={4} ; sample_at_ts={5})".
        #                 format(command_id, sensor_id, odr, scale, duration, sample_at_ts))
        #
        #     try:
        #         _value = await client.write_gatt_char(commandCharacteristicUUIDString, write_data)
        #     except Exception as e:
        #         _value = str(e).encode()
        #     logger.info("[Characteristic Command   ] Write Value: {0} ".format(to_hex(write_data)))
        #
        #     if return_sample_at_ts:
        #         return True, sample_at_ts
        #     else:
        #         return True
        # except Exception as e:
        #     logger.error(e)
        #     return False
        # finally:
        #     if client.is_connected:
        #         await client.disconnect()
        #     logger.info("DisConnected: {0}".format(not client.is_connected))


async def built_in_self_test(device, address, loop, run_bist=False, _verbose=True, debug=False):
    global CurrentTimeServiceUuidString, CurrentTimeCharacteristicUuidString
    global TestingServiceUUIDString, TestingCharacteristicUUIDString
    global data_received_event
    global all_data_received
    global verbose
    global mac_addr
    global PacketsExpected

    verbose = _verbose
    if verbose:
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    mac_addr = address

    command_id = 0  # SampleNow Command

    logger.info("Connecting to ep...")
    client = BleakClient(address, device=device, loop=loop)
    err = ""
    connected = False
    con_counter = 0
    num_of_tries = 10
    conn_timeout = 10
    try:
        # while connected is False and con_counter < num_of_tries:
        #     con_counter += 1
        #     logger.info("connecting...try...{0}".format(con_counter))
        #     try:
        #         connected = await client.connect(timeout=conn_timeout)
        #     except Exception as e:
        #         err = str(e)
        #         logger.info("Connection fail...retrying...")
        #
        # if connected is False:
        #     logger.error(err)
        #     return False
        # else:
            logger.info("Connected: {0}".format(connected))
            logger.info("[Service CTS          ] {0}: {1}".format(CurrentTimeServiceUuidString, "CTS"))
            logger.info("[Characteristic CTS   ] {0}: {1}".format(CurrentTimeCharacteristicUuidString, "CTS"))

            milliseconds_since_epoch = (round(time.time() * 1000))
            write_data = bytearray(struct.pack('q', milliseconds_since_epoch))

            logger.info("Sending Set-Time command to EP (CT={0})".format(milliseconds_since_epoch))

            try:
                _value = bytes(await client.write_gatt_char(CurrentTimeCharacteristicUuidString, write_data))
            except Exception as e:
                _value = str(e).encode()

            logger.info("[Characteristic CTS   ] Write Value: {0} ".format(to_hex(write_data)))
            logger.info("[Service Command          ] {0}: {1}".format(TestingServiceUUIDString, "Command"))
            logger.info("[Characteristic Command   ] {0}: {1}".format(TestingCharacteristicUUIDString, "Command"))

            await client.start_notify(commandCharacteristicUUIDString, command_notification_handler)

            PacketsExpected = 2
            await client.start_notify(TestingCharacteristicUUIDString, testing_notification_handler)
            if (run_bist):
                write_data = bytearray(b'\x01')
                logger.info("Sending 'run built in self test' command to EP ")

                try:
                    _value = await client.write_gatt_char(TestingCharacteristicUUIDString, write_data)
                except Exception as e:
                    _value = str(e).encode()

                logger.info("[Characteristic Command   ] Write Value: {0} ".format(to_hex(write_data)))
            else:
                write_data = bytearray(b'\x02')
                logger.info("Sending 'get built in self test results' command to EP ")

                try:
                    _value = await client.write_gatt_char(TestingCharacteristicUUIDString, write_data)
                except Exception as e:
                    _value = str(e).encode()

                logger.info("[Characteristic Command   ] Write Value: {0} ".format(to_hex(write_data)))

                while all_data_received is False:
                    data_received_event.clear()
                    data_received_waiter_task = asyncio.create_task(waiter(data_received_event))
                    try:
                        await asyncio.wait_for(data_received_waiter_task, timeout=5)
                    except asyncio.CancelledError:
                        logger.error("CancelledError - BUILT IN SELF TEST")
                    except asyncio.TimeoutError:
                        logger.error("Data receive timeout - BUILT IN SELF TEST")
                        return False

                await client.stop_notify(TestingCharacteristicUUIDString)
                data_as_json = cbor2.loads(binascii.a2b_hex(DataBuffer.hex()))
                logger.info(json.dumps(data_as_json, indent=4, sort_keys=True))

            return True
    except Exception as e:
        logger.error(e)
        return False
    finally:
        logger.info("DisConnected: {0}".format(await client.disconnect()))


def get_acceleration_channels():
    return list(range(3))


def get_magnetic_channels(hw):
    channels = [3, 4, 5]
    if hw == 'hc':
        channels = [5]
    return channels


def get_temp_channel():
    return [6]


def get_ambient_temp_channel(hw):
    if hw == 'c':
        return [7]
    return []


def get_hw_type(hw_revision):
    print(hw_revision)
    if hw_revision.startswith('canary'):
        hw = 'c'
    elif hw_revision.startswith('halo') or hw_revision.startswith('apus'):
        hw = 'hc'
    else:
        # todo : add later
        #raise Exception('Unrecognized HW revision')
        hw = 'c'
    return hw

# todo : Amit write here the write value !
async def task(event, number):
    # wait for the event to be set
    await event.wait()
    # generate a random value between 0 and 1
    value = random()
    # block for a moment
    await asyncio.sleep(value)
    # report a message
    print(f'Task {number} got {value}')

# async def waiter(event):
#     await event.wait()

async def task1(event, number):
    # wait for the event to be set

    await event.wait()
    # generate a random value between 0 and 1
    value = random()
    # block for a moment
    await asyncio.sleep(value)
    # report a message
    #print(f'Task1 wait  {number} got {value}')

def handle_rx(self, _: BleakGATTCharacteristic, data: bytearray):

        #print(f' waisting time : {st - self.accumolator}') todo: guy version ! -> 0.085Sec / proces 0.07 mSec
        #save the incoming data in list - All the data
        print((data.decode()))
        print("(data.decode())")
@qasync.asyncSlot()
async def run_fetch(device,
                    address,
                    loop,
                    sensor_id,
                    _verbose=True,
                    hw=None,
                    dir_name=None):
    global DataServiceUUIDString, DataCharacteristicUUIDString
    global data_received_event
    global all_data_received
    global DataNotificationState
    global verbose
    global mac_addr
    global hw_revision
    global fw_revision
    global output_path
    global serial_number

    verbose = _verbose
    if verbose:
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    mac_addr = address

    if output_path is None:
        embedded_tools_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        output_folder_in_vibration_test_tools = os.path.join(embedded_tools_path, 'VibrationTestTools', 'Output')
        hw_str = 'canaryr4000' if hw == 'c' else 'halo-ncs'
        if dir_name:
            base_path = os.path.join(output_folder_in_vibration_test_tools,
                                     '{}_{}'.format(hw_str, address.replace(':', '.')), dir_name
                                     )
            output_path = base_path
        else:
            base_path = os.path.join(output_folder_in_vibration_test_tools,
                                     '{}_{}'.format(hw_str, address.replace(':', '.')),
                                     )
            i = 1
            output_path = base_path + '_{}'.format(i)
            while os.path.exists(output_path):
                i = i + 1
                output_path = base_path + '_{}'.format(i)
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    print("######################   start   ##########################")
    logger.info("=========   Test Ble code         =========")
    logger.info("=========   Connecting to ep...   =========")

    client = BleakClient(address, device=device, loop=loop)
    err = ""
    connected = False
    conn_timeout = 10
    try:
        while not client.is_connected:
            print(time.strftime('%H-%M-%S'))
            try:
                connected = await client.connect(timeout=conn_timeout)
            except asyncio.CancelledError:
                logger.error("CancelledError - sample")
                await client.disconnect()
            except Exception as e:
                err = str(e)
                await client.disconnect()
        if connected is False:
            logger.error(err)
            return False
        else:
            logger.info("Connected: {0}".format(connected))
            try:
                _value = bytes(await client.read_gatt_char(HardwareRevisionCharacteristicUuidString))
                print(_value)
            except Exception as e:
                _value = str(e).encode()

            print("######################   Connect + Hw    ##########################")
            hw_revision = _value.decode("utf-8")
            hw = get_hw_type(hw_revision)
            logger.info("[HardwareRevision str: {0} ".format(hw_revision))
            print("######################   HW Read          ##########################")

            #######################################################
            await client.start_notify(DataCharacteristicUUIDString, data_notification_handler)
            print("######################   Notification     ##########################")
            all_channels = []
            if sensor_id == sensors.ALL:
                all_channels.extend(get_acceleration_channels())
                all_channels.extend(get_magnetic_channels(hw))
                all_channels.extend(get_temp_channel())
                all_channels.extend(get_ambient_temp_channel(hw))
                print("######################   All Channel  ##########################{0}".format(all_channels))
            elif sensor_id == sensors.SENSOR_MAGNETIC:
                all_channels = get_magnetic_channels(hw)

            elif sensor_id == sensors.SENSOR_IIS3DWB:
                all_channels = get_acceleration_channels()

            elif sensor_id == sensors.SENSOR_TMP1075:
                all_channels = get_temp_channel()

            elif sensor_id == sensors.SENSOR_TMP_AMBIENT:
                all_channels = get_ambient_temp_channel(hw)
            else:  # read acceleration only
                all_channels = get_acceleration_channels()

            all_channels = list(set(all_channels))
            logger.info('sensor channels: {}'.format(str(all_channels)))
            print("######################   Start Collect   ##########################{0}".format(all_channels))
            for channel in all_channels:
                print(f'start channel       !!!!!!!!! : {channel}')
                all_data_received = False
                DataNotificationState = 0
                # Todo: Amit
                #await client.start_notify(DataCharacteristicUUIDString, data_notification_handler)
                write_data = bytearray(struct.pack('BBH', channel, 0, 0))

                print("######################   Write to channel  ##########################{0}".format(channel))
                try:
                    _value = await client.write_gatt_char(DataCharacteristicUUIDString, write_data)
                except Exception as e:
                    _value = str(e).encode()

                #logger.info("[Characteristic Data  ] Write Value: {0} ".format(to_hex(write_data)))

                while all_data_received is False:
                    print("start Collecting data")
                    data_received_event.clear()
                    #data_received_waiter_task = asyncio.create_task(waiter(data_received_event))
                                                # await event.wait() !!
                    try:
                        print("######################   start asyncio  ##########################{0}")
                        data_received_event = asyncio.Event()
                        print(data_received_event.is_set())
                        print(data_received_event)
                        print("                                 i start to wait here !!!!!!!!!!!!!!!!!!!!")
                        await data_received_event.wait()

                        print("                                 i am wait here  !!!!!!!!!!!!!!!!!!!!!!!!!")
                        #t = [asyncio.create_task(task1(data_received_event, i)) for i in range(3)]
                        # tasks = asyncio.gather(divide(4, 2), divide(4, 0))
                        # try:
                        #     await tasks
                        #event.set()
                        #await asyncio.wait(data_received_event)

                        #done, _ = await asyncio.wait([task_a, task_b])
                        #done, _ = await asyncio.wait(data_received_waiter_task)
                        #for task in done:
                        #    if task.exception():
                        #      raise task.exception()
                        #    else:
                        #     print(task.result())
                        #print("11111111111111111111111111111111111111111111")
                        #print(" got Future <Future pending> attached to a different loop ")
                        #await asyncio.wait(data_received_waiter_task, timeout=3)
                        #await asyncio.sleep(0)
                        # await asyncio.gather(data_received_waiter_task, timeout=5)
                        #results = await asyncio.gather(data_received_waiter_task)
                        #print("pass")
                        #group = asyncio.gather(data_received_waiter_task)
                    except (asyncio.CancelledError, asyncio.TimeoutError) as e:
                        logger.error(e)
                        print("222222222222222222222222222222222222")
                        all_data_received = True
                print("------------------------------------------------------")
                print("------------------------------------------------------")
                print("------------------------------------------------------")
                print("------------------------------------------------------")
            #######################################################
            print("     1.       start data_notification_handler ")
            #await client.start_notify(DataCharacteristicUUIDString, data_notification_handler)

            #await client.start_notify(DataNotificationState, data_notification_handler)
            #await client.start_notify(DataServiceUUIDString, data_notification_handler)
            #await client.start_notify(DeviceInformationServiceUuidString, data_notification_handler)

            #print("2")
            #await client.start_notify(commandCharacteristicUUIDString, data_notification_handler)#todo: remove
            #await client.start_notify(DataServiceUUIDString, data_notification_handler)#todo: remove
            #print("3")
            #await client.start_notify(TestingServiceUUIDString, data_notification_handler)#todo: remove
            #print("4")
            #await client.start_notify(CurrentTimeServiceUuidString, data_notification_handler)#todo: remove
            #await client.start_notify(UU, data_notification_handler)  # todo: remove
            #print("----------------")
            ##logger.info("SendCharacteristicUuidString Notification Started!!!")
            #
            # hw_revision = _value.decode("utf-8")
            # hw = get_hw_type(hw_revision)
            #
            # logger.info("[HardwareRevision str: {0} ".format(hw_revision))

            # try:
            #     _value = bytes(await client.read_gatt_char(FirmwareRevisionCharacteristicUuidString))
            # except Exception as e:
            #     _value = str(e).encode()
            #
            # fw_revision = _value.decode("utf-8")
            # logger.info("[FirmwareRevision str: {0} ".format(fw_revision))

            # try:
            #     _value = bytes(await client.read_gatt_char(SerialNumberCharacteristicUuidString))
            # except Exception as e:
            #     _value = str(e).encode()
            #
            # serial_number = _value.decode("utf-8")
            # logger.info("[SerialNumber str: {0} ".format(serial_number))

            # logger.info("Connected: {0}".format(connected))
            # logger.info("[Service Data         ] {0}: {1}".format(DataServiceUUIDString, "Data"))
            # logger.info("[Characteristic Data  ] {0}: {1}".format(DataCharacteristicUUIDString, "Data"))



            all_channels = []
            if sensor_id == sensors.ALL:
                all_channels.extend(get_acceleration_channels())
                all_channels.extend(get_magnetic_channels(hw))
                all_channels.extend(get_temp_channel())
                all_channels.extend(get_ambient_temp_channel(hw))
            elif sensor_id == sensors.SENSOR_MAGNETIC:
                all_channels = get_magnetic_channels(hw)

            elif sensor_id == sensors.SENSOR_IIS3DWB:
                all_channels = get_acceleration_channels()

            elif sensor_id == sensors.SENSOR_TMP1075:
                all_channels = get_temp_channel()

            elif sensor_id == sensors.SENSOR_TMP_AMBIENT:
                all_channels = get_ambient_temp_channel(hw)
            else:  # read acceleration only
                all_channels = get_acceleration_channels()

            all_channels = list(set(all_channels))
            #logger.info('-------------sensor channels: {}'.format(str(all_channels)))

            for channel in all_channels:
                all_data_received = False
                DataNotificationState = 0
                print("start process")
                write_data = bytearray(struct.pack('BBH', channel, 0, 0))
                #logger.info("2     --------- > Sending Fetch command to EP )".format(channel))
                #print(write_data)
                try:
                    _value = await client.write_gatt_char(commandCharacteristicUUIDString, write_data)
                    logger.info("       2.    Fetch command Transmit to EP )".format(channel))
                    logger.info("       3.    data command Transmit to EP )".format(write_data))
                    print(write_data)

                except Exception as e:
                    _value = str(e).encode()


                # try:
                #     print("hello from code ")
                # except Exception as e:
                #     _value = str(e).encode()

                #logger.info("[Characteristic Data  ] Write Value: {0} ".format(to_hex(write_data)))
                #logger.info(to_hex(write_data))
                #await client.start_notify(DataCharacteristicUUIDString, handle_rx)
                #print("---------------------------------------------")
                #print(asyncio.get_event_loop())



                ###################################
                #print("----------    start Compare  ---------- ")
                # create a shared event object

                event = asyncio.Event()
                # create and run the tasks
                # start processing in all tasks
                event.set()
                data_received_event.set()
                # print(data_received_waiter_task)
                # print(type(data_received_waiter_task))

                print("     4.       create task data_received_event     ")
                data_received_waiter_task = [asyncio.create_task(waiter(data_received_event))]
                tasks = [asyncio.create_task(task(event, i)) for i in range(5)]
                # print(tasks)
                # print(type(tasks))
                # print(tasks[0])
                # print(type(tasks[0]))
                # allow the tasks to start

                await asyncio.sleep(1)
                # start processing in all tasks
                #event.set()
                #data_received_event.set()
                # await for all tasks  to terminate


                #################################################### check
                ##tasks = array of Task  []
                    ## each element is task (event , index )
                        ##async def task(event, number):
                            # wait for the event to be set
                            # await event.wait()
                            # # generate a random value between 0 and 1
                            # value = random()
                            # # block for a moment
                            # await asyncio.sleep(value)
                            # # report a message
                            # print(f'Task {number} got {value}')

                #data_received_waiter_task = [asyncio.create_task(waiter(data_received_event))]
                                                                #func event
                                                     #await event.wait()
                #tasks                     = [asyncio.create_task(task(event)]







                _ = await asyncio.wait(tasks, timeout=5)
                res = await asyncio.wait(data_received_waiter_task, timeout=5)
                print('if i read this its ok !!!!')
                print("-----------------------------------------------")
                print("-----------------------------------------------")
                print("-----------------------------------------------")
                print(res)
                print(_)
                print("-----------------------------------------------")


                #asyncio
                while all_data_received is False:
                    data_received_event.clear()
                    data_received_waiter_task = asyncio.create_task(waiter(data_received_event))


                    print(data_received_waiter_task)
                    print(type(data_received_waiter_task))

                    try:

                        print("print debbug from here - line 959 ")
                        res = await asyncio.wait(data_received_waiter_task, timeout=5) #todo: chaqnge here -> data recice waiter task
                        print(res)
                        print("1")
                        #resualt = await asyncio.wait_for(data_received_waiter_task, timeout=5)
                        #print(resualt)
                        print("++++++++++++++++++++++++++++++++++")
                        print("++++++++++++++++++++++++++++++++++")
                        print("++++++++++++++++++++++++++++++++++")
                        print("++++++++++++++++++++++++++++++++++")
                    except (asyncio.CancelledError, asyncio.TimeoutError) as e:
                        logger.error(e)
                        all_data_received = True
            return True

    except Exception as e:
        logger.error(e)
        return False
    finally:
        #logger.info("DisConnected: {0}".format(await client.disconnect()))
        logger.info("output path: {}".format(output_path))
        print("Finally !!!!!!!!!!!!!!!!!!!")

async def disconnect(client):
    try:
        await client.stop_notify(DataCharacteristicUUIDString)
        logger.info("DisConnected: {0}".format(await client.disconnect()))
        return True
    except asyncio.CancelledError:
        logger.error("CancelledError - disconnecting")
        return False

# if __name__ == "__main__":


# command_id = 0  # SampleNow Command
# sample_at_ts = round(time.time()) + sample_delay
# logger.info("======== Sample at: {} [{}] ========".format(
#     sample_at_ts, time.strftime('%H-%M-%S', time.localtime(sample_at_ts))))
# write_data = bytearray(struct.pack('=HHHHHI', command_id, sensor_id, odr, scale, duration, sample_at_ts))
#
# logger.info("Sending Sample-All command to EP (command_id={0} ;"
#             "sensor_id={1} ; odr={2} ; scale={3} ; duration={4} ; sample_at_ts={5})".
#             format(command_id, sensor_id, odr, scale, duration, sample_at_ts))
