#!/usr/bin/env python3

import json
import socket

# Default subnet for host discovery
HOST_SUBNET = "192.168.1"

# List of host substrings for the "test" group
TEST_HOSTS = ["test", "dev"]

# Additional grouping rules based on substrings in hostnames
ADDITIONAL_GROUP_RULES = {
    "group1": ["dev", "app"],
    "group2": ["db", "srv"]
}

def is_host_reachable(ip, port=22, timeout=1):
    """
    Checks if a host is reachable by attempting to open a socket on a given port.
    Defaults to port 22 (SSH) and a 1-second timeout.
    """
    try:
        with socket.create_connection((ip, port), timeout):
            return True
    except (socket.timeout, socket.error):
        return False

def get_reachable_hosts(subnet):
    """
    Returns a list of reachable hosts within the given subnet.
    Each host is represented as a dictionary containing its FQDN, hostname, and IP address.
    """
    reachable_hosts = []
    for i in range(1, 255):  # IP range (1-254)
        ip = f"{subnet}.{i}"
        try:
            fqdn = socket.gethostbyaddr(ip)[0]  # Retrieve the fully qualified domain name (FQDN)
            hostname = fqdn.split('.')[0]  # Extract the short hostname
            if is_host_reachable(ip):
                reachable_hosts.append({"fqdn": fqdn, "hostname": hostname, "ip": ip})
        except socket.herror:
            # Skip hosts with no DNS entry
            pass
    return reachable_hosts

def group_hosts_by_test_and_prod(hosts, test_hosts):
    """
    Splits hosts into 'test' and 'prod' groups based on substrings in hostnames.
    Hosts containing substrings from the test_hosts list are placed in the 'test' group.
    All other hosts go to the 'prod' group.
    """
    test_group = []
    prod_group = []

    for host in hosts:
        if any(substring in host["hostname"] for substring in test_hosts):
            test_group.append(host["hostname"])
        else:
            prod_group.append(host["hostname"])

    return {"test": test_group, "prod": prod_group}

def group_hosts_by_inclusion(hosts, group_rules):
    """
    Creates additional host groups based on substrings in hostnames.
    Each group contains hosts whose hostname includes any of the specified substrings.
    """
    groups = {group: [] for group in group_rules}  # Initialize groups

    for host in hosts:
        hostname = host["hostname"]
        for group, substrings in group_rules.items():
            if any(substring in hostname for substring in substrings):
                groups[group].append(hostname)

    return groups

def generate_inventory(subnet):
    """
    Generates a dynamic inventory in JSON format.
    Groups are created based on 'test'/'prod' rules and additional substring matching.
    """
    reachable_hosts = get_reachable_hosts(subnet)

    # Create 'test' and 'prod' groups
    base_groups = group_hosts_by_test_and_prod(reachable_hosts, TEST_HOSTS)

    # Create additional groups based on inclusion rules
    additional_groups = group_hosts_by_inclusion(reachable_hosts, ADDITIONAL_GROUP_RULES)

    # Build the inventory structure
    inventory = {
        "all": {
            "hosts": [host["hostname"] for host in reachable_hosts],
        },
        "_meta": {
            "hostvars": {
                host["hostname"]: {
                    "fqdn": host["fqdn"],
                    "ip": host["ip"]
                }
                for host in reachable_hosts
            }
        }
    }

    # Add groups to the inventory
    for group, hosts in {**base_groups, **additional_groups}.items():
        inventory[group] = {"hosts": hosts}

    return inventory

def main():
    """
    Entry point for the script.
    Prints inventory in JSON format when called with the --list flag.
    """
    print(json.dumps(generate_inventory(HOST_SUBNET), indent=4))

if __name__ == "__main__":
    main()
