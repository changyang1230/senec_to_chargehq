import time
import json
import requests
from senec import Senec
import configparser

# Read the configuration file
config = configparser.ConfigParser()
config.read('config.ini')

# Initialize the Senec API object and the JSON payload
api = Senec(config['DEFAULT']['senec_ip'])
if not api:
    sys.exit()

# Initialize the Charge HQ API endpoint
endpoint = "https://api.chargehq.net/api/public/push-solar-data"

while True:
    try:
        # Get fresh data
        data = api.get_values()
        
        # Extract the values and change the units to kW
        production_kw = data["ENERGY"]['GUI_INVERTER_POWER']/1000
        net_import_kw = data["ENERGY"]['GUI_GRID_POW']/1000
        consumption_kw = data["ENERGY"]['GUI_HOUSE_POW']/1000
        imported_kwh = data["STATISTIC"]['LIVE_GRID_IMPORT']
        exported_kwh = data["STATISTIC"]['LIVE_GRID_EXPORT']        
        battery_discharge_kw = data["ENERGY"]['GUI_BAT_DATA_POWER'] / (-1000)
        battery_soc = data["ENERGY"]['GUI_BAT_DATA_FUEL_CHARGE'] / 100

        # Create the JSON payload
        payload = {
            "apiKey": config['DEFAULT']['api_key'],
            "siteMeters": {
                "production_kw": production_kw,
                "net_import_kw": net_import_kw,
                "consumption_kw": consumption_kw,
                "imported_kwh": imported_kwh,
                "exported_kwh": exported_kwh,
                "battery_discharge_kw": battery_discharge_kw,
                "battery_soc": battery_soc
            }
        }

        # Send the JSON payload to the API endpoint
        response = requests.post(endpoint, json=payload)
        print(response.text)
    except Exception as e:
        print(e)

    # Wait for 30 seconds before repeating
    time.sleep(30)
