# pylint: disable=W0212
"""
device
"""
import json
import uuid
from datetime import datetime
from . import device_schema_gen

class Schema(device_schema_gen.DeviceSchema):
    @classmethod
    def load(cls, file_path):
        with open(file_path, encoding="utf-8") as schema_file:
            schema_dict = json.load(schema_file)
            self = device_schema_gen.DeviceSchema.from_json(schema_dict)
            return self


def make_attr_slug(slot, attr):
    prefix = None
    if attr.name:
        prefix = "".join([x.lower() if x.isalnum() else "_" for x in attr.name])
    elif attr.quantity:
        prefix = attr.quantity.replace(" ", "_").lower()
    else:
        prefix = attr.format.kind.lower()
    return prefix + "_" + str(slot)


def make_attr_doc(attribute):
    unit_str = " measured in " + attribute.unit if attribute.unit is not None else ""
    quantity_str = (
        " and represents " + attribute.quantity
        if attribute.quantity is not None
        else ""
    )
    return "%s\n\n This attribute has format %s%s%s." % (
        attribute.name,
        attribute.format.kind,
        quantity_str,
        unit_str,
    )


def get_valid_type_for_attr(attr):
    attr_py_type = None
    valid_values = None
    if attr.format.kind in (
        "Int8",
        "Int16",
        "Int32",
        "Int64",
        "Uint8",
        "Uint16",
        "Uint32",
        "Uint64",
    ):
        attr_py_type = int
    elif attr.format.kind in ("Float32", "Float64"):
        attr_py_type = float
    elif attr.format.kind == "Bool":
        attr_py_type = bool
    elif attr.format.kind == "Data":
        attr_py_type = str
    elif attr.format.kind == "Enum":
        attr_py_type = int
        valid_values = list(map(int, attr.format.value.value.keys()))
    else:
        raise Exception("Invalid attribute format " + str(attr.format))
    return (attr_py_type, valid_values)


def set_slot_value(self, slot, value):
    if not isinstance(slot, int):
        raise TypeError("the attribute slot must be an int value")
    slot_key = str(slot)

    # Check if slot is within bounds.
    if slot_key not in self._rvalues:
        raise TypeError(
            "cannot set value: no read attribute for slot %s found in device with schema %d"
            % (slot_key, self.device_class_id)
        )

    # Check the attribute type.
    attr = self.schema.attributes[slot_key]
    attr_py_type, valid_rvalues = get_valid_type_for_attr(attr)
    if not isinstance(value, attr_py_type):
        raise TypeError(
            "value '%s' for attribute slot %d has an invalid type: expected %s, got %s"
            % (value, slot, attr_py_type.__name__, type(value).__name__)
        )
    if valid_rvalues is not None and value not in valid_rvalues:
        raise TypeError(
            "value %s for enum attribute slot %d is invalid: expected one of: %s"
            % (value, slot, list(valid_rvalues))
        )

    self._rvalues[slot_key] = value


def get_slot_value(self, slot):
    if not isinstance(slot, int):
        raise TypeError("the attribute slot must be an int value")
    return self._rvalues[str(slot)]


def make_read_attr_property(slot, attr):
    slug = make_attr_slug(slot, attr)
    attr_py_type, valid_rvalues = get_valid_type_for_attr(attr)

    def attr_get(self):
        return self._rvalues[slot]

    def attr_set(self, x):
        if not isinstance(x, attr_py_type):
            raise TypeError(
                "value '%s' for attribute '%s' has an invalid type: expected %s, got %s"
                % (x, slug, attr_py_type.__name__, type(x).__name__)
            )
        if valid_rvalues is not None and x not in valid_rvalues:
            raise TypeError(
                "value %s for enum attribute '%s' is invalid: expected one of: %s"
                % (x, slug, list(valid_rvalues))
            )
        self._rvalues[slot] = x

    def attr_del(self):
        self._rvalues[slot] = None

    prop = property(
        fget=attr_get, fset=attr_set, fdel=attr_del, doc=make_attr_doc(attr)
    )
    return (slug, prop)


def make_write_attr_property(slot, attr):
    slug = make_attr_slug(slot, attr)

    def attr_get(self):
        return self._wbinds[slot]

    def attr_set(self, f):
        if not callable(f):
            raise TypeError(
                "value for attribute 'on_%s_update' must be a function, got %s"
                % (slug, type(f).__name__)
            )
        self._wbinds[slot] = f

    def attr_del(self):
        self._wbinds[slot] = None

    prop = property(
        fget=attr_get, fset=attr_set, fdel=attr_del, doc=make_attr_doc(attr)
    )
    return ("on_" + slug + "_update", prop)


