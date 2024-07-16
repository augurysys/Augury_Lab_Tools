import testble
import cbor2
import array

## Cbor msg to Ep ##
####################
        #1
        # Canary EP UUT stage:
        # The UUT stage is a value set in the internal flash of the EP to indicate which stage the unit is in within the production line testing stages of the EP.
        # When the EP image is burned the EP will be in stage 1 and the EP exposes 3 commands regarding the UUT stage:
        # Get current stage value and and an indication whether this is the final stage or not
        # Increment the current stage value (valid values 1-30)
        # Set current value as final - this means that the unit passed all stages and is ready for installation.

        #2
        # Canary EP BIST (Built-In-Self-Test)
        # The Canary EP can run tests to validate that all of its HW components are working correctly. The EP exposes commands over BLE that allow running these tests and getting a report about it.

        #3
        #Canary EP Current Time:
        #The Canary EP allows the user to set/get the current time (date/time) in the EP.
        #Setting the current time is a prerequisite for any other testing service it provide

        #Canary EP commands:
        #       Forcing the EP to go to sleep for a given amount of time
        #       Sampling all/part of the sensors
        #       Download the last sampled data



######### Device info:
        # GATT service: Device Information Service (0x180A)
        # The standard Device information service is exposed by the Canary EP and exposes the following information over the standard characteristics:
        #
        # Char: Model Number string (0x2A24) (standard characteristic)
        # Access: Read
        # Exposes the Module type as string (in Canary EP the string is “Canary”)
        #
        # Char: Manufacturer Name string (0x2A29) (standard characteristic)
        # Access: Read
        # Exposes the Manufacturer Name as string (in Canary EP the string is “Augury Inc.”)
        #
        # Char Serial number string (0x2A25) (standard characteristic)
        # Access: Read
        # Exposes the serial number of the EP (string)
        #
        # Char: Firmware reversion string (0x2A26) (standard characteristic)
        # Access: Read
        # Exposes the Firmware reversion of the EP (string)
        #
        # Char: Hardware reversion string (0x2A27) (standard characteristic)
        # Access: Read
        # Exposes the HW reversion of the EP (string)


######### Current Time:
        # GATT service: commands (UUID 0bb52dda-d431-40cc-8a41-a666a25254b6)
        # Char: Augu Set Time (UUID d82c52f5-51ee-490f-bf1e-1d841fb9c66f)
        # Access: write, read
        # This allows the client to set and get the current time in the EP.
        # The value (both for read and write) is a cbor encoded map that includes one field that is linux epoch time in milliseconds (UTC time).
        # e.g.
        # {
        #    “time”:1651363200000
        # }



######### Built In Self Test (BIST):
        # GATT service: testing (UUID 53cdde50-a736-4793-a0dd-a818fbbd3fd0)
        # Char: BIST (UUID 54f5aab5-5ebf-40b1-a819-e49bf3024048)
        # Access: write, notify
        #
        # Run BIST:
        # Write to the BIST Char the value 0x01
        #
        # Note: This will result in creating a new report file and will overwrite the previous report file
        #
        # Get last BIST report:
        # Enable Notify on the testing Characteristic
        # Write to the BIST Char the value 0x02
        # The EP will send  2 CBOR files:
        # Info CBOR file
        # BIST results CBOR file
        #
        # Info CBOR file
        # Sent in 1st notification
        # This file includes the version and size of the BIST results CBOR file which is sent next
        # Structure:
        # {
        #     "len": <bist_results_size>,
        #     "ver": <bist_results_version>
        # }
        #
        #
        #
        # BIST Results CBOR file
        # Sent in the 2nd notification and on. These notifications (2nd notification and on) are aggregated to the full BIST results report CBOR file
        #
        # The structure of the report CBOR file is as follows:
        # “bist_result” - (string - pass/fail/not executed)
        # “timestamp” - (int - timestamp in posix epoch format)
        # “tests” - (array) of items that are of type map that have the following structure:
        # “name”: (string)
        # “result”: (string - pass/fail reasons separated by “,”)
        # “raw” : (byte string)
        # example:
        # {
        #     "bist_result": "pass",
        #     "timestamp": 1651065325557,
        #     "tests": [
        #         {
        #             "name": "battery level (adc)",
        #             "raw": "-",
        #             "result": "PASS"
        #         },
        #         {
        #             "name": "hw id check",
        #             "raw": "-",
        #             "result": "PASS"
        #         },
        #         …
        #      ]
        # }




try:
    from bleak.backends.winrt.util import allow_sta
    # tell Bleak we are using a graphical user interface that has been properly
    # configured to work with asyncio
    allow_sta()
except ImportError:
    # other OSes and older versions of Bleak will raise ImportError which we
    # can safely ignore
    pass
from testble import *
import asyncio
from dataclasses import dataclass
from functools import cached_property
from bleak.backends.characteristic import BleakGATTCharacteristic
import os
import time
import struct
import json
#from AuguryUiA2 import *
from AuguryUi3_7 import *
from rich.console import Console
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QLineEdit,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
import AmitFunction
import qasync
from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets
import plotly.express as px
import plotly.graph_objects as go
from threading import Event
from AuguryTestSample import *

UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
#UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

UART_RX_CHAR_UUID = "ac7bf687-7a30-4336-a6f6-b8030930854d"

# all other EPAugury_Lab.py
CurrentTimeServiceUuidString = "00001805-0000-1000-8000-00805f9b34fb"
CurrentTimeCharacteristicUuidString = "00002a2b-0000-1000-8000-00805f9b34fb"

CommandServiceUUIDString = "0bb52dda-d431-40cc-8a41-a666a25254b6"
commandCharacteristicUUIDString = "ac7bf687-7a30-4336-a6f6-b8030930854d"

BT_UUID_COMMANDS = "38efff62-58d9-475a-b311-e16494a89cf5"

DataServiceUUIDString = "bf289137-78a3-4c60-b381-25558e78e252"
DataCharacteristicUUIDString = "b5d1f9be-b0bb-4059-9cb7-c2fffd184770"

DeviceInformationServiceUuidString = "0000180A-0000-1000-8000-00805f9b34fb"
FirmwareRevisionCharacteristicUuidString = "00002A26-0000-1000-8000-00805f9b34fb"

HardwareRevisionCharacteristicUuidString = "00002A27-0000-1000-8000-00805f9b34fb"
SerialNumberCharacteristicUuidString = "00002A25-0000-1000-8000-00805f9b34fb"

TestingServiceUUIDString = "53cdde50-a736-4793-a0dd-a818fbbd3fd0"
TestingCharacteristicUUIDString = "54f5aab5-5ebf-40b1-a819-e49bf3024048"

#LEDs_control_UUID=  "37028891-93b2-4b81-86c6-f5e49c0616cf
#UUT_stage_(UUID dac93259-da1d-4388-904a-7bc3b6d016f0)


UART_SAFE_SIZE = 20
samplecounter = 0
sensor = 0
deviceBLE = "None"
Bledevicelist = []
listofDeviceComboBox = []
device = None
file = None
fileJson = None
fileName = ""
countersample = -6
hw_revision = 0

data_received_event = asyncio.Event()
global loop
all_data_received = False

verbose = True
mac_addr = ""
output_path = None
address_device = ""


def parse_data(data):
    global all_data_received
    global mac_addr
    global hw_revision
    global fw_revision
    global output_path
    global serial_number

    print("Parsing data from augulab ...")

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
    #print(data_format)
    #json_data['Data_Format'] = data_format[meta_data_format]
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

    print(hw_revision)
    print(mac_str)
    print(meta_timestamp)
    print(meta_sensor_id)
    print(meta_channel)

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


