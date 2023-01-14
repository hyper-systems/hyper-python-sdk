#!/usr/bin/env python3
import os
from hyper_systems.devices import Device, Schema
from hyper_systems.http import Client

HYPER_API_URL = "https://<your organization name>.hyper.systems/api"
HYPER_API_KEY = "<insert your api key here>"
HYPER_SITE_ID = 1
SCHEMA_FILE = "<path to schema_file>/<schema file name>.json"

print("Initializing the device...")
schema = Schema.load(SCHEMA_FILE)
device = Device.from_schema(schema, device_id="00:11:22:33:44:55")

print("Attributes:")
print(device.attributes)

def my_device_reboot(v):
    if v:
        print("rebooting")


print("Setting device attribute values...")
device.sht31_ambient_temperature_0 = -30.14
device.veml7700_ambient_light_2 = 200.112

print("Device values:")
print(device.values)

print("Device message:")
print(device.message)

print("Unsetting a device attribute value...")
del device.sht31_ambient_temperature_0

print("Unsetting all device attribute values...")
device.clear()

print("Binding a callback for a device attribute...")
device.on_reboot_1_4_update = my_device_reboot

print("Setting device attribute values (again)...")
device.sht31_ambient_temperature_0 = -30.14
device.veml7700_ambient_light_2 = 200.112

print("Publishing the device message...")
client = Client(api_url=HYPER_API_URL, api_key=HYPER_API_KEY, site_id=HYPER_SITE_ID)
client.publish_device_message(device.message)
