#!/usr/bin/python3

import os
import sys
import argparse
import psycopg2
import psycopg2.extras

try:
    import json
except ImportError:
    import simplejson as json

class ExampleInventory(object):

    def __init__(self):
        self.inventory = {}
        self.read_cli_args()

        # Called with `--list`.
        if self.args.list:
            self.inventory = self.example_inventory()
        # Called with `--host [hostname]`.
        elif self.args.host:
            # Not implemented, since we return _meta info `--list`.
            self.inventory = self.empty_inventory()
        # If no groups or vars are present, return an empty inventory.
        else:
            self.inventory = self.empty_inventory()

        print(json.dumps(self.inventory))

    # Example inventory for testing.
    def example_inventory(self):

        username = os.environ["DB_USERNAME"]
        password = os.environ["DB_PASSWORD"]

        con = psycopg2.connect(database="test_inventory", 
                            user=username, 
                            password=password, 
                            host="192.168.49.2", port="30008")

        cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * from hosts")
        hosts = cur.fetchall()

        for host in hosts:
            groupName = host['groupname']
            hostName = host['hostname']
            ipAddress = host['ipaddress']

            if groupName not in self.inventory:
                self.inventory[groupName] = dict()
                self.inventory[groupName]['vars'] = {"ansible_connection": "local", "ansible_python_interpreter": "{{ ansible_playbook_python }}"}
                self.inventory[groupName]['hosts'] = list()

            self.inventory[groupName]['hosts'].append(ipAddress)

        con.close()

        self.inventory['_meta'] = {'hostvars': {}}

        return self.inventory

    # Empty inventory for testing.
    def empty_inventory(self):
        return {'_meta': {'hostvars': {}}}

    # Read the command line args passed to the script.
    def read_cli_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--list', action = 'store_true')
        parser.add_argument('--host', action = 'store')
        self.args = parser.parse_args()

# Get the inventory.
ExampleInventory()
