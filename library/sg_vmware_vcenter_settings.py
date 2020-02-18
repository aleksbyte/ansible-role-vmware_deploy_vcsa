#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2018, Christian Kotte <christian.kotte@gmx.de>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

try:
    from pyVmomi import vim, vmodl
except ImportError:
    pass

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.vmware import PyVmomi, vmware_argument_spec
from ansible.module_utils._text import to_native

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: vmware_vcenter_settings
short_description: Configures general settings on a vCenter server
description:
- This module can be used to configure the vCenter server general settings (except the statistics).
- The statistics can be configured with the module C(vmware_vcenter_statistics).
version_added: 2.8
author:
- Christian Kotte (@ckotte)
notes:
- Tested with vCenter Server Appliance (vCSA) 6.5 and 6.7
requirements:
- python >= 2.6
- PyVmomi
options:
    database:
        description:
            - The database settings for vCenter server.
            - 'Valid attributes are:'
            - '- C(max_connections) (int): Maximum connections. (default: 50)'
            - '- C(task_cleanup) (bool): Task cleanup. (default: true)'
            - '- C(task_retention) (int): Task retention (days). (default: 30)'
            - '- C(event_cleanup) (bool): Event cleanup. (default: true)'
            - '- C(event_retention) (int): Event retention (days). (default: 30)'
        type: dict
        default: {
            max_connections: 50,
            task_cleanup: True,
            task_retention: 30,
            event_cleanup: True,
            event_retention: 30,
        }
    runtime_settings:
        description:
            - The unique runtime settings for vCenter server.
            - 'Valid attributes are:'
            - '- C(unique_id) (int): vCenter server unique ID.'
            - '- C(managed_address) (str): vCenter server managed address.'
            - '- C(vcenter_server_name) (str): vCenter server name. (default: FQDN)'
        type: dict
    user_directory:
        description:
            - The user directory settings for the vCenter server installation.
            - 'Valid attributes are:'
            - '- C(timeout) (int): User directory timeout. (default: 60)'
            - '- C(query_limit) (bool): Query limit. (default: true)'
            - '- C(query_limit_size) (int): Query limit size. (default: 5000)'
            - '- C(validation) (bool): Mail Validation. (default: true)'
            - '- C(validation_period) (int): Validation period. (default: 1440)'
        type: dict
        default: {
            timeout: 60,
            query_limit: True,
            query_limit_size: 5000,
            validation: True,
            validation_period: 1440,
        }
    mail:
        description:
            - The settings vCenter server uses to send email alerts.
            - 'Valid attributes are:'
            - '- C(server) (str): Mail server'
            - '- C(sender) (str): Mail sender address'
        type: dict
    snmp_receivers:
        description:
            - SNMP trap destinations for vCenter server alerts.
            - 'Valid attributes are:'
            - '- C(snmp_receiver_1_url) (str): Primary Receiver ULR. (default: "localhost")'
            - '- C(snmp_receiver_1_enabled) (bool): Enable receiver. (default: True)'
            - '- C(snmp_receiver_1_port) (int): Receiver port. (default: 162)'
            - '- C(snmp_receiver_1_community) (str): Community string. (default: "public")'
            - '- C(snmp_receiver_2_url) (str): Receiver 2 ULR. (default: "")'
            - '- C(snmp_receiver_2_enabled) (bool): Enable receiver. (default: False)'
            - '- C(snmp_receiver_2_port) (int): Receiver port. (default: 162)'
            - '- C(snmp_receiver_2_community) (str): Community string. (default: "")'
            - '- C(snmp_receiver_3_url) (str): Receiver 3 ULR. (default: "")'
            - '- C(snmp_receiver_3_enabled) (bool): Enable receiver. (default: False)'
            - '- C(snmp_receiver_3_port) (int): Receiver port. (default: 162)'
            - '- C(snmp_receiver_3_community) (str): Community string. (default: "")'
            - '- C(snmp_receiver_4_url) (str): Receiver 4 ULR. (default: "")'
            - '- C(snmp_receiver_4_enabled) (bool): Enable receiver. (default: False)'
            - '- C(snmp_receiver_4_port) (int): Receiver port. (default: 162)'
            - '- C(snmp_receiver_4_community) (str): Community string. (default: "")'
        type: dict
        default: {
            snmp_receiver_1_url: 'localhost',
            snmp_receiver_1_enabled: True,
            snmp_receiver_1_port: 162,
            snmp_receiver_1_community: 'public',
            snmp_receiver_2_url: '',
            snmp_receiver_2_enabled: False,
            snmp_receiver_2_port: 162,
            snmp_receiver_2_community: '',
            snmp_receiver_3_url: '',
            snmp_receiver_3_enabled: False,
            snmp_receiver_3_port: 162,
            snmp_receiver_3_community: '',
            snmp_receiver_4_url: '',
            snmp_receiver_4_enabled: False,
            snmp_receiver_4_port: 162,
            snmp_receiver_4_community: '',
        }
    timeout_settings:
        description:
            - The vCenter server connection timeout for normal and long operations.
            - 'Valid attributes are:'
            - '- C(normal_operations) (int) (default: 30)'
            - '- C(long_operations) (int) (default: 120)'
        type: dict
        default: {
            normal_operations: 30,
            long_operations: 120,
        }
    logging_options:
        description:
            - The level of detail that vCenter server usesfor log files.
        type: str
        choices: ['none', 'error', 'warning', 'info', 'verbose', 'trivia']
        default: 'info'