@dataclass
class QBleakClient(QObject):
    global MainWindow
    global ui
    device: BLEDevice
    messageChanged = pyqtSignal(bytes)
    count = 0
    Elem = 64000
    maxCount = 0
    countersample = -1
    step = 0
    state = 0
    calc = 0
    startMeasure = 0
    endMeasure = 0
    rec = 0
    corrent_count = 0
    databuffer = []
    TendMeasure = 0
    TstartMeasure = 0

    sensor_output = {
        "name": "#from Connect Device",  # from Connect Device
        "output_data": "#from Rx channel",  # from Rx channel
        "fs_rec": "#By user / code",  # By user / code
        "Sensor_ID": "#from Connect Device",  # from Connect Device
        "Serial_Number": "",  # from Connect Device
        "Data_Channel": "Acceleration_Z",  # config later more
        "Sensitivity": [15, 30, 60],  # Sensitivity
        "Scaling_Factor": [1, 2, 3],  # intern Scaling_Factor
        "Sensor_Temperature": "TBD",  # Sensor_Temperature
        "Num_Of_Samples": "",  # from Connect Device
        "Data": []  # ActualData
    }

    def __post_init__(self):
        super().__init__()

    @cached_property
    def client(self) -> BleakClient:
        # print(f'                    client -> self.client : {self.client}')
        print(f'                            client -> self.client : {self.device}')
        return BleakClient(self.device, disconnected_callback=self.handle_disconnect2)

    async def start(self):
        print("             FC ->  start in client -> connect & handler ")
        MainWindows.UiPrint(ui, "        Function call start in client.")
        try:
            print(f'             start -> self.client : {self.client}')
            print("              Qbleak start build_client before :  {}".format(MainWindows.current_client))
            print("              start build_client before  :   {}".format(self.client))
            print("              Qbleak ->start connect ")
            await self.client.connect()
            print("              Qbleak ->end connect ")
            print(f'             Qbleak -> self.client : {self.client}')

            ## firmware ##
            ##############
            try:
                _value = bytes(await self.client.read_gatt_char(HardwareRevisionCharacteristicUuidString))
                print(self.client)
            except Exception as e:
                _value = str(e).encode()
            print(f'             3        value : {_value}')
            try:
                _value = bytes(await self.client.read_gatt_char(FirmwareRevisionCharacteristicUuidString))
            except Exception as e:
                _value = str(e).encode()
            print(f'            4       firmware value : {_value}')
            fw_revision = _value.decode("utf-8")
            print("             5       [FirmwareRevision str: {0} ".format(fw_revision))

            print(self.client)
            #await self.client.start_notify(DataCharacteristicUUIDString, self.handle_rx)   #todo:  guy version :UART_TX_CHAR_UUID
            #await self.client.start_notify(DataCharacteristicUUIDString, self.handle_rx)
            await self.client.start_notify(DataCharacteristicUUIDString, self.data_notification_handler)
            #await self.client.start_notify(UART_TX_CHAR_UUID, self.handle_rx)
            #await self.client.start_notify(UART_SERVICE_UUID, self.handle_rx)
            print("Connect ->  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ")
            MainWindows.UiPrint(ui, "        Device is Connect")

            ######
            #time.sleep(1)
            ######## Send as i do #########
            #
            # try:
            #     _value = bytes(await self.client.read_gatt_char(FirmwareRevisionCharacteristicUuidString))
            # except Exception as e:
            #     _value = str(e).encode()
            # fw_revision = _value.decode("utf-8")
            # logger.info("[FirmwareRevision str: {0} ".format(fw_revision))

            # b = bytearray(
            #     [0xa2, 0x61, 0x64, 0x19, 0x0f, 0xa0, 0x62, 0x63, 0x68, 0x86, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05])
            # try:
            #     await self.client.write_gatt_char(commandCharacteristicUUIDString, b)
            #     await self.client.write_gatt_char(CommandServiceUUIDString, b)
            #     # _value = bytes(await client.write_gatt_char(CurrentTimeCharacteristicUuidString, write_data))
            #     print(" Send msg ok  : {} ".format(b))
            # except Exception as e:
            #     _value = str(e).encode()
            #
            # try:
            #     await self.client.write_gatt_char(commandCharacteristicUUIDString, b)
            #     # _value = bytes(await client.write_gatt_char(CurrentTimeCharacteristicUuidString, write_data))
            #     print(" Send msg : {} ".format(b))
            # except Exception as e:
            #     _value = str(e).encode()
            #
            # try:
            #     await self.client.write_gatt_char(CommandServiceUUIDString, b)
            #     # _value = bytes(await client.write_gatt_char(CurrentTimeCharacteristicUuidString, write_data))
            #     print(" Send msg : {} ".format(b))
            # except Exception as e:
            #     _value = str(e).encode()
            #
            # time.sleep(2)
            #
            # try:
            #     print("here ")
            #     await self.client.write_gatt_char(CommandServiceUUIDString, b)
            #     await self.client.write_gatt_char(CurrentTimeCharacteristicUuidString, b)
            #     print(" Send msg : {} ".format(b))
            # except Exception as e:
            #     _value = str(e).encode()


        except Exception as e:
            MainWindows.UiPrint(ui, "       Something went wrong - error: {}".format(e))
            print("             start function Error")
    async def stop(self):
        print("FC -> QBleakClient -> Stop Func")
        await self.client.disconnect()
        MainWindows.UiPrint(ui, "QBleakClient -> Disconnect From Device")

    async def write(self, data):
        print("FC -> write ")
        await self.client.write_gatt_char(UART_RX_CHAR_UUID, data)
        print("send:", data)

    async def writedata(self, UUID, data):
        print("FC -> write ")
        await self.client.write_gatt_char(UUID, data)
        print("send:", data)

    async def read_gatt(self): # todo: add data + uuid
        print("FC -----> Read gatt ")
        try:
            _value = bytes(await self.client.read_gatt_char(HardwareRevisionCharacteristicUuidString))
        except Exception as e:
            _value = str(e).encode()
        print(f'Ican Read all data value : {_value}')
        return _value


    def handle_disconnect2(self, _: BleakClient):  # (self) -> None:
        MainWindows.UiPrint(ui, "QBleakClient -> handle_disconnect2 call Back from clien")
        MainWindows.UiPrint(ui, "Close The File")
        file.close()
        MainWindows.UiPrint(ui, "+++++   Device is Disconnect   +++++")
        MainWindows.progBarUpdate(ui, 0, 0)
        # cancelling all tasks effectively ends the program
        # for task in asyncio.all_tasks():
        #    task.cancel()

    @qasync.asyncSlot()
    def handle_disconnect(self) -> None:
        print("Qbleak - handle_disconnect function.")
        # cancelling all tasks effectively ends the program
        for task in asyncio.all_tasks():
            task.cancel()

    def _handle_read(self, _: int, data: bytearray) -> None:
        # print("received:", data)
        self.messageChanged.emit(data)

    def data_notification_handler(self, _: BleakGATTCharacteristic, data: bytearray):
        global DataBytesExpected
        global DataBuffer
        global MetaDataBuffer
        global data_received_event
        global all_data_received
        global DataNotificationState
        global meta_sensor_id, meta_temp_avg, meta_sampling_freq, meta_timestamp, meta_num_of_samples, meta_overrun, meta_channel, meta_data_format, meta_data_unit, meta_scale
        print("iget somthing !!!! ")
        # print("get somthing - > data_notification_handler !!!!  ")
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
            #print("===HERE===")
            for x in data:
                DataBuffer.append(x)

            #print("DATA FORMAT : ".format(DataBuffer))
            if DataBytesExpected:
                drawProgressBar(len(DataBuffer) / DataBytesExpected, 100)

            if len(DataBuffer) == DataBytesExpected:
                DataNotificationState = 4


                print("All data was received successfully!!! ({0} Bytes)".format(len(DataBuffer)))
                parse_data(DataBuffer)
                # except:
                #     print("+++++    Error   +++++")

    def handle_rx(self, _: BleakGATTCharacteristic, data: bytearray):
        global samplecounter
        global file
        global fileJson
        st = time.time()
        print("get some data here :")
        #print(f' waisting time : {st - self.accumolator}') todo: guy version ! -> 0.085Sec / proces 0.07 mSec
        #save the incoming data in list - All the data
        self.databuffer.append((data.decode()))
        file.write('{0},'.format(str(data.decode())))  # to change one line vs multi
        # todo: later fix the buffer more generic for all ep - now save all
        #ACK, ACK, ELem =, 64000, Sample Time =, 3921990
        if len(self.databuffer) == 7:
            if self.databuffer[2] == 'ELem=':
                self.Elem = int(self.databuffer[3])
                print("===========")
                print(self.databuffer)
                print(self.Elem)
                print(self.databuffer[5])
                self.countersample = 0
                self.rec = True
                print("===========")
        # file.write('{0},'.format(str(data.decode()))) # to change one line vs multi
        # self.sensor_output['Data'] = self.databuffer

        # todo: in the end save it ->  only if disconnect / stop !
        #self.sensor_output['Data'] = self.databuffer
        #json.dump(self.sensor_output, fileJson)
        #each 200 sample we call this function to calc data
        if self.countersample % 100 == 0 and self.rec:
            # cal each 100 rx msg Timinig
            if self.state == 0:
                print(f"start  ----- {self.countersample}")
                self.startMeasure = time.time()
                self.state = 1
            else:
                print(f"stop   ----- {self.countersample}")
                self.endMeasure = time.time()
                self.state = 0
                self.calc = 1
                self.corrent_count += 1

            if self.calc == 1:
                timer = AmitFunction.calculate_duration(int((self.endMeasure * 1000) - (self.startMeasure * 1000)), 100, int(self.Elem), Currentcount=self.corrent_count)
                self.calc = 0
                MainWindows.hourUpdate(ui, min=timer[0], sec=timer[1])
                MainWindows.progBarUpdate(ui, counter=self.countersample, Element=self.Elem)
                #print("@@@---------------------->>>>>>> timer function ")
                #print(f' timerAvr:  {timer}')
                #print("cal time (stim , Endtime , Delta =200 , Elem = 64000 , count) : ")
                # call calc calcduration () - > m , s dict
                # print(f'  Delta Time  : {self.endMeasure - self.startMeasure}')
                # print(f' self.accumolator {self.accumolator}')
                # print(f' counter sample {self.countersample}')
                # print(f'( if inside here for update : {self.countersample}  + delta T each rx : {time.time() - st}')
                #updata UI
                # json file write once on valid data only!
        self.countersample += 1
        if (self.rec and self.countersample == 64000 ):
            self.sensor_output['Data'] = self.databuffer
            print("DDDDDDDoooooooooooooneeeeeeee")
            print("save the data to file")
            self.sensor_output['Data'] = self.databuffer
            print(self.databuffer)
            print(len(self.databuffer))
            print(self.sensor_output)
            MainWindows.end_sample(ui, self.sensor_output)
            #fileJson = open(self.FileNameJson, "w")
            # self.sensor_output['Data'] = self.databuffer
            # json.dump(self.sensor_output, fileJson)
            # self.sensor_output['Data'] = []
            self.rec = 0
        # END Of Rx interrupt
        #self.acc = time.time()
        #print(f'( self.countersample {self.countersample}  + delta T each rx : {time.time() - st}')