def get_device_message(self):
    """
    Produces a dict with the final message.
    """
    message_uuid = str(uuid.uuid4())
    collected_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "message_uuid": message_uuid,
        "created_time": collected_time,
        "vendor_device_id": self.vendor_device_id,
        "device_class_id": self.device_class_id,
        "values": {
            slot: value for (slot, value) in self._rvalues.items() if value is not None
        },
    }


def get_device_values(self):
    """
    Produces the dict of all set attribute values.
    """
    values = dict()
    for attr in self.attributes:
        try:
            val = getattr(self, attr)
            # ignore unset attribute attralues (None)
            if val:
                values[attr] = val
        except AttributeError:
            pass

    return values


def device_repr(self):
    return repr("<%s: %s>" % (type(self).__name__, self.vendor_device_id))


def clear_values(self):
    """
    Set all attribute values to None.
    """
    for slot in self._rvalues.keys():
        self._rvalues[slot] = None


def dispatch(self, message):
    if message["vendor_device_id"] != self.vendor_device_id:
        raise ValueError(
            "tried to dispatch a message for a wrong device, expected message for id '%s', but got a message for '%s'"
            % (self.vendor_device_id, message["vendor_device_id"])
        )
    for (slot, value) in message["values"].items():
        attr = self.schema.attributes[slot]
        attr_py_type, valid_rvalues = get_valid_type_for_attr(attr)
        slug = make_attr_slug(slot, attr)

        if not isinstance(value, attr_py_type):
            raise TypeError(
                "incoming value '%s' for attribute '%s' has an invalid type: expected %s, got %s"
                % (value, slug, attr_py_type.__name__, type(value).__name__)
            )
        if valid_rvalues is not None and value not in valid_rvalues:
            raise TypeError(
                "incoming value %s for enum attribute '%s' is invalid: expected one of: %s"
                % (value, slug, list(valid_rvalues))
            )
        if not attr.access.write:
            raise TypeError(
                "received incoming value %s for read-only attribute '%s'"
                % (value, slug)
            )

        if slot in self._rvalues:
            self._rvalues[slot] = value
        if slot in self._wbinds and self._wbinds[slot] is not None:
            f = self._wbinds[slot]
            f(value)


def validate_vendor_device_id(vendor_device_id_format, id):
    if vendor_device_id_format.kind == "Macaddr":
        if len(id) != 17:
            raise ValueError("the vendor device id must a valid MAC address")


class Device:
    def __init__(self, *args, **kwargs):
        raise TypeError(
            "Device class should not be initialized directly, please use Device.from_schema"
        )

    @classmethod
    def from_schema(cls, schema, device_id):
        """
        A smart constructor function for a device described by a given schema.
        """
        validate_vendor_device_id(schema.vendor_device_id_format, device_id)

        rattrs = {
            slot: attr for (slot, attr) in schema.attributes.items() if attr.access.read
        }
        wattrs = {
            slot: attr
            for (slot, attr) in schema.attributes.items()
            if attr.access.write
        }
        rattrs_props = dict(
            make_read_attr_property(slot, attr) for (slot, attr) in rattrs.items()
        )
        wattrs_props = dict(
            make_write_attr_property(slot, attr) for (slot, attr) in wattrs.items()
        )
        schema_attrs = {
            "vendor_device_id": device_id.upper(),
            "device_class_id": schema.id,
            "values": property(get_device_values),
            "message": property(get_device_message),
            "dispatch": dispatch,
            "schema": schema,
            "clear": clear_values,
            "__setitem__": set_slot_value,
            "__getitem__": get_slot_value,
            "attributes": [
                make_attr_slug(slot, attr) for (slot, attr) in schema.attributes.items()
            ],
            "_rvalues": {slot: None for slot in rattrs},
            "_wbinds": {slot: None for slot in wattrs},
            "__repr__": device_repr,
            "__doc__": (schema.name + "\n" + schema.description),
            "__slots__": (),
        }
        type_name = "Device" + str(schema.id)
        props = {**schema_attrs, **rattrs_props, **wattrs_props}
        cls = type(type_name, (), props)
        return cls()
