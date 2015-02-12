#!/usr/bin/env python

from device import Device
import xmltodict
import json

##################################################################
######    VLAN RESOURCES  START    ###############################
##################################################################


def getVLAN(device, vid):

	command = 'show vlan id ' + vid
	data = device.show(command)
	data_dict = xmltodict.parse(data[1])
	vlan = {}
	
	try:
		v = data_dict['ins_api']['outputs']['output']['body']['TABLE_vlanbriefid']['ROW_vlanbriefid']
		
		vlan['vlan_id'] = str(v['vlanshowbr-vlanid-utf'])
		vlan['name'] = str(v['vlanshowbr-vlanname'])
		vlan['vlan_state'] = str(v['vlanshowbr-vlanstate'])
		
		state = str(v['vlanshowbr-shutstate'])

		if state == 'shutdown':
			vlan['admin_state'] = 'down'
		elif state == 'noshutdown':
			vlan['admin_state'] = 'up'
		
	except:
		return vlan 

	return vlan

def getVLANS(device):

	command = 'show vlan'
	data = device.show(command)
	data_dict = xmltodict.parse(data[1])
	vlans = []
	try:
		vlan_list = data_dict['ins_api']['outputs']['output']['body']['TABLE_vlanbrief']['ROW_vlanbrief']
		for v in vlan_list:
			vlan = {}
			vlan['vlan_id'] = str(v['vlanshowbr-vlanid-utf'])
			vlan['name'] = str(v['vlanshowbr-vlanname'])
			vlan['vlan_state'] = str(v['vlanshowbr-vlanstate'])
			state = str(v['vlanshowbr-shutstate'])
			if state == 'shutdown':
				vlan['admin_state'] = 'down'
			elif state == 'noshutdown':
				vlan['admin_state'] = 'up'
				vlans.append(vlan)
	except:
		vlan = getVLAN(device,'1')
		vlans.append(vlan)

	return vlans

def get_list_of_vlans(device):

	command = 'show vlan'
	data = device.show(command)
	data_dict = xmltodict.parse(data[1])
	vlans = []
	
	try:
		vlan_list = data_dict['ins_api']['outputs']['output']['body']['TABLE_vlanbrief']['ROW_vlanbrief']
		for v in vlan_list:
			vlans.append(str(v['vlanshowbr-vlanid-utf']))
	except:
		vlans.append('1')

	# returns a list of VLAN IDs configured on the switch
	return vlans


def get_vlan_list(vlans):
	final = []
	new = []
	if ',' in vlans:
		new = vlans.split(',')
	else:
		new.append(vlans)
	for each in new:
		if not '-' in each:
			final.append(each)
		else:
			low = int(each.split('-')[0])
			high = int(each.split('-')[1])
			for num in range(low,high+1):
				vlan = str(num)
				final.append(vlan)

	# returns a VLAN list with an input of a single VLAN or range, e.g. 2-10,12,25,30-40
	return final


def configVLAN(device,vlan,vid):
	#vlan currently received as set
	#then converted to a dictionary

	VLAN_ARGS = {
		'name':'name {name}',
		'vlan_state':'state {vlan_state}',
		'admin_state':'shutdown'
		 }

	vlan = dict(vlan)
	commands = []
	for param,value in vlan.iteritems():
		if  param != 'admin_state':
			if value:
				command = VLAN_ARGS.get(param,'DNE').format(**vlan)
		else:
			if value == 'up':
				command = 'no shutdown'
			elif value == 'down':
				command = 'shutdown'
		if command and command != 'DNE':
			commands.append(command)

	commands.insert(0,'vlan ' + vid)
	commands.append('exit')

	return commands
	
def deleteVLAN(device,vid):
	commands = []
	commands.append('no vlan ' + vid)
	return commands


##################################################################
######    VLAN RESOURCES  END    #################################
##################################################################

##################################################################
######    INTERFACE RESOURCES  START  ############################
##################################################################


# defaulting an interace is not idempotent
# let cisco know you can't get description of svi interface through show interface vlan N cmd

def getType(interface):

	if interface.upper().startswith('ET'):
		return 'ethernet'
	elif interface.upper().startswith('VL'):
		return 'svi'
	elif interface.upper().startswith('LO'):
		return 'loopback'
	elif interface.upper().startswith('MG'):
		return 'management'
	elif interface.upper().startswith('PO'):
		return 'portchannel'
	else:
		return 'unknown'

