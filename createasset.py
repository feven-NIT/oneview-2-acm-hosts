#!/usr/bin/env python3

import logging
import json
from pprint import pprint
from hpeOneView.oneview_client import OneViewClient
import sys, os

def createAsset(templateName, serialNumber, serverName):
  print("createAsset ", templateName,serialNumber,serverName)
  
  oneview_client = OneViewClient.from_environment_variables()
  server_profiles = oneview_client.server_profiles
  all_profiles = server_profiles.get_all()
  server_hardwares = oneview_client.server_hardware
  server_hardware_all = server_hardwares.get_all()
  profile_templates = oneview_client.server_profile_templates
  all_templates = profile_templates.get_all()

  serv_template = None
  for template in all_templates:
    if template['name'] == templateName:
      serv_template = template
      break
      
  if serv_template is None:
    print("server template ", templateName," is not found")
    return 2
  
  server = None
  
  for serv in server_hardware_all:
    if serialNumber == serv['serialNumber'].lower():
      server = serv
      break

  if server is None:
    print("hardware with specified serial number not found")
    return 3     
  if server['serverProfileUri'] is not None:
    print("a server profile already exists for this hardware")
    return 4
  if server['powerState'] != 'Off':
    print("hardware should be Off")
    return 5
  if server['maintenanceMode'] != False:
    print("hardware is in maintenance mode")
    return 6
  if server['model'] != 'ProLiant BL460c Gen9':
    print("hardware model does not match 'ProLiant BL460c Gen9'")
    return 7
  if server['state'] != 'NoProfileApplied':
    print("a profile is already applied to this hardware")
    return 8
  if server['status'] == 'Critical':
    print("hardware is in Critical state")
    return 9

  ls =  {'controllers': [{'deviceSlot': 'Embedded',
                           'driveWriteCache': 'Unmanaged',
                           'importConfiguration': False,
                           'initialize': True,
                           'logicalDrives': [],
                           'mode': 'HBA',
                           'predictiveSpareRebuild': 'Unmanaged'}],
          'reapplyState': 'NotApplying',
          'sasLogicalJBODs': []}
  options = dict(
    name=serverName,
    serverHardwareUri=server['uri'],
    serverProfileTemplateUri=serv_template['uri'],
    localStorage=ls
  )
  profile = oneview_client.server_profiles.create(options, force=True)

  options = dict(serverProfileTemplateUri=serv_template['uri'])
  profile.patch(operation="replace", path="/templateCompliance", value="Compliant")
  return 0
    
if __name__ == '__main__':
    from sys import argv

    if len(argv) == 4:
      sys.exit(createAsset(argv[1],argv[2],argv[3]))
    else:
      print("3 arguments needed : templateName, serialNumber, serverName")
      sys.exit(1)
