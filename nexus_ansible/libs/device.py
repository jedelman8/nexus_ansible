#!/usr/bin/env python

import xmltodict
import json
import yaml
import sys

from nxapi import NXAPI

class Device():
  
  def __init__(self,username='cisco',password='!cisco123!',ip='192.168.200.50'):
    
    self.username = username
    self.password = password
    self.ip = ip
    
  def open(self):

    self.sw1 = NXAPI()
    self.sw1.set_target_url('http://'+self.ip+'/ins')
    self.sw1.set_username(self.username)
    self.sw1.set_password(self.password)

  def show(self,command,fmat='xml'):

    self.sw1.set_msg_type('cli_show')
    self.sw1.set_out_format(fmat)
    self.sw1.set_cmd(command)

    return self.sw1.send_req()

  def config(self,command,fmat='xml'):

    self.sw1.set_msg_type('cli_conf')
    self.sw1.set_out_format(fmat)
    self.sw1.set_cmd(command)

    return self.sw1.send_req()