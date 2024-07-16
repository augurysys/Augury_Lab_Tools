import os
AUTOMATION_ETHERNET_SWITCH_IP = "192.168.1.130"
AUTOMATION_ROUTER_IP = "172.20.4.2"
AUTOMATION_ROUTER_USER = "root"
AUTOMATION_ROUTER_PASSWORD = "1*Augury"

TIMEOUT_FOR_EP_DFU = 360

# Will use this when version number that is already installed on Node > version number that we want to test
NODE_MASK_VERSION = "09.99.99"

EP_HW_REVISION = "apus_alpha"

EP_MASK_VERSION = "09.09.1099"

USERNAME = "automation+de+ca@notaugury.com"

# TODO: verify and describe values calculation
MIN_NUM_OF_WIFI_RECEIVED_BYTES_PER_HOUR_NODE_1 = 0  # 830615
MIN_NUM_OF_WIFI_RECEIVED_BYTES_PER_HOUR_NODE_2 = 0  # 476975
MIN_NUM_OF_WIFI_TRANSMITTED_BYTES_PER_HOUR_NODE_1 = 0  # 1820172
MIN_NUM_OF_WIFI_TRANSMITTED_BYTES_PER_HOUR_NODE_2 = 0  # 2501300

MAX_NUM_OF_WIFI_RECEIVED_BYTES_PER_HOUR_NODE_1 = 1146921
MAX_NUM_OF_WIFI_RECEIVED_BYTES_PER_HOUR_NODE_2 = 735486
MAX_NUM_OF_WIFI_TRANSMITTED_BYTES_PER_HOUR_NODE_1 = 3152300
MAX_NUM_OF_WIFI_TRANSMITTED_BYTES_PER_HOUR_NODE_2 = 3682646

TURNED_OFF_EP_SERIAL_NUMBER = "10003234"
TURNED_OFF_EP_MAC_ADDRESS = "D6:B6:B1:C8:2A:16"

# The CI setups channel has the latest versions of the devices
CI_SETUP_CHANNEL = "ci_setup"

# The mounted dir in the docker run command. This dir can be accessed from the Jenkins agent.
SHARED_REPORTS_DIR = "/tmp/reports"
FAILURES_SUMMARY_FILE_NAME = "failures_summary.txt"
FAILURES_TABLE_SUMMARY_FILE_NAME = "samples_table_failures_summary.csv"
FAILED_METRIC_FILE_NAME = "failed_metric_file.txt"

NORMAL_SAMPLING_INTERVAL = 3600

# Mix sampling configuration
NEW_DEFAULT_FULL_TO_SMALL_RATIO = 4
NEW_DEFAULT_FULL_SAMPLE_INSTANCE = 6
OLD_DEFAULT_FULL_TO_SMALL_RATIO = 1
OLD_DEFAULT_FULl_SAMPLE_INSTANCE = 1
DEFAULT_LONG_SAMPLE_DURATION = 4

# Vibration (Shaker) Test variables

SHAKERS_LIST = {
    "Big_Shaker": 'Dev1/ao0',
    "Small_Shaker": 'Dev1/ao1'
}

WHITE_LIST = {
  "wave_packet": [89, 281, 479, 677, 877, 1069, 1259, 1459, 1657, 1847, 2039, 2237, 2437, 2633, 2833, 3023, 3217, 3413, 3613, 3803, 4001, 4201, 4397, 4591, 4793, 4993, 5189, 5387, 5573, 5779, 5953, 6151],
  "sweep": None,
  "chirp": None
}

VIBRATION_METHODS = ["wave_packet", "sweep"]  # TODO: chirp, white_noise

CTC_SENSITIVITY = 100  # [mV/g], CTC reference sensor datasheet

DEFAULT_SHAKER_TYPE = 'Dev1/ao0'
DEFAULT_VIBRATION_METHOD = "wave_packet"

VIBRATION_THRESHOLD = 100
FREQ_ERROR_THRESHOLD = 1
RMS_THRESHOLD = 1
RESET_ID_IN_BIG_QUERY = 1000
UNSUPPORTED_FIELD_IN_EP_CONFIG = "unsupported field"
EP_DEVICE_CONFIG_WITH_UNSUPPORTED_FIELD = {
    "samplingConfig": {
        "sensors": [
            "vib0",
            "vib1",
            "vib2",
            "mag",
            "temperature"
        ],
        UNSUPPORTED_FIELD_IN_EP_CONFIG: True,
        "samplingIntervalSec": 900,
        "samplingFreqHz": 20833,
        "samplingDurationSec": 4
    },

    "mixSample":
        {
            "fullToSmallRatio": 4,
            "fullSampleInstance": 6
        },
    "advPattern": {
        "pattern": 1,
        "intervalMSec": 2000
    }
}
ETHERNET_PORT_WAIT_TILL_AVAILABLE_IN_SECONDS = 30