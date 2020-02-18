#!/usr/bin/python

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
module: vcenter_scheduled_tasks
short_description: JPMC module to manage scheduled task on vCenter
description:
- Only removal at the moment.
version_added: '2.4'
author:
- Manuel Perrot
requirements:
- pyVmomi
'''

EXAMPLES = r'''
- name: Remove all scheduled tasks
  vcenter_scheduled_tasks:
    hostname: '{{ vcenter_hostname }}'
    username: '{{ vcenter_username }}'
    password: '{{ vcenter_password }}'
    remove_unmanaged_tasks: true
    managed_tasks: []
  delegate_to: localhost
'''

RETURN = r'''
licenses:
    description: list of tasks - it can be empty
    returned: always
    type: list
    sample:
    - f600d-21ae3-5592b-249e0-cc341
    - 143cc-0e942-b2955-3ea12-d006f
'''

try:
    from pyVmomi import vim
except ImportError:
    pass

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
from ansible.module_utils.vmware import PyVmomi, vmware_argument_spec, find_hostsystem_by_name

def diffcheck(first, second):
    return [item for item in first if item not in second]

def main():
    argument_spec = vmware_argument_spec()
    argument_spec.update(dict(
        remove_unmanaged_tasks=dict(type='bool', default=False),
        managed_tasks=dict(type='list', default=[]),
    ))

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    result = {
        "changed": False,
        "vCenterScheduledTasksRemoved": [],
        "diff": {
            "before": [],
            "after": []
        }
    }

    pyv = PyVmomi(module)
    if not pyv.is_vcenter():
        module.fail_json(msg="vcenter_scheduled_tasks  is meant for vCenter, hostname %s "
                             "is not vCenter server." % module.params.get('hostname'))

    existingScheduledTasks = pyv.content.scheduledTaskManager.RetrieveEntityScheduledTask()

    for existingScheduledTask in existingScheduledTasks:
        result['diff']['before'].append(existingScheduledTask.info.name)

    diffs = diffcheck(result['diff']['before'],module.params['managed_tasks'])

    if diffs:
        if module.params['remove_unmanaged_tasks']:
            for diff in diffs:
                existingScheduledTasks = pyv.content.scheduledTaskManager.RetrieveEntityScheduledTask()
                for existingScheduledTask in existingScheduledTasks:
                    if diff == existingScheduledTask.info.name:
                        existingScheduledTask.RemoveScheduledTask()
                        result['vCenterScheduledTasksRemoved'].append(diff)
                        result['changed'] = True
                    else:
                        module.debug('This task is managed by ansible config - not deleting "%s"' % diff)
        else:
            module.debug('argurment remove_unmanaged_tasks is false so skipping the removal of unmanaged tasks')
    else:
        module.debug('There is no difference between desired state and current state - no changes required')

    existingScheduledTasks = pyv.content.scheduledTaskManager.RetrieveEntityScheduledTask()
    for existingScheduledTask in existingScheduledTasks:
        result['diff']['after'].append(existingScheduledTask.info.name)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