def getInterface(device, interface):

	command = 'show interface ' + interface
	intf_type = getType(interface)
	i = {}
	interface = {}
	try:
		data = device.show(command)
		data_dict = xmltodict.parse(data[1])	
		i = data_dict['ins_api']['outputs']['output']['body']['TABLE_interface']['ROW_interface']
	except:
		pass
	
	if i:
		interface['interface'] = str(i['interface'])
		interface['type'] = intf_type
		interface['ip_addr'] = str(i.get('eth_ip_addr',None))
		interface['ip_mask'] = str(i.get('eth_ip_mask',None))
		if intf_type == 'ethernet':
			#print data_dict['body']['TABLE_interface']['ROW_interface'].keys()
			interface['state'] = str(i.get('state','N/A'))
			interface['admin_state'] = str(i.get('admin_state','N/A'))
			interface['mac_addr'] = str(i.get('eth_hw_addr','N/A'))
			interface['bia_addr'] = str(i.get('eth_bia_addr','N/A'))
			interface['description'] = str(i.get('desc',None))
			interface['duplex'] = str(i.get('eth_duplex','N/A'))
			interface['speed'] = str(i.get('eth_speed','N/A'))
			interface['media'] = str(i.get('eth_media','N/A'))
			interface['eth_hw'] = str(i.get('eth_hw_desc','N/A'))
			interface['auto_neg'] = str(i.get('eth_autoneg','N/A'))
			interface['mode'] = str(i.get('eth_mode','layer3'))
			if interface['mode'] == 'access':
				interface['mode'] = 'layer2'
		elif intf_type == 'svi':
			interface['state'] = str(i.get('svi_line_proto','N/A'))
			interface['admin_state'] = str(i.get('svi_admin_state','N/A'))
			interface['mac_addr'] = str(i.get('svi_mac','N/A'))
			interface['description'] = str(i.get('desc','unable_to_read_nxapi_bug'))
			interface['note'] = 'admin_state will be down if no interfaces in vlan'
		elif intf_type == 'loopback':
			interface['admin_state'] = str(i.get('state','N/A'))
			interface['description'] = str(i.get('desc',None))
		elif intf_type == 'management':
			interface['admin_state'] = str(i.get('state','N/A'))
			interface['description'] = str(i.get('desc',None))
			interface['mac_addr'] = str(i.get('eth_hw_addr','N/A'))
			interface['bia_addr'] = str(i.get('eth_bia_addr','N/A'))
			interface['state'] = str(i.get('state','N/A'))
			interface['eth_hw'] = str(i.get('eth_hw_desc','N/A'))
			interface['duplex'] = str(i.get('eth_duplex','N/A'))
			interface['speed'] = str(i.get('eth_speed','N/A'))
			interface['auto_neg'] = str(i.get('eth_autoneg','N/A'))
		elif intf_type == 'portchannel':
			interface['description'] = str(i.get('desc',None))
			interface['admin_state'] = str(i.get('admin_state',None))
			interface['state'] = str(i.get('state',None))
			interface['duplex'] = str(i.get('eth_duplex','N/A'))
			interface['speed'] = str(i.get('eth_speed','N/A'))
			interface['mode'] = str(i.get('eth_mode','layer3'))
			if interface['mode'] == 'access':
				interface['mode'] = 'layer2'

	return interface

def getInterfaces_dict(device):

	command = 'show interface status'
	data = device.show(command)
	data_dict = xmltodict.parse(data[1])
	interfaces = {
		'ethernet':[],
		'svi':[],
		'loopback':[],
		'management':[],
		'portchannel':[],
		'unknown':[]
		}
	
	interface_list = data_dict['ins_api']['outputs']['output']['body']['TABLE_interface']['ROW_interface']
	for i in interface_list:
		intf = i['interface']
		intf_type = getType(intf)

		interfaces[intf_type].append(intf)

	return interfaces

def getInterfaces(device):

	command = 'show interface status'
	data = device.show(command)
	data_dict = xmltodict.parse(data[1])
	interfaces = []
	interface_list = data_dict['ins_api']['outputs']['output']['body']['TABLE_interface']['ROW_interface']
	for i in interface_list:
		intf = i['interface']
		interface = getInterface(device,intf)
		interfaces.append(interface)
	return interfaces

def get_intf_args(interface):	
	intf_type = getType(interface)

	arguments = {'admin_state':'','description':'description '}
	if intf_type == 'ethernet':
		arguments['mac_addr'] = 'mac-address {mac_addr}'
		arguments['duplex'] = 'duplex {duplex}'
		arguments['speed'] = 'speed {speed}'
		arguments['mode'] = ''
	elif intf_type == 'loopback':
		pass
	elif intf_type == 'management':
		arguments['duplex'] = 'duplex {duplex}'
		arguments['speed'] = 'speed {speed}'
	elif intf_type == 'svi':
		arguments['mac_addr'] = 'mac-address {mac_addr}'
	elif intf_type == 'portchannel':
		arguments['mode'] = ''

	return arguments

def configInterface(device,interface,intf):

	INTERFACE_ARGS = get_intf_args(intf)

	commands = []
	interface = dict(interface)
	for k,v in interface.iteritems():
		if k == 'admin_state':
			if v == 'up':
				command = 'no shutdown'
			elif v == 'down':
				command = 'shutdown'
		elif k == 'mode':
			if v == 'layer2':
				command = 'switchport'
			elif v == 'layer3':
				command = 'no switchport'
		else:
			command = INTERFACE_ARGS.get(k,'xx') + v
			#command = INTERFACE_ARGS.get(k,'DNE').format(**interface)

		if command and not command.startswith('DNE'):
			commands.append(command)
	commands.insert(0,'interface ' + intf)
	
	return commands


def defaultInterface(device,interface):
	commands = []
	commands.append('default interface ' + interface)
	return commands

def deleteInterface(device,interface):
	commands = []
	commands.append('no interface ' + interface)
	return commands

##################################################################
######    INTERFACE RESOURCES  END ###############################
##################################################################



##################################################################
######    GENERAL START   ########################################
##################################################################


def converttoCiscostring(cmds):
	c = ' ; '.join(cmds)
	return c + ' ; '
	
##################################################################
######    GENERAL END   ##########################################
##################################################################

