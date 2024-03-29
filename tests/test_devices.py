#!/usr/bin/env python3
import os, sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(PROJECT_ROOT)
from hyper_systems.devices import Schema, Device

SCHEMA_FILE = os.path.join(PROJECT_ROOT, "./tests/hyper_device_schema_12.json")

schema = Schema.load(SCHEMA_FILE)
dev1 = Device.from_schema(schema, device_id="DE:AD:BE:EF:FF:00")

# create device with invalid macaddr
try:
    dev2_invalid = Device.from_schema(schema, device_id="DE:AD:BE")
    assert False
except ValueError as err:
    assert err.args[0] == "the vendor device id must a valid MAC address"

# check printing
assert str(dev1) == "'<Device12: DE:AD:BE:EF:FF:00>'"

# check attributes
assert dev1.attributes == [
    "publish_interval_s_6",
    "uptime_ms_5",
    "reboot_1_4",
    "firmware_version_data_1_3",
    "veml7700_ambient_light_2",
    "sht31_relative_humidity_1",
    "sht31_ambient_temperature_0",
]

# set valid attribute value
assert dev1.sht31_ambient_temperature_0 is None
dev1.sht31_ambient_temperature_0 = 2.2
assert dev1.sht31_ambient_temperature_0 == 2.2

# unset attribute value
del dev1.sht31_ambient_temperature_0
assert dev1.sht31_ambient_temperature_0 is None

# set invalid attr type
try:
    dev1.veml7700_ambient_light_2 = "invalid"
    assert False
except TypeError as err:
    assert (
        err.args[0]
        == "value 'invalid' for attribute 'veml7700_ambient_light_2' has an invalid type: expected float, got str"
    )

# set invalid attr type by slot
try:
    dev1[2] = "invalid"
    assert False
except TypeError as err:
    assert (
        err.args[0]
        == "value 'invalid' for attribute slot 2 has an invalid type: expected float, got str"
    )

# set write attribute binding
assert dev1.on_publish_interval_s_6_update is None
dev1.on_publish_interval_s_6_update = print

# unset write attribute binding
del dev1.on_publish_interval_s_6_update
assert dev1.on_publish_interval_s_6_update is None

# set invalid bind type
try:
    dev1.on_publish_interval_s_6_update = 5
    assert False
except TypeError as err:
    assert (
        err.args[0]
        == "value for attribute 'on_publish_interval_s_6_update' must be a function, got int"
    )

# dispatch values to incorrect vendor device id
invalid_vendor_device_id_msg = {"vendor_device_id": "YY:XX:XX:XX:XX:XX"}
try:
    dev1.dispatch(invalid_vendor_device_id_msg)
    assert False
except ValueError as err:
    assert (
        err.args[0]
        == "tried to dispatch a message for a wrong device, expected message for id 'DE:AD:BE:EF:FF:00', but got a message for 'YY:XX:XX:XX:XX:XX'"
    )

# dispatch invalid value
dev1.on_publish_interval_s_6_update = lambda x: None
invalid_value_msg = {"vendor_device_id": "DE:AD:BE:EF:FF:00", "values": {"6": "hello"}}
try:
    dev1.dispatch(invalid_value_msg)
    assert False
except TypeError as err:
    assert (
        err.args[0]
        == "incoming value 'hello' for attribute 'publish_interval_s_6' has an invalid type: expected int, got str"
    )

# dispatch valid value
expected_value_attr_6 = None


def set_value_attr_6(x):
    global expected_value_attr_6
    expected_value_attr_6 = x


dev1.on_publish_interval_s_6_update = set_value_attr_6
invalid_value_msg = {"vendor_device_id": "DE:AD:BE:EF:FF:00", "values": {"6": 42}}
assert dev1.publish_interval_s_6 is None
dev1.dispatch(invalid_value_msg)
assert dev1.publish_interval_s_6 == 42
assert expected_value_attr_6 == 42

# clear all values
dev1.uptime_ms_5 = 100
dev1.veml7700_ambient_light_2 = 321.60
assert dev1.uptime_ms_5 == 100 and dev1.veml7700_ambient_light_2 == 321.60
dev1.clear()
assert dev1.uptime_ms_5 is None and dev1.veml7700_ambient_light_2 is None

# set value by slot
dev1[5] = 1000
assert dev1[5] == 1000

# set value by slot out of bounds
try:
    dev1[999] = 42
    assert False
except TypeError as err:
    assert (
        err.args[0]
        == "cannot set value: no read attribute for slot 999 found in device with schema 12"
    )

print(dev1)
print(dev1.message)

# device with keyed attributes
SCHEMA_FILE = os.path.join(PROJECT_ROOT, "./tests/hyper_device_schema_91.json")

schema = Schema.load(SCHEMA_FILE)
dev_keyed = Device.from_schema(schema, device_id="ABC1234")

print(dev_keyed.attributes)
print(dev_keyed._rvalues)
dev_keyed[0]["plastic"] = 1234
print(dev_keyed[0])

dev_keyed2 = Device.from_schema(schema, device_id="ABC4321")

dev_keyed2.temperature_by_material_0["plastic"] = 4321
print(dev_keyed2.temperature_by_material_0)

dev_keyed3 = Device.from_schema(schema, device_id="ABC4321")
try:
    dev_keyed3.temperature_by_material_0 = 5
    assert False
except TypeError as err:
    assert (
        err.args[0]
        == "value '5' for attribute 'temperature_by_material_0' has an invalid type: expected dict, got int"
    )

dev_keyed4 = Device.from_schema(schema, device_id="ABC4321")
try:
    dev_keyed4.temperature_by_material_0[42] = 10
    assert False
except TypeError as err:
    assert (
        err.args[0]
        == "keyed attribute slot `0` (`temperature_by_material_0`) must be a dict[string, float]"
    )

dev_keyed5 = Device.from_schema(schema, device_id="ABC4321")
try:
    dev_keyed4[0][42] = 10
    assert False
except TypeError as err:
    assert (
        err.args[0]
        == "keyed attribute slot `0` (`temperature_by_material_0`) must be a dict[string, float]"
    )
