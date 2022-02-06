#!/bin/bash

# deploy source code only

TARGET="$1"

if [ $# -lt 1 ]; then
	echo "Expected host name from Ansible inventory"
	exit 1
fi

ansible-playbook -i inventory.yml --limit "${TARGET}" --tags roon_remote_src site.yml

