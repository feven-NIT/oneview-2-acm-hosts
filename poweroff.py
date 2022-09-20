#!/usr/bin/env python3

import logging
import json
from pprint import pprint
from hpeOneView.oneview_client import OneViewClient
import sys, os

def poweroff(serialNumber):
  print("poweroff ", serialNumber)
  
  oneview_client = OneViewClient.from_environment_variables()
  server_profiles = oneview_client.server_profiles
  all_profiles = server_profiles.get_all()
  server_hardwares = oneview_client.server_hardware
  server_hardware_all = server_hardwares.get_all()
  profile_templates = oneview_client.server_profile_templates
  all_templates = profile_templates.get_all()
  
  server = None
  
  for serv in server_hardware_all:
    if serialNumber == serv['serialNumber'].lower():
      server = serv
      break

  if server is None:
    print("hardware with specified serial number not found")
    return 3     

  hardware = server_hardwares.get_by_uri(server['uri'])

  configuration = {
    "powerState": "Off",
    "powerControl": "PressAndHold"
  }
  server_power = hardware.update_power_state(configuration)
  
  return 0
    
if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
      sys.exit(poweroff(argv[1]))
    else:
      print("1 argument needed : serialNumber")
      sys.exit(1)