async def waiter(event):
    await event.wait()


def command_notification_handler(sender, data):
    global data_received_event

    """
    Simple notification handler which prints the data received.
    """
    print("Notify {0}: {1}".format(sender, data))
    data_received_event.set()


class MainWindows(QMainWindow, Ui_MainWindow):
    def __init__(self, window):
        super().__init__()
        global loop
        print("init main ui")
        self.setupUi(window)
        self.resize(750, 650)
        self._client = None
        scan_button = QPushButton("Scan Devices")
        self.devices_combobox = QComboBox()
        connect_button = QPushButton("Connect")
        self.message_lineedit = QLineEdit()
        send_button = QPushButton("Send Message")
        self.log_edit = QPlainTextEdit()
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        lay = QVBoxLayout(central_widget)
        lay.addWidget(scan_button)
        lay.addWidget(self.devices_combobox)
        lay.addWidget(connect_button)
        lay.addWidget(self.message_lineedit)
        lay.addWidget(send_button)
        lay.addWidget(self.log_edit)

        self.button = QtWidgets.QPushButton('Plot', self)
        self.pb_plot.clicked.connect(self.show_graph)
        self.pb_stop_sample.clicked.connect(self.read_temp)
        #self.cmdline.event(self.cmdline)

        self.pb_stop_sample.setEnabled(True)
        self.pb_plot.setEnabled(False)
        self.cb60.setEnabled(False)
        self.cb30.setEnabled(False)
        self.cb15.setEnabled(False)
        self.cb15.setChecked(True)

        self.lable_config.setEnabled(False)
        self.progressBar.setEnabled(False)
        self.lable_progress.setEnabled(False)
        self.pb_connect.setEnabled(False)
        self.pb_start_sample.setEnabled(False)
        self.pb_disconnect.setEnabled(False)
        self.pb_scan.setEnabled(True)
        self.comboBox.setEnabled(False)

        self.model = QtGui.QStandardItemModel()
        self.listView.setModel(self.model)
        self.listView.setAutoScroll(True)
        self.listView.scrollToBottom()
        self.pb_start_sample.clicked.connect(self.handle_start_sample)
        # self.Connect_Pb.setStyleSheet("background-color : red")
        self.pb_connect.clicked.connect(self.handle_connect)
        self.pb_scan.clicked.connect(self.handle_scan)
        self.pb_disconnect.clicked.connect(self.handle_disc)
        self.cb15.clicked.connect(lambda: self.handle_cb(value=15))
        self.cb30.clicked.connect(lambda: self.handle_cb(value=30))
        self.cb60.clicked.connect(lambda: self.handle_cb(value=60))
        self.FileName = ""
        self.Config = ""
        global file, fileJson

        self.pushButton_2.clicked.connect(self.handle_pb2)
        self.pushButton_3.clicked.connect(self.handle_pb3)
        self.pushButton_4.clicked.connect(self.handle_pb4)
        self.pushButton_5.clicked.connect(self.handle_pb5)
        self.pushButton_6.clicked.connect(self.handle_pb66)

        self.pushButton_4.setText("Sample & save ")


    def end_sample(self, buffer):
        print(buffer)
        with open(self.FileNameJson, 'w') as f:
            json.dump(buffer, f)

        print("END HERE")

    @qasync.asyncSlot()
    async def handle_pb66(self):
        print(" ")
        print(" ")
        print("     self.handle_pb66  --- > sample now ")  # send somthing here
        # await self._client.start_notify(DataCharacterist

        sample_delay = 0 # after 2 sec
        command_id = 0  # SampleNow Command
        sample_at_ts = round(time.time()) + sample_delay
        sample_at_ts = 0
        duration = 4000
        scale = 0
        odr = 0
        sensor_id = 99

        logger.info("======== Sample at: {} [{}] ========".format(
            sample_at_ts, time.strftime('%H-%M-%S', time.localtime(sample_at_ts))))
        write_data = bytearray(struct.pack('=HHHHHI', command_id, sensor_id, odr, scale, duration, sample_at_ts))

        print("     Sending Sample-All command to EP (command_id={0} ;"
                    "sensor_id={1} ; odr={2} ; scale={3} ; duration={4} ; sample_at_ts={5})".
                    format(command_id, sensor_id, odr, scale, duration, sample_at_ts))


        try:
            _value = await self.current_client.write(write_data)
        except Exception as e:
            _value = str(e).encode()

        write_data = bytearray(struct.pack('=HHHHHI', command_id, sensor_id, odr, scale, duration, sample_at_ts))

        # sensor_id = 0x99
        # print("     Sending Sample-All command to EP (command_id={0} ;"
        #       "sensor_id={1} ; odr={2} ; scale={3} ; duration={4} ; sample_at_ts={5})".
        #       format(command_id, sensor_id, odr, scale, duration, sample_at_ts))
        #
        # try:
        #     _value = await self.current_client.write(write_data)
        # except Exception as e:
        #     _value = str(e).encode()

        print("     _Value: {0} ".format(_value))
        print(" END PB 66 ")






    @qasync.asyncSlot()
    async def handle_pb2(self):
        print("self.handle_pb2") # send somthing here
        #await self._client.start_notify(DataCharacteristicUUIDString, data_notification_handler)
        # write_data = bytearray(struct.pack('BBH', 0, 0, 0))
        # print(write_data)
        # try:
        #     _value = await self._client.write_gatt_char(DataCharacteristicUUIDString, write_data)
        # except Exception as e:
        #     _value = str(e).encode()

        # result = self.cmdline.toPlainText() # string here
        #
        # try:
        #     _value = bytes(await self.client.read_gatt_char(HardwareRevisionCharacteristicUuidString))
        # except Exception as e:
        #     _value = str(e).encode()
        # print(f'33        value : {_value}')
        #
        # try:
        #     _value = bytes(await self._client.read_gatt_char(HardwareRevisionCharacteristicUuidString))
        # except Exception as e:
        #     _value = str(e).encode()
        # print(f'44       value : {_value}')
        #
        #
        # print(" input  string : {} ".format(result))
        # # convert to the same
        # b = bytearray()
        #
        # for item in result:
        #     b.append(int(item))
        # print(b)
        # print(" Send cmd msg : {} ".format(b))
        #
        # try:
        #     _value = await self.current_client.write_gatt_char(commandCharacteristicUUIDString, b)
        #     _value = await self.current_client.write_gatt_char(CommandServiceUUIDString, b)
        #     _value = await self._client.write_gatt_char(CommandServiceUUIDString, b)
        #     _value = await self._client.write_gatt_char(commandCharacteristicUUIDString, b)
        #     await self.client.write_gatt_char(commandCharacteristicUUIDString, b)
        #     await self.client.write_gatt_char(CommandServiceUUIDString, b)
        #     # _value = bytes(await client.write_gatt_char(CurrentTimeCharacteristicUuidString, write_data))
        #     print(" Send msg : {} ".format(b))
        # except Exception as e:
        #     _value = str(e).encode()

        PacketsExpected = 2
                # run_bist = 1
                # #await self.current_client.start_notify(TestingCharacteristicUUIDString, testing_notification_handler)
                # if (run_bist):
                #     write_data = bytearray(b'\x01')
                #     print("Sending 'run built in self test' command to EP ")
                #
                #     try:
                #         _value = await self.current_client.writedata(TestingCharacteristicUUIDString, write_data)
                #     except Exception as e:
                #         _value = str(e).encode()
                #
                #     logger.info("[Characteristic Command   ] Write Value: {0} ".format(to_hex(write_data)))
                #     print(_value)


        # else:
        write_data = bytearray(b'\x02')
        logger.info("Sending 'get built in self test results' command to EP ")
        try:
            _value = await self.current_client.writedata(TestingCharacteristicUUIDString, write_data)
        except Exception as e:
            _value = str(e).encode()

        print("[Characteristic Command   ] Write Value: {0} ".format(to_hex(write_data)))

        # make handler - await client.start_notify.

        # while all_data_received is False:
        #     data_received_event.clear()
        #     data_received_waiter_task = asyncio.create_task(waiter(data_received_event))
        #     try:
        #         await asyncio.wait_for(data_received_waiter_task, timeout=5)
        #     except asyncio.CancelledError:
        #         logger.error("CancelledError - BUILT IN SELF TEST")
        #     except asyncio.TimeoutError:
        #         logger.error("Data receive timeout - BUILT IN SELF TEST")
        #         return False

        #await client.stop_notify(TestingCharacteristicUUIDString)
        data_as_json = cbor2.loads(binascii.a2b_hex(DataBuffer.hex()))
        print(json.dumps(data_as_json, indent=4, sort_keys=True))

    # pb4
    # global CommandServiceUUIDString, commandCharacteristicUUIDString
    # print("self.handle_pb4")
    # b = bytearray(
    #     [0xa2, 0x61, 0x64, 0x19, 0x0f, 0xa0, 0x62, 0x63, 0x68, 0x86, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05])
    # try:
    #     await self.client.write_gatt_char(commandCharacteristicUUIDString, b)
    #     await self.client.write_gatt_char(CommandServiceUUIDString, b)
    #     # _value = bytes(await client.write_gatt_char(CurrentTimeCharacteristicUuidString, write_data))
    #     print(" Send msg : {} ".format(b))
    # except Exception as e:
    #     _value = str(e).encode()
    #
    # try:
    #     _value = bytes(await self._client.read_gatt_char(HardwareRevisionCharacteristicUuidString))
    # except Exception as e:
    #     _value = str(e).encode()
    # print(_value)
    @qasync.asyncSlot()
    async def handle_pb4(self):
        global address_device
        global data_received_event
        global all_data_received
        global DataNotificationState
        global verbose
        global mac_addr
        global hw_revision
        global fw_revision
        global output_path
        global serial_number

        sensor_id = 99 # make parameter
        hw = None
        dir_name = None
        #################################
        # only if device + is connect ! #
        #################################
        if verbose:
            logging.basicConfig(stream=sys.stdout, level=logging.INFO)

        address = address_device
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
                print(base_path)
                print(output_path)
            else:
                base_path = os.path.join(output_folder_in_vibration_test_tools,
                                         '{}_{}'.format(hw_str, address.replace(':', '.')),
                                         )
                i = 1
                print(base_path)
                print(output_path)
                output_path = base_path + '_{}'.format(i)
                while os.path.exists(output_path):
                    i = i + 1
                    output_path = base_path + '_{}'.format(i)
        if not os.path.exists(output_path):
            os.makedirs(output_path)


        print("######################   start   ##########################")

        print("######################   Start Fetch PB4     ##########################")
        try:
            _value = bytes(await self.current_client.read_gatt())
            print(_value)
        except Exception as e:
            _value = str(e).encode()

        hw_revision = _value.decode("utf-8")
        hw = get_hw_type(hw_revision)

        #TODO: need to make method for it now its work !
        #await client.start_notify(DataCharacteristicUUIDString, data_notification_handler)
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
            # await client.start_notify(DataCharacteristicUUIDString, data_notification_handler)
            write_data = bytearray(struct.pack('BBH', channel, 0, 0))

            print("######################   Write to channel  ##########################{0}".format(channel))
            try:
                _value = await self.current_client.writedata(DataCharacteristicUUIDString, write_data)
            except Exception as e:
                _value = str(e).encode()

            while all_data_received is False:
                print("start Collecting data")
                data_received_event.clear()
                # data_received_waiter_task = asyncio.create_task(waiter(data_received_event))
                # await event.wait() !!
                try:
                    print("######################   start asyncio  ##########################{0}")
                    data_received_event = asyncio.Event()
                    print(data_received_event.is_set())
                    print(data_received_event)
                    print("                                 i start to wait here !!!!!!!!!!!!!!!!!!!!")
                    await data_received_event.wait()

                    print("                                 i am wait here  !!!!!!!!!!!!!!!!!!!!!!!!!")
                    # t = [asyncio.create_task(task1(data_received_event, i)) for i in range(3)]
                    # tasks = asyncio.gather(divide(4, 2), divide(4, 0))
                    # try:
                    #     await tasks
                    # event.set()
                    # await asyncio.wait(data_received_event)

                    # done, _ = await asyncio.wait([task_a, task_b])
                    # done, _ = await asyncio.wait(data_received_waiter_task)
                    # for task in done:
                    #    if task.exception():
                    #      raise task.exception()
                    #    else:
                    #     print(task.result())
                    # print("11111111111111111111111111111111111111111111")
                    # print(" got Future <Future pending> attached to a different loop ")
                    # await asyncio.wait(data_received_waiter_task, timeout=3)
                    # await asyncio.sleep(0)
                    # await asyncio.gather(data_received_waiter_task, timeout=5)
                    # results = await asyncio.gather(data_received_waiter_task)
                    # print("pass")
                    # group = asyncio.gather(data_received_waiter_task)
                except (asyncio.CancelledError, asyncio.TimeoutError) as e:
                    logger.error(e)
                    print("222222222222222222222222222222222222")
                    all_data_received = True
            print("------------------------------------------------------")
            print("------------------------------------------------------")
            print("------------------------------------------------------")
            print("------------------------------------------------------")
            print("######################   DATA IS Ready !!!!!     ##########################")
            # logger.info("[Characteristic Data  ] Write Value: {0} ".format(to_hex(write_data)))

        #     while all_data_received is False:
        #         print("start Collecting data")
        #         data_received_event.clear()
        #         # data_received_waiter_task = asyncio.create_task(waiter(data_received_event))
        #         # await event.wait() !!
        #         try:
        #             print("######################   start asyncio  ##########################{0}")
        #             data_received_event = asyncio.Event()
        #             print(data_received_event.is_set())
        #             print(data_received_event)
        #             print("                                 i start to wait here !!!!!!!!!!!!!!!!!!!!")
        #             await data_received_event.wait()
        #
        #             print("                                 i am wait here  !!!!!!!!!!!!!!!!!!!!!!!!!")
        #             # t = [asyncio.create_task(task1(data_received_event, i)) for i in range(3)]
        #             # tasks = asyncio.gather(divide(4, 2), divide(4, 0))
        #             # try:
        #             #     await tasks
        #             # event.set()
        #             # await asyncio.wait(data_received_event)
        #
        #             # done, _ = await asyncio.wait([task_a, task_b])
        #             # done, _ = await asyncio.wait(data_received_waiter_task)
        #             # for task in done:
        #             #    if task.exception():
        #             #      raise task.exception()
        #             #    else:
        #             #     print(task.result())
        #             # print("11111111111111111111111111111111111111111111")
        #             # print(" got Future <Future pending> attached to a different loop ")
        #             # await asyncio.wait(data_received_waiter_task, timeout=3)
        #             # await asyncio.sleep(0)
        #             # await asyncio.gather(data_received_waiter_task, timeout=5)
        #             # results = await asyncio.gather(data_received_waiter_task)
        #             # print("pass")
        #             # group = asyncio.gather(data_received_waiter_task)
        #         except (asyncio.CancelledError, asyncio.TimeoutError) as e:
        #             logger.error(e)
        #             print("222222222222222222222222222222222222")
        #             all_data_received = True
        #     print("------------------------------------------------------")
        #     print("------------------------------------------------------")
        #     print("------------------------------------------------------")
        #     print("------------------------------------------------------")
        # #######################################################
        # print("     1.       start data_notification_handler ")
        # await client.start_notify(DataCharacteristicUUIDString, data_notification_handler)

        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        A = Vibration_Analysis()
        print(output_path)
        A.run_vibration_analysis(report_path= output_path, method="wave_packet", white_list= "89, 281, 479, 677, 877, 1069, 1259, 1459, 1657, 1847, 2039, 2237, 2437, 2633, 2833, 3023, 3217, 3413, 3613, 3803, 4001, 4201, 4397, 4591, 4793, 4993, 5189, 5387, 5573, 5779, 5953, 6151",
                                  shaker_reports_full_path="piezo.json", shaker_tool_only='false')

    @qasync.asyncSlot()
    async def handle_pb5(self):
        #print(self.client) -> Error
        print("======   Handle_PB5  ======")
        milliseconds_since_epoch = (round(time.time() * 1000))
        write_data = bytearray(struct.pack('q', milliseconds_since_epoch))
        print("Sending Set-Time command to EP (CT={0})".format(milliseconds_since_epoch))
        try:
            _value = bytes(await self.current_client.writedata(CurrentTimeCharacteristicUuidString, write_data))
        except Exception as e:
            _value = str(e).encode()


    @qasync.asyncSlot()
    async def handle_pb6(self):

        print(self._client)
        print("self.handle_pb6")
        try:
            _value = bytes(await self._client.read_gatt_char(HardwareRevisionCharacteristicUuidString))
            print(_value)

            _value = bytes(await self._client.read_gatt_char(HardwareRevisionCharacteristicUuidString))
            print(_value)

            _value = bytes(await self.current_client.read_gatt_char(HardwareRevisionCharacteristicUuidString))
            print(_value)

        except Exception as e:
            _value = str(e).encode()


    def handle_cb(self, value):
        #todo: need init state / or call this function on init
        print("config funtion state")
        self.cb15.setChecked(False)
        self.cb30.setChecked(False)
        self.cb60.setChecked(False)

        if value == 15:
            self.cb15.setChecked(True)
            self.cb30.setChecked(False)
            self.cb60.setChecked(False)
        elif value == 30:
            self.cb15.setChecked(False)
            self.cb30.setChecked(True)
            self.cb60.setChecked(False)
        elif value == 60:
            self.cb15.setChecked(False)
            self.cb30.setChecked(False)
            self.cb60.setChecked(True)

        self.Config = value
        print(self.Config)
        print("config funtion state")

    @qasync.asyncSlot()
    async def read_temp(self):
        global loop
        global address_device
        #####################todo : start here
        print("start here ")
        # create a shared event object
        #event = asyncio.Event()
        # create and run the tasks
        #tasks = [asyncio.create_task(task(event, i)) for i in range(5)]
        # allow the tasks to start
        #print('Main blocking...')
        # await asyncio.sleep(0)
        # start processing in all tasks        # report a messagelobal data_received_event
        #print('Main setting the event')        #    print(f'Task {number} got {value}') cmd = "get_read_tmp"
        #event.set()        # await self.current_client.write(cmd.encode())
        # await for all tasks  to terminate        print("         Start the script         ")
        #_ = await asyncio.wait(tasks)


        #print("***********           task1 work ok !!!!           ***********")
        #t = [asyncio.create_task(task1(event, i)) for i in range(8)]
        #await asyncio.sleep(0)
        #event.set()
        #res = await asyncio.wait(t)
        #print(res)
        #print("************           task1 Finish !!!!       ***********")

        device = self.comboBox.currentData()
        print(f'    device To connect : {device}')
        print(f'    device address    : {device[1][0].address}')
        err = ""
        connected = False
        con_counter = 0
        num_of_tries = 10
        conn_timeout = 5
        print("     Finish init Before Connect   ")
        print("**********************************")

        print("         Start connect")
        address_device = device[1][0].address
        client = BleakClient(device[1][0].address, device=device[0])
        client1 = QBleakClient(device=device[0])

        print(client)
        print("         fetch        ")

        print("************           Run fetch start on testble.py  !!!!       ***********")
        await testble.run_fetch(device, device[1][0].address, loop ,99)
        print("**************************************************************")
        print("*******************      E     N   D   *************************")
        print("**************************************************************")
        err = ""
        connected = False
        conn_timeout = 2
        try:
            while not client.is_connected:
                print(time.strftime('%H-%M-%S'))
                try:
                    connected = await client.connect()

                except asyncio.CancelledError:
                    print("CancelledError - sample")
                    await client.disconnect()
                except Exception as e:
                    err = str(e)
                    await client.disconnect()

            if connected == False:
                print('wasn\'t able to connect :( {}'.format(err))
                return False
            else:
                print("Connected: {0}".format(connected))
                print("[Service CTS          ] {0}: {1}".format(CurrentTimeServiceUuidString, "CTS"))
                print("[Characteristic CTS   ] {0}: {1}".format(CurrentTimeCharacteristicUuidString, "CTS"))

                milliseconds_since_epoch = (round(time.time() * 1000))
                write_data = bytearray(struct.pack('q', milliseconds_since_epoch))
                print("Sending Set-Time command to EP (CT={0})".format(milliseconds_since_epoch))
                print(f'Sending cts Set-Time command to EP cmd {write_data}')

                print(f' client : {client}')
                print(f' write data  : {write_data}')

                try:
                    _value = await client.write_gatt_char(CurrentTimeCharacteristicUuidString, write_data)
                    #_value = bytes(await client.write_gatt_char(CurrentTimeCharacteristicUuidString, write_data))
                except Exception as e:
                    _value = str(e).encode()

                print("[Characteristic CTS   ] Write Value: {0} ".format(to_hex(write_data)))
                print("[Service Command          ] {0}: {1}".format(CommandServiceUUIDString, "Command"))
                print("[Characteristic Command   ] {0}: {1}".format(commandCharacteristicUUIDString, "Command"))
                print(f'         device To connect : {device}')
                print(f'         Finish connect - > status :  {connected}')
        except Exception as e:
            logger.error(e)
            return False
        print("=============================================================")

        #await testble.run_sample(device, device[1][0].address, ui, 99, 1, 1, 4, 0)

        print("-------------------------------------------------------------")
        #await built_in_self_test(device, device[1][0].address, ui,True)
        #await testble.run_fetch(device, device[1][0].address, loop,99)
        print("=============================================================")
        print("finish ")
        try:
            while connected is False and con_counter < num_of_tries:
                con_counter += 1
                print("info(connecting...try...{0}".format(con_counter))
                try:
                    connected = await client.connect(timeout=conn_timeout)
                    print(connected)
                except Exception as e:
                    err = str(e)
                    print("Connection fail...retrying...")

            if connected is False:
                # logger.error(err)
                print("error")
                return False
            else:
                print("Connected: {0}".format(connected))
                print("[Service CTS          ] {0}: {1}".format(CurrentTimeServiceUuidString, "CTS"))
                print("[Characteristic CTS   ] {0}: {1}".format(CurrentTimeCharacteristicUuidString, "CTS"))

                milliseconds_since_epoch = (round(time.time() * 1000))
                print(f'milliseconds_since_epoch : {milliseconds_since_epoch}')
                print("Sending Set-Time command to EP (CT={0})".format(milliseconds_since_epoch))
                write_data = bytearray(struct.pack('q', milliseconds_since_epoch))
                print(f'1        send data   --->>>  : {write_data}')

                write_data = bytearray(struct.pack('=H', 0))
                print(f'write_data : {write_data}')

                try:
                    _value = (await client.write_gatt_char(CurrentTimeCharacteristicUuidString,write_data))
                except Exception as e:
                    _value = str(e).encode()
                print(f'2        value : {_value}')

                try:
                    _value = bytes(await client.read_gatt_char(HardwareRevisionCharacteristicUuidString))
                except Exception as e:
                    _value = str(e).encode()
                print(f'3        value : {_value}')

                try:
                    _value = bytes(await client.read_gatt_char(FirmwareRevisionCharacteristicUuidString))
                except Exception as e:
                    _value = str(e).encode()
                print(f'4       firmware value : {_value}')

                fw_revision = _value.decode("utf-8")
                print("5        [FirmwareRevision str: {0} ".format(fw_revision))

                try:
                    _value = bytes(await client.read_gatt_char(SerialNumberCharacteristicUuidString))
                    print(_value)
                except Exception as e:
                    _value = str(e).encode()

                serial_number = _value.decode("utf-8")
                print("6        [SerialNumber str: {0} ".format(serial_number))
                print("7        [Characteristic CTS   ] Write Value: {0} ".format(write_data))
                print("8        [Service Command          ] {0}: {1}".format(TestingServiceUUIDString, "Command"))
                print("9        [Characteristic Command   ] {0}: {1}".format(TestingCharacteristicUUIDString, "Command"))
                write_data = bytearray(struct.pack('=H', 0))
                print("######################################################################")
                await client.start_notify(DataCharacteristicUUIDString, self.data_notification_handler)
                #todo:#await client.start_notify(DataCharacteristicUUIDString, data_notification_handler)
                write_data = bytearray(struct.pack('=H', 0))
                print(f'10 write_data : {write_data}')

                _value = await client.write_gatt_char(commandCharacteristicUUIDString, write_data)
                print(f'11')
                write_data = bytearray(b'\x02')
                _value = await client.write_gatt_char(commandCharacteristicUUIDString, write_data)
                print(f'12')
                _value = await client.write_gatt_char(commandCharacteristicUUIDString, write_data)
                print(f'13')
                print("done")

                try:
                    _value = await self.current_client.write_gatt_char(DataCharacteristicUUIDString, write_data)

                except Exception as e:
                    _value = str(e).encode()
                all_data_received = False
                DataNotificationState = 0


                try:
                    _value = await client.write_gatt_char(DataCharacteristicUUIDString, write_data)
                except Exception as e:
                    _value = str(e).encode()


                print(f'device address    : {device[1][0].address}')
                ## put here todo: sample here

                #command_id = 0  # SampleNow Command
                #sample_at_ts = round(time.time()) + 0

                # write_data = bytearray(
                #     struct.pack('=HHHHHI', command_id, sensor_id, odr, scale, duration, sample_at_ts))
                #
                # try:
                #     _value = await client.write_gatt_char(commandCharacteristicUUIDString, write_data)
                # except Exception as e:
                #     _value = str(e).encode()
                # #logger.info("[Characteristic Command   ] Write Value: {0} ".format(to_hex(write_data)))
                #
                # if return_sample_at_ts:
                #     return True, sample_at_ts
                # else:
                #     return True

                # global data_received_event
                # while all_data_received is False:
                #     #data_received_event.clear()
                #     #data_received_waiter_task = asyncio.create_task(self.waiter(data_received_event))
                #     try:
                #         await asyncio.wait_for(data_received_waiter_task, timeout=5)
                #
                #     except (asyncio.CancelledError, asyncio.TimeoutError) as e:
                #         print(e)
                #         all_data_received = True

                PacketsExpected = 2
                #await client.start_notify(TestingCharacteristicUUIDString, testing_notification_handler)
                # if (run_bist):
                #     write_data = bytearray(b'\x01')
                #     print("Sending 'run built in self test' command to EP ")
                #
                #     try:
                #         _value = await client.write_gatt_char(TestingCharacteristicUUIDString, write_data)
                #     except Exception as e:
                #         _value = str(e).encode()
                #
                #     print("[Characteristic Command   ] Write Value: {0} ".format(to_hex(write_data)))
                # else:
                #     write_data = bytearray(b'\x02')
                #     print("Sending 'get built in self test results' command to EP ")
                #
                #     try:
                #         _value = await client.write_gatt_char(TestingCharacteristicUUIDString, write_data)
                #     except Exception as e:
                #         _value = str(e).encode()
                #
                #     print("[Characteristic Command   ] Write Value: {0} ".format(to_hex(write_data)))

                    # while all_data_received is False:
                    #     data_received_event.clear()
                    #     data_received_waiter_task = asyncio.create_task(waiter(data_received_event))
                    #     try:
                    #         await asyncio.wait_for(data_received_waiter_task, timeout=5)
                    #     except asyncio.CancelledError:
                    #         logger.error("CancelledError - BUILT IN SELF TEST")
                    #     except asyncio.TimeoutError:
                    #         logger.error("Data receive timeout - BUILT IN SELF TEST")
                    #         return False
                    #
                    # await client.stop_notify(TestingCharacteristicUUIDString)
                    # data_as_json = cbor2.loads(binascii.a2b_hex(DataBuffer.hex()))
                    # logger.info(json.dumps(data_as_json, indent=4, sort_keys=True))

                return True
        except Exception as e:
            print(e)
            return False
        finally:
            #print("DisConnected: {0}".format(await client.disconnect()))
            print("script end")


    def data_notification_handler(self, _: BleakGATTCharacteristic, data: bytearray):
        print(data)
        global DataBytesExpected
        global DataBuffer
        global MetaDataBuffer
        global data_received_event
        global all_data_received
        global DataNotificationState
        global meta_sensor_id, meta_temp_avg, meta_sampling_freq, meta_timestamp, meta_num_of_samples, meta_overrun, meta_channel, meta_data_format, meta_data_unit, meta_scale
        print(data)
        data_received_event.set()

    @qasync.asyncSlot()
    async def handle_start_sample(self):
        # print(self.cb60)
        # cmd = "set_scale_60"
        # await self.current_client.write(cmd.encode())
        #cmd = "set_start_sp"
        #await self.current_client.write(cmd.encode())
        #####

        print("here we start ")
        device = self.comboBox.currentData()
        print(self._client)
        print(type(self._client))
        await testble.run_sample(self._client, device[1][0].address, loop, duration=4000, sensor_id=0,odr=0, scale=0)
        print("1111111111111 ")

        await testble.run_fetch(device, device[1][0].address, loop, 99)
        print("here we start ")
        #write to ep ( ep already connect )
        #write_data = bytearray(struct.pack('BBH', 0, 0, 0))
        #_value = await self.client.write_gatt_char(commandCharacteristicUUIDString, write_data)



    def savetodrive(self):
        print("upload to drive ")

    def show_graph(self):
        print("here")
        # df = px.data.tips()
        # fig = px.box(df, x="day", y="total_bill", color="smoker")
        # fig.update_traces(quartilemethod="exclusive") # or "inclusive", or "linear" by default
        # self.Webwidget.setHtml(fig.to_html(include_plotlyjs='cdn'))
        # file_path = os.path.abspath(os.path.join(report.halo, "aa.html"))
        # local_url = QUrl.fromLocalFile(file_path)
        # browser.load(local_url)

        mypath = (os.path.join(os.getcwd(), "report/halo"))
        # print(os.path.dirname(__file__).join("report/halo"))
        # print(os.path.join(os.getcwd()))
        print(mypath)
        self.Webwidget.load(QtCore.QUrl().fromLocalFile(mypath + '/Shaker_results3.html'))
        # fig1 = go.Figure(data=go.Bar(y=[2, 3, 1]))
        fig1 = go.Figure()
        fig1.write_html(mypath + '/Shaker_results3.html', auto_open=True)

    def combopb(self):
        print("PB ")
        print(self.comunes)

    @cached_property
    def devices(self):
        return list()

    @property
    def current_client(self):
        print("==========================FC -> current_client")
        return self._client

    def progBarUpdate(self, counter, Element):
        self.progressBar.setValue(int(100 / 64000 * counter))

    def hourUpdate(self, min, sec):
        # self.progressBar.setValue(int(100 / 64000 * counter))
        self.lable_time.setText(str(min))
        self.lable_time_2.setText(str(sec))

    def UiPrint(self, string):
        item = QtGui.QStandardItem(string)
        self.model.appendRow(item)
        self.listView.scrollToBottom()

    async def build_client(self, device):
        print("     MainWindows -> build_client Function Call -> ")
        if self._client is not None:
            await self._client.stop()
        print("     1.MainWindows build_client before :  {}".format(self._client))
        self._client = QBleakClient(device)
        print("     2.MainWindows build_client before :  {}".format(self._client))
        # self._client.messageChanged.connect(self.handle_message_changed)
        await self._client.start()  # main window call to qbleak method !
        print("     3.MainWindows finish build client")

    @qasync.asyncSlot()
    async def handle_pb3(self):
        print("=================='handle_pb3  =================")
        try:
            write_data = bytearray(struct.pack('=H', 2))
            print(write_data)
            await self.current_client.write(write_data) # send data
            print("write good")
        except Exception as e:
            _value = str(e).encode()
            print(f'             get error : -> : {_value}')

        print("get data")
        print("++++++++")
        await self.current_client.read_gatt()  # send data - to fix it !
        print("after call ")



        #await self._client.client.read_gatt_char(HardwareRevisionCharacteristicUuidString)  # second method
        #await self._client.client.read(HardwareRevisionCharacteristicUuidString)




        # try:
        #     _value = bytes(await self.client.read_gatt_char(HardwareRevisionCharacteristicUuidString))
        # except Exception as e:
        #     _value = str(e).encode()
        #     print(_value)
        # print(f'             2        value : {_value}')


        # message = "self.message_lineedit.text()"
        # if message:
        #     cmd = "set_scale_60"
        #     await self.current_client.write(cmd.encode())# one method
        #     await self._client.client.write_gatt_char(commandCharacteristicUUIDString, cmd.encode())# second method


        # try:
        #     print(type(self.client))
        #     print("pass 3")
        # except Exception as e:
        #     print(e)
        #     print("error 3")

        #
        # try:
        #     _value = bytes(await self.client.read_gatt_char(HardwareRevisionCharacteristicUuidString))
        # except Exception as e:
        #     _value = str(e).encode()
        # print(f'3        value : {_value}')

        # try:
        #     _value = bytes(await self._client.read_gatt_char(HardwareRevisionCharacteristicUuidString))
        # except Exception as e:
        #     _value = str(e).encode()
        #
        # hw_revision = _value.decode("utf-8")
        # hw = get_hw_type(hw_revision)
        # logger.info("[HardwareRevision str: {0} ".format(hw_revision))
        #
        # try:
        #     _value = bytes(await self._client.read_gatt_char(FirmwareRevisionCharacteristicUuidString))
        # except Exception as e:
        #     _value = str(e).encode()
        #
        # fw_revision = _value.decode("utf-8")
        # logger.info("[FirmwareRevision str: {0} ".format(fw_revision))
        #
        # try:
        #     _value = bytes(await self._client.read_gatt_char(SerialNumberCharacteristicUuidString))
        # except Exception as e:
        #     _value = str(e).encode()
        #
        # serial_number = _value.decode("utf-8")
        # logger.info("[SerialNumber str: {0} ".format(serial_number))
        #
        # #logger.info("Connected: {0}".format(connected))
        # logger.info("[Service Data         ] {0}: {1}".format(DataServiceUUIDString, "Data"))
        # logger.info("[Characteristic Data  ] {0}: {1}".format(DataCharacteristicUUIDString, "Data"))
        #

        #
        # client = self.current_client
        # print(client)
        # print(self._client)
        # global CommandServiceUUIDString, commandCharacteristicUUIDString
        # print("self.handle_pb3")
        # b = bytearray([0xa2, 0x61, 0x64, 0x19, 0x0f, 0xa0, 0x62, 0x63, 0x68, 0x86, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05])
        # # try:
        #
        #     try:
        #         _value = bytes(await client.read_gatt_char(HardwareRevisionCharacteristicUuidString))
        #     except Exception as e:
        #         _value = str(e).encode()
        #     print(_value)
        #
        #     try:
        #         _value = bytes(await client.client.read_gatt_char(HardwareRevisionCharacteristicUuidString))
        #     except Exception as e:
        #         _value = str(e).encode()
        #     print(_value)
        #
        #     await client.write_gatt_char(commandCharacteristicUUIDString, b)
        #     _value = await client.write_gatt_char(commandCharacteristicUUIDString, b)
        #     await self.current_client.write.write_gatt_char(CommandServiceUUIDString, b)
        #     _value = await self._client.write_gatt_char(CommandServiceUUIDString, b)
        #     # _value = bytes(await client.write_gatt_char(CurrentTimeCharacteristicUuidString, write_data))
        #     print(" Send msg : {} ".format(b))
        # except Exception as e:
        #     _value = str(e).encode()
        #     print(_value)
        # print("done ")

    @qasync.asyncSlot()
    async def handle_connect(self):
        print("MainWindows handle_connect - Function Call")
        # get combobox obj
        device = self.comboBox.currentData()
        MainWindows.UiPrint(ui, "        Try connect to:  {}".format(device))
        MainWindows.UiPrint(ui, "        Build Client Obj")
        # build client Obj & Connect
        print("==================================================================")
        print("MainWindows handle_connect : self_client before build :  {}".format(self._client))
        if isinstance(device[1][0], BLEDevice):
            await self.build_client(device[1][0])
            # self.log_edit.appendPlainText("connected")
        "handle_connect after  build :  {}".format(self._client)
        print("==================================================================")
        # todo:  save as json file & csv and later check times
        self.FileName = device[1][0].name + self.Config + ".txt"
        self.FileNameJson = device[1][0].name + self.Config + ".json"

        MainWindows.UiPrint(ui, "        File to Save Data :  {}".format(self.FileName))
        MainWindows.UiPrint(ui, "        File to Save Data New :  {}".format(self.FileNameJson))

        # PB State on Ui -  here connect / Disconnect
        self.pb_disconnect.setEnabled(True)
        self.pb_connect.setEnabled(False)
        self.comboBox.setEnabled(False)
        self.pb_scan.setEnabled(False)
        self.pb_start_sample.setEnabled(True)
        self.pb_stop_sample.setEnabled(True)
        self.cb60.setEnabled(True)
        self.cb15.setEnabled(True)
        self.cb30.setEnabled(True)
        ##stop sample disconect

        global file , fileJson  # in start scan open file
        file = open(self.FileName, "a")
        file.truncate(0) # remove all data
        #fileJson = open(self.FileNameJson, "w")


    @qasync.asyncSlot()
    async def handle_scan(self):
        # done
        self.pb_scan.setEnabled(False)
        print("hande_scan function call ")
        MainWindows.UiPrint(ui, "Start Scanning For BLE")

        self.devices.clear()
        self.comboBox.clear()
        devices = await BleakScanner.discover(timeout=4, return_adv=True)
        self.devices.extend(devices)
        # "address", "name", "details", "_rssi", "_metadata"
        print("==============")
        print(devices)
        print("==============")
        # 1.list preper for gui
        dev = []
        try:
            devices = (sorted(devices.items(), key=lambda key_val: str(key_val[1][0].name)))
        except :
            print(" none type value ")
        #we can order todo: add smart filter by val

        for i, device in enumerate(self.devices):
                dev.append(device)

        #dev.sort(key=lambda x: x.name)
        # 2 Add to gui
        for i, device in enumerate(devices):
            self.comboBox.insertItem(i, (str(device[1][0].name)+ "  " + str(device[1][1].rssi)), device)

        MainWindows.UiPrint(ui, "Stop Scanning For BLE")
        self.pb_scan.setChecked(False)
        self.pb_scan.setEnabled(True)

        # if somthing found in scan
        if len(dev) > 0:
            self.comboBox.setEnabled(True)
            self.pb_connect.setEnabled(True)

    # def ComboboxItemPressed(self):
    #     print("ComboboxItemPressed")
    #     global deviceComboboxBLE
    #     deviceComboboxBLE = self.comboBox.currentText()
    #     print("here   ---> ComboboxItemPressed")
    #     print(self)

    def handle_message_changed(self, message):
        self.log_edit.appendPlainText(f"msg: {message.decode()}")
        print("hello")

    @qasync.asyncSlot()
    async def handle_send(self):
        if self.current_client is None:
            return
        # message = self.message_lineedit.text()
        # if message:
        print(" +++  Send - Somthing  +++ ")
        await self.current_client.write("0x23")

    @qasync.asyncSlot()
    async def handle_disc(self):
        print("")
        # file Close  #  todo: Comment maybe to add also here ! ?
        await self._client.stop()  # disconnect and call disonnect 2 + Close File
        self.pb_scan.setEnabled(True)
        self.pb_connect.setEnabled(True)
        self.comboBox.setEnabled(True)
        self.pb_disconnect.setEnabled(False)
        self.pb_start_sample.setEnabled(False)
        self.pb_stop_sample.setEnabled(False)

        print(self._client)
        self.end_sample(self._client.databuffer)


def main():
    global ui
    global loop
    global data_received_event
    console = Console()
    try:
        app = QApplication(sys.argv)
        loop = qasync.QEventLoop(app)
        asyncio.set_event_loop(loop)
        mainwindow = QtWidgets.QMainWindow()
        ui = MainWindows(window=mainwindow)
        mainwindow.show()
    except BaseException as e:
        console.print_exception(show_locals=True)
    with loop:
        loop.run_forever()


if __name__ == "__main__":
    main()

####### from here scatch
# 1.pip install pipreqs - ok
# 2.pipreqs - ok
# 3.install all dep pip install -r requirements.txt

## protocol :
# 0- samplecounter now
# 1 - clear bat
# 2   clear fs

#to deleta all FS-   [2, 0, 0 , 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] len 14
#                     0, 0, 99, 0, 0, 0, 0, 0, 16, 39, 0, 0, 0, 0
                #sample     all                10k
                #cts send - Mon, 24 Jun 2024 21:58:43 GMT all the time !
#
# @timeit
# def math_harder():
#     [x**(x%17)^x%17 for x in range(1,5555)]
# math_harder()
