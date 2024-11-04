#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import requests
import os

DOCUMENTATION = '''
---
module: sap_install
author: Peter Varkoly <varkoly@suse.com>
version_added: "1.4"
short_description: Install a SAP HANA database and an additional SAP product if source is given
requirements: [ lvm2 ]
description:
    - Install the SAP HANA database with the given parameter. 
    - Install am additional SAP product if the variable product source is given. 
    - Currently implemented on SUSE Linux Enterprise Server for SAP Applications
    - Any distribution that uses systemd as their init system
options:
    admin_pw:
        required: true
        description:
            - The password of the SAP main administrator.
    sid:
        required: true
        description:
            - The SID of the HANA database to install.
    inst_number:
        required: true
        description:
            - The instance number of the HANA database to install.
    xs_routing_mode:
        required: false
        description:
            - The XS routing mode. This can be 'ports' or 'hostname'. Default is 'ports'.
    xs_domain_name:
        required: false
        description:
            - The XS domain name. Required only if xs_routing_mode == 'hostname'.
'''

EXAMPLES = '''
---
- name: Install SAP products
  hosts: all
  become: yes
  tasks:
    - name: Install needed packages
      zypper:
        name:
          - lvm2
        state: present

    - name: Create physical partition on the selected disk
      command: "parted {{ disk }} mklabel gpt"
      ignore_errors: yes

    - name: Create partition for LVM
      parted:
        device: "{{ disk }}"
        number: 1
        state: present
        part_type: primary
        fs_type: linux-lvm
        size: 160GiB

    - name: Create physical volume (PV)
      lvg:
        vg: sap
        pvs:
          - "{{ disk }}"1

    - name: Create logical volume for hanadata
      lvol:
        vg: sap
        lv: hanadata
        size: "{{ hanadata_size }}"

    - name: Create logical volume for hanalog
      lvol:
        vg: sap
        lv: hanalog
        size: "{{ hanalog_size }}"

    - name: Create logical volume for hanashared
      lvol:
        vg: sap
        lv: hanashared
        size: "{{ hanashared_size }}"

    - name: Create logical volume for usrsap
      lvol:
        vg: sap
        lv: usrsap
        size: "{{ usrsap_size }}"

    - name: Format LV hanadata with xfs
      filesystem:
        fstype: xfs
        dev: /dev/sap/hanadata

    - name: Format LV hanalog with xfs
      filesystem:
        fstype: xfs
        dev: /dev/sap/hanalog

    - name: Format LV hanashared with xfs
      filesystem:
        fstype: xfs
        dev: /dev/sap/hanashared

    - name: Format LV usrsap with xfs
      filesystem:
        fstype: xfs
        dev: /dev/sap/usrsap

    - name: Create mount points for the LVs
      file:
        path: "{{ item }}"
        state: directory
      loop:
        - /hana/data
        - /hana/log
        - /hana/shared
        - /usr/sap 

    - name: Mount hanalog on /hana/log 
      mount:
        path: /hana/log 
        src: /dev/sap/hanalog 
        fstype: xfs 
        state: mounted 

    - name: Mount hanashared on /hana/shared 
      mount:
        path: /hana/shared 
        src: /dev/sap/hanashared 
        fstype: xfs 
        state: mounted 

    - name: Mount usrsap auf /usr/sap 
      mount:
        path: /usr/sap 
        src:/dev/sap/usrsap
        fstype=xfs 
         state=mounted 

    - name: Run the sap installation
      sap_install:
        admin_pw: "{{ admin_pw }}"
        sid: "{{ sid }}"
        inst_number: "{{ inst_number }}"
        hana_source: "{{ hana_source }}"
        xs_routing_mode: "{{ xs_routing_mode }}"
        xs_domain_name: "{{ xs_domain_name }}"
        product_source: "{{ product_source }}"

'''

def run_module():
    # Define the arguments/parameters that the module will take
    module_args = dict(
        admin_pw=dict(type='str', required=True, no_log=True),
        sid=dict(type='str', required=True),
        inst_number=dict(type='str', required=True),
        hana_source=dict(type='str', required=True)
        xs_routing_mode=dict(type='str', required=False)
        xs_domain_name=dict(type='str', required=False)
        product_source=dict(type='str', required=False)
    )

    # Seed the result dict in the object
    result = dict(
        changed=False,
        message=''
    )

    # The AnsibleModule object will be our abstraction working with Ansible
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    admin_pw = module.params['admin_pw']
    sid = module.params['sid']
    inst_number = module.params['inst_number']
    hana_source = module.params['hana_source']
    xs_routing_mode = module.params.get('xs_routing_mode','ports')
    xs_domain_name = module.params.get('xs_domain_name','')
    product_source = module.params.get('product_source','')

    # Logic for the module
    try:
        # Example: Download the source file
        response = requests.get(source_url)
        if response.status_code == 200:
            with open(f"{sid}_{inst_number}.bin", "wb") as file:
                file.write(response.content)
            result['changed'] = True
            result['message'] = 'File downloaded and saved successfully.'
        else:
            module.fail_json(msg=f"Failed to download file from {source_url}, status code: {response.status_code}")

    except Exception as e:
        module.fail_json(msg=f"An error occurred: {str(e)}")

    # Return success message
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
