#!/usr/bin/env python
import socket
import xmltodict
import json
from nxapi_lib import *

def main():
    
    module = AnsibleModule(
        argument_spec = dict(
            interface=dict(required=True),
            admin_state=dict(default='up',choices=['up', 'down']),
            mac_addr=dict(default=None),
            duplex=dict(default=None),
            state=dict(default='present',choices=['present','absent','default']),
            speed=dict(default=None),
            description=dict(default=None),
            mode=dict(choices=['layer2','layer3']),
            host=dict(required=True),
            username=dict(default='cisco'),
            password=dict(default='!cisco123!'),
        ),
        supports_check_mode=False
    )   
    
    results = {}


    host = socket.gethostbyname(module.params['host'])
    un = module.params['username']
    pw = module.params['password']

    interface = module.params['interface']
    mac_addr = module.params['mac_addr']
    duplex = module.params['duplex']
    admin_state = module.params['admin_state']
    speed = module.params['speed']
    description = module.params['description']
    mode = module.params['mode']

    state = module.params['state']

    device = Device(ip=host,username=un,password=pw)
    device.open()

    changed = False
    dry_run = False


    interface = interface.lower()
    args = dict(interface=interface,admin_state=admin_state,description=description,\
            duplex=duplex,speed=speed,mac_addr=mac_addr,mode=mode)

    keys = get_intf_args(interface).keys()

    proposed = {}
    for k in keys:
        temp = args.get(k,None)
        if temp:
            proposed[k] = temp

    existing = getInterface(device,interface)

    for ex in existing.keys():
        if ex not in keys:
            existing.pop(ex)

    intf_type = getType(interface)
    
    i_list = []
    
    #############################################################################################
    # the follow if/conditional block is used only if a "keyword" is used for the interface param
    # this section is NOT idempotent
    # only when the interface param is a single interface, the module is idempotent
    # will be fixed soon so that it is always idempotent even when using keywords
    ############################################################################################

    if interface in ['svi','loopback','all','ethernet','portchannel']:
        interface_dict = getInterfaces_dict(device)
        if interface != 'all':
            i_list = interface_dict[interface]
        else:
            for k,v in interface_dict.iteritems():
                if v:
                    for each in v:
                        if each != 'mgmt0':
                            i_list.append(each)
        commands = []
        cmds = ''
        for each_intf in i_list:
            if state == 'default':
                commands.append('default interface ' + each_intf)
            elif state == 'absent':
                if each_intf.lower().startswith('eth'):
                    commands.append('default interface ' + each_intf)
                else:
                    commands.append('no interface ' + each_intf)
            else:
                cmd = 'interface ' + each_intf
                commands.append(cmd)
                if admin_state == 'up':
                    commands.append('no shutdown')
                elif admin_state == 'down':
                    commands.append('shutdown')
                if each_intf.lower().startswith('eth'):
                    if speed:
                        commands.append('speed ' + speed)
                    if duplex:
                        commands.append('duplex ' + duplex)
                if mode:
                    if each_intf.lower().startswith('eth') or each_intf.lower().startswith('po'):
                        if mode == 'layer2':
                            commands.append('switchport')
                        else:
                            commands.append('no switchport')

        if commands:
            cmds = converttoCiscostring(commands)

        if commands and dry_run == False:
            push = device.config(cmds)
            changed = True

    ########################################################
    #####   If the interface keywords are not being used
    #####   The following conditional block IS idempotent
    ########################################################
    else:

        delta = set()
        commands = []

        if intf_type == 'unknown':
            results['changed'] = changed
            results['error'] = 'unknown interface type found'
            return results

        if state == 'absent':
            if existing:
                if intf_type in ['svi','loopback','portchannel'] and interface != 'vlan1'.lower():
                    cmds = deleteInterface(device,interface)
                    commands.append(cmds)
                    changed = True
                elif intf_type in ['ethernet'] or interface == 'vlan1'.lower():
                    cmds = defaultInterface(device,interface)
                    commands.append(cmds)
                    changed = True
                elif intf_type == 'management':
                    cmds = 'CAUTION: cannot remove or default the management interface. NXAPI uses this interface.'
            else:
                cmds = 'No commands sent (1).'
        elif state == 'present':
            delta = set(proposed.iteritems()).difference(existing.iteritems())
            if not existing:
                cmds = configInterface(device,delta,interface)
                commands.append(cmds)
                changed = True
            else:
                if delta:
                    cmds = configInterface(device,delta,interface)
                    commands.append(cmds)
                    changed = True
                else:
                    cmds = 'No commands sent (2).'
        elif state == 'default':
            if existing:
                cmds = defaultInterface(device,interface)
                commands.append(cmds)
                changed = True 
        
        cmds = ''
        for each in commands:
            temp = converttoCiscostring(each)
            cmds += temp 

        if cmds and dry_run == False:
            push = device.config(cmds)

        postrun = getInterface(device,interface)
        

        results['proposed'] = proposed
        results['existing'] = existing
        results['new'] = postrun
    
    results['state'] = state
    results['commands'] = cmds
    results['changed'] = changed

    module.exit_json(cmds=cmds,**results)

from ansible.module_utils.basic import *  
main()
