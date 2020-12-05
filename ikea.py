#!/usr/bin/env python3
"""
This file generates debug information about your Tradfri network.

To run the script, do the following:
$ pip3 install pytradfri
$ Download this file (debug_info.py)
$ python3 debug_info.py <IP>

Where <IP> is the address to your IKEA gateway. The first time
running you will be asked to input the 'Security Code' found on
the back of your IKEA gateway.
"""
# Hack to allow relative import above top level package
import sys
import os

from pytradfri import Gateway
from pytradfri.api.libcoap_api import APIFactory
from pytradfri.error import PytradfriError
from pytradfri.util import load_json, save_json
import json
import uuid
import argparse

CONFIG_FILE = "tradfri_standalone_psk.conf"

class Ikea:
    api = ""
    devices_command = ""
    devices_commands = ""
    gateway = ""
    devices = ""
    lights = ""

    def __init__(self, ip, key):
        folder = os.path.dirname(os.path.abspath('.'))  # noqa
        sys.path.insert(0, os.path.normpath("%s/.." % folder))  # noqa

        conf = load_json(CONFIG_FILE)

        try:
            identity = conf[ip].get("identity")
            psk = conf[ip].get("key")
            api_factory = APIFactory(host=ip, psk_id=identity, psk=psk)
        except KeyError:
            identity = uuid.uuid4().hex
            api_factory = APIFactory(host=ip, psk_id=identity)

            try:
                psk = api_factory.generate_psk(key)
                print("Generated PSK: ", psk)

                conf[ip] = {"identity": identity, "key": psk}
                save_json(CONFIG_FILE, conf)
            except AttributeError:
                raise PytradfriError(
                    "Please provide the 'Security Code' on the "
                    "back of your Tradfri gateway using the "
                    "-K flag."
                )


        self.api = api_factory.request
        self.gateway = Gateway()
        self.updateDevices()

    def jsonify(self, input):
        return json.dumps(
            input,
            sort_keys=True,
            indent=4,
            ensure_ascii=False,
        )

    def updateDevices(self):
        self.devices_command = self.gateway.get_devices()
        self.devices_commands = self.api(self.devices_command)
        self.devices = self.api(self.devices_commands)
        self.lights = [dev for dev in self.devices if dev.has_light_control]

    def getStatus(self, light):
        self.updateDevices()
        return self.lights[light].light_control.lights[0].state

    def turnOnLight(self, light, value):
        self.api(self.lights[light].light_control.set_dimmer(value))

# ikea = Ikea("192.168.178.101", "ro8fRf1TbgJpFwdt")
# print(ikea.getStatus(0))
# ikea.turnOnLight(0, 0)
# print(ikea.getStatus(0))
