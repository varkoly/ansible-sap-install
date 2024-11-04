# ansible-sap-install
Ansible module to install sap products on SLES

Example playbook:


```
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
        start: 0%
        end: 100%

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
      file:```
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
```