extends_documentation_fragment: vmware.documentation
'''

EXAMPLES = r'''
- name: Configure vCenter general settings
  vmware_vcenter_settings:
    hostname: '{{ vcenter_hostname }}'
    username: '{{ vcenter_username }}'
    password: '{{ vcenter_password }}'
    settings:
    - 
    validate_certs: no
  delegate_to: localhost
'''

RETURN = r'''
results:
    description: metadata about vCenter settings
    returned: always
    type: dict
    sample: {
        "changed": false,
        "db_event_cleanup": true,
        "db_event_retention": 30,
        "db_max_connections": 50,
        "db_task_cleanup": true,
        "db_task_retention": 30,
        "directory_query_limit": true,
        "directory_query_limit_size": 5000,
        "directory_timeout": 60,
        "directory_validation": true,
        "directory_validation_period": 1440,
        "logging_options": "info",
        "mail_sender": "vcenter@vcenter01.example.com",
        "mail_server": "mail.example.com",
        "msg": "vCenter settings already configured properly",
        "runtime_managed_address": "192.168.1.10",
        "runtime_server_name": "vcenter01.example.com",
        "runtime_unique_id": 1,
        "timeout_long_operations": 120,
        "timeout_normal_operations": 30
    }
'''

class VmwareVcenterSettings(PyVmomi):
    """Manage settings for a vCenter server"""

    def __init__(self, module):
        super(VmwareVcenterSettings, self).__init__(module)

        if not self.is_vcenter():
            self.module.fail_json(msg="You have to connect to a vCenter server!")

def main():
    """Main"""
    argument_spec = vmware_argument_spec()
    argument_spec.update(dict(
        settings=dict(type='list'),
    ))

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    vcenter = VmwareVcenterSettings(module)
    option_manager = vcenter.content.setting

    """Manage settings for a vCenter server"""
    result = dict(changed=False, msg='')
    change_option_list = []
    changed = False
    changed_list = []

    # Check all general settings, except statistics
    for desired_setting in module.params.get("settings"):
        desired_setting_key = next(iter(desired_setting))
        settingFound = False
        for current_setting in option_manager.setting:
            if desired_setting_key == current_setting.key:
                settingFound = True
                if desired_setting[desired_setting_key] != current_setting.value:
                    changed = True
                    changed_list.append(desired_setting_key)
                    result[desired_setting_key] = desired_setting[desired_setting_key]
                    change_option_list.append(
                        vim.option.OptionValue(key=desired_setting_key, value=desired_setting[desired_setting_key])
                    )

        if settingFound == False:
            module.warn("The setting %s has not been found on this vCenter - skipping." % str(desired_setting))

    if changed:
        if module.check_mode:
            changed_suffix = ' would be changed'
        else:
            changed_suffix = ' changed'
        if len(changed_list) > 2:
            message = ', '.join(changed_list[:-1]) + ', and ' + str(changed_list[-1])
        elif len(changed_list) == 2:
            message = ' and '.join(changed_list)
        elif len(changed_list) == 1:
            message = changed_list[0]
        message += changed_suffix
        if not module.check_mode:
            try:
                option_manager.UpdateOptions(changedValue=change_option_list)
            except (vmodl.fault.SystemError, vmodl.fault.InvalidArgument) as invalid_argument:
                module.fail_json(
                    msg="Failed to update option(s) as one or more OptionValue contains an invalid value: %s" %
                    to_native(invalid_argument.msg)
                )
            except vim.fault.InvalidName as invalid_name:
                module.fail_json(
                    msg="Failed to update option(s) as one or more OptionValue objects refers to a "
                    "non-existent option : %s" % to_native(invalid_name.msg)
                )
    else:
        message = "vCenter settings already configured properly"
    result['changed'] = changed
    result['msg'] = message

    module.exit_json(**result)


if __name__ == '__main__':
    main()
