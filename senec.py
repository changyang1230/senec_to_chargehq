#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Library to get a lot of useful data out of Senec appliances.

Tested with: SENEC.Home V3 hybrid duo

Kudos:
* SYSTEM_STATE_NAME taken from https://github.com/mchwalisz/pysenec
"""
from numpy import empty
import requests
import struct
import logging

__author__ = "Nicolas Inden"
__copyright__ = "Copyright 2022, Nicolas Inden"
__credits__ = ["Nicolas Inden", "Mikołaj Chwalisz"]
__license__ = "Apache-2.0 License"
__version__ = "1.0.3"
__maintainer__ = "Nicolas Inden"
__email__ = "nico@smashnet.de"
__status__ = "Production"

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',level=logging.INFO)
log = logging.getLogger("Senec")

class Senec():

    def __init__(self, device_ip):
        self.device_ip = device_ip
        self.read_api  = f"http://{device_ip}/lala.cgi"

    def get_values(self, request_json = {}):
        if not request_json: request_json = BASIC_REQUEST
        try:
            response = requests.post(self.read_api, json=request_json)
            if response.status_code == 200:
                res = self.__decode_data(response.json())
                return self.__substitute_system_state(res)
            else:
                log.warning(f"Status code {response.status_code}")
                return {"error": f"Status code {response.status_code}"}
        except requests.Timeout:
            errmsg = f"{self.device_ip}: Timeout while accessing Senec box."
            log.warning(errmsg)
            return {"error": errmsg}
        except requests.ConnectionError:
            errmsg = f"{self.device_ip}: Connection error while accessing Senec box."
            log.warning(errmsg)
            return {"error": errmsg}
        except requests.exceptions.JSONDecodeError as e:
            errmsg = f"{self.device_ip}: Could not decode JSON response: {e}"
            log.warning(errmsg)
            return {"error": errmsg}
        except Exception as e:
            errmsg = f"{self.device_ip}: Other exception: {e}"
            log.warning(errmsg)
            return {"error": errmsg}

    def get_all_values(self):
        request_json = {"STATISTIC": {},"ENERGY": {},"FEATURES": {},"LOG": {},"SYS_UPDATE": {},"WIZARD": {},"BMS": {},"BAT1": {},"BAT1OBJ1": {},"BAT1OBJ2": {},"BAT1OBJ3": {},"BAT1OBJ4": {},"PWR_UNIT": {},"PV1": {},"FACTORY": {},"GRIDCONFIG": {}}
        return self.get_values(request_json)

    def __decode_data(self, data):
        return { k: self.__decode_data_helper(v) for k, v in data.items() }

    def __decode_data_helper(self, data):
        if isinstance(data, str):
            return self.__decode_value(data)
        if isinstance(data, list):
            return [self.__decode_value(val) for val in data]
        if isinstance(data, dict):
            return { k: self.__decode_data_helper(v) for k, v in data.items() }

    def __decode_value(self, value):
        if value.startswith("fl_"):
            return struct.unpack('!f', bytes.fromhex(value[3:]))[0]
        if value.startswith("u8_"):
            return struct.unpack('!B', bytes.fromhex(value[3:]))[0]
        if value.startswith("i3_") or value.startswith("i8_") or value.startswith("u3_") or value.startswith("u1_"):
            return int(value[3:], 16)
        if value.startswith("st_"):
            return value[3:]
        return value

    def __substitute_system_state(self, data):
        system_state = data['STATISTIC']['CURRENT_STATE']
        try:
            data['STATISTIC']['CURRENT_STATE'] = SYSTEM_STATE_NAME[system_state]
        except KeyError as e:
            log.error(f"Failed substituting system state: {e}")
            data['STATISTIC']['CURRENT_STATE'] = f"unknown ({system_state})"
        finally:
            return data

BASIC_REQUEST = {
    'STATISTIC': {
        'CURRENT_STATE': '',                # Current state of the system (int, see SYSTEM_STATE_NAME)
        'LIVE_BAT_CHARGE_MASTER': '',       # Battery charge amount since installation (kWh)
        'LIVE_BAT_DISCHARGE_MASTER': '',    # Battery discharge amount since installation (kWh)
        'LIVE_GRID_EXPORT': '',             # Grid export amount since installation (kWh)
        'LIVE_GRID_IMPORT': '',             # Grid import amount since installation (kWh)
        'LIVE_HOUSE_CONS': '',              # House consumption since installation (kWh)
        'LIVE_PV_GEN': '',                  # PV generated power since installation (kWh)
        'MEASURE_TIME': ''                  # Unix timestamp for above values (ms)
    },
    'ENERGY': {
        'GUI_BAT_DATA_CURRENT': '',         # Battery charge current: negative if discharging, positiv if charging (A)
        'GUI_BAT_DATA_FUEL_CHARGE': '',     # Remaining battery (percent)
        'GUI_BAT_DATA_POWER': '',           # Battery charge power: negative if discharging, positiv if charging (W)
        'GUI_BAT_DATA_VOLTAGE': '',         # Battery voltage (V)
        'GUI_GRID_POW': '',                 # Grid power: negative if exporting, positiv if importing (W)
        'GUI_HOUSE_POW': '',                # House power consumption (W)
        'GUI_INVERTER_POWER': '',           # PV production (W)
        'STAT_HOURS_OF_OPERATION': ''       # Appliance hours of operation
    },
    'BMS': {
        'CHARGED_ENERGY': '',               # List: Charged energy per battery
        'DISCHARGED_ENERGY': '',            # List: Discharged energy per battery
        'CYCLES': ''                        # List: Cycles per battery
    },
    'PV1': {
        'MPP_CUR': '',                      # List: MPP current (A)
        'MPP_POWER': '',                    # List: MPP power (W)
        'MPP_VOL': '',                      # List: MPP voltage (V)
        'POWER_RATIO': '',                  # Grid export limit (percent)
        'P_TOTAL': ''                       # ?
    },
    'FACTORY': {
        'DESIGN_CAPACITY': '',              # Battery design capacity (Wh)
        'MAX_CHARGE_POWER_DC': '',          # Battery max charging power (W)
        'MAX_DISCHARGE_POWER_DC': ''        # Battery max discharging power (W)
    }
}

SYSTEM_STATE_NAME = {
    0: "INITIAL STATE",
    1: "ERROR INVERTER COMMUNICATION",
    2: "ERROR ELECTRICY METER",
    3: "RIPPLE CONTROL RECEIVER",
    4: "INITIAL CHARGE",
    5: "MAINTENANCE CHARGE",
    6: "MAINTENANCE READY",
    7: "MAINTENANCE REQUIRED",
    8: "MAN. SAFETY CHARGE",
    9: "SAFETY CHARGE READY",
    10: "FULL CHARGE",
    11: "EQUALIZATION: CHARGE",
    12: "DESULFATATION: CHARGE",
    13: "BATTERY FULL",
    14: "CHARGE",
    15: "BATTERY EMPTY",
    16: "DISCHARGE",
    17: "PV + DISCHARGE",
    18: "GRID + DISCHARGE",
    19: "PASSIVE",
    20: "OFF",
    21: "OWN CONSUMPTION",
    22: "RESTART",
    23: "MAN. EQUALIZATION: CHARGE",
    24: "MAN. DESULFATATION: CHARGE",
    25: "SAFETY CHARGE",
    26: "BATTERY PROTECTION MODE",
    27: "EG ERROR",
    28: "EG CHARGE",
    29: "EG DISCHARGE",
    30: "EG PASSIVE",
    31: "EG PROHIBIT CHARGE",
    32: "EG PROHIBIT DISCHARGE",
    33: "EMERGANCY CHARGE",
    34: "SOFTWARE UPDATE",
    35: "NSP ERROR",
    36: "NSP ERROR: GRID",
    37: "NSP ERROR: HARDWRE",
    38: "NO SERVER CONNECTION",
    39: "BMS ERROR",
    40: "MAINTENANCE: FILTER",
    41: "SLEEPING MODE",
    42: "WAITING EXCESS",
    43: "CAPACITY TEST: CHARGE",
    44: "CAPACITY TEST: DISCHARGE",
    45: "MAN. DESULFATATION: WAIT",
    46: "MAN. DESULFATATION: READY",
    47: "MAN. DESULFATATION: ERROR",
    48: "EQUALIZATION: WAIT",
    49: "EMERGANCY CHARGE: ERROR",
    50: "MAN. EQUALIZATION: WAIT",
    51: "MAN. EQUALIZATION: ERROR",
    52: "MAN: EQUALIZATION: READY",
    53: "AUTO. DESULFATATION: WAIT",
    54: "ABSORPTION PHASE",
    55: "DC-SWITCH OFF",
    56: "PEAK-SHAVING: WAIT",
    57: "ERROR BATTERY INVERTER",
    58: "NPU-ERROR",
    59: "BMS OFFLINE",
    60: "MAINTENANCE CHARGE ERROR",
    61: "MAN. SAFETY CHARGE ERROR",
    62: "SAFETY CHARGE ERROR",
    63: "NO CONNECTION TO MASTER",
    64: "LITHIUM SAFE MODE ACTIVE",
    65: "LITHIUM SAFE MODE DONE",
    66: "BATTERY VOLTAGE ERROR",
    67: "BMS DC SWITCHED OFF",
    68: "GRID INITIALIZATION",
    69: "GRID STABILIZATION",
    70: "REMOTE SHUTDOWN",
    71: "OFFPEAK-CHARGE",
    72: "ERROR HALFBRIDGE",
    73: "BMS: ERROR OPERATING TEMPERATURE",
    74: "FACOTRY SETTINGS NOT FOUND",
    75: "BACKUP POWER MODE - ACTIVE",
    76: "BACKUP POWER MODE - BATTERY EMPTY",
    77: "BACKUP POWER MODE ERROR",
    78: "INITIALISING",
    79: "INSTALLATION MODE",
    80: "GRID OFFLINE",
    81: "BMS UPDATE NEEDED",
    82: "BMS CONFIGURATION NEEDED",
    83: "INSULATION TEST",
    84: "SELFTEST",
    85: "EXTERNAL CONTROL",
    86: "ERROR: TEMPERATURESENSOR",
    87: "GRID OPERATOR: CHARGE PROHIBITED",
    88: "GRID OPERATOR: DISCHARGE PROHIBITED",
    89: "SPARE CAPACITY",
    90: "SELFTEST ERROR",
    91: "EARTH FAULT",
    92: "PV-MODE",
    93: "REMOTE DISCONNECTION",
    94: "ERROR DRM0",
    95: "BATTERY DIAGNOSIS"
}

if __name__ == "__main__":
    api = Senec("IP_OF_YOUR_SENEC_APPLIANCE")
    print(api.get_values())
