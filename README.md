# Ansible Dynamic Inventory Based On Hosts In Subnet

This Python script dynamically generates an inventory for Ansible based on reachable hosts in a given subnet. Hosts are automatically grouped into predefined categories such as `test`/`prod` or `user-defined groups` based on hostname patterns.

## Features

- **Subnet Scanning:** Detects all reachable hosts in a specified subnet using port 22 (SSH).
- **Dynamic Grouping:**
  - Hosts are grouped into `test` and `prod` based on substrings in their hostnames.
  - Additional custom groups can be created using hostname substring rules.
- **Host Variables:** Each host's FQDN and IP are included in the inventory for detailed configuration.

## How It Works

1. The script scans a given subnet (`192.168.1.0/24` by default) for active hosts.
2. It checks if a host is reachable on port 22.
3. For reachable hosts:
   - It retrieves their FQDN and hostname.
   - Groups them based on predefined rules.
4. Outputs the inventory in JSON format.

## Inventory Structure

The output JSON includes:
- A list of all reachable hosts under the `all` group.
- `test` and `prod` groups based on hostname substrings.
- Additional custom groups based on user-defined rules.
- `_meta` section with host variables (`fqdn`, `ip`).

Example:
```json
{
    "all": {
        "hosts": ["host1", "host2"]
    },
    "_meta": {
        "hostvars": {
            "host1": {"fqdn": "host1.local", "ip": "192.168.1.1"},
            "host2": {"fqdn": "host2.local", "ip": "192.168.1.2"}
        }
    },
    "test": {
        "hosts": ["host1"]
    },
    "prod": {
        "hosts": ["host2"]
    },
    "group1": {
        "hosts": ["host1"]
    },
    "group2": {
        "hosts": []
    }
}
```

## Configuration

You can customize the script by modifying these variables:
- **`HOST_SUBNET`:** Subnet to scan (default is `192.168.1`).
- **`TEST_HOSTS`:** List of substrings for hosts to be placed in the `test` group.
- **`ADDITIONAL_GROUP_RULES`:** Dictionary defining custom groups and their matching substrings.

## Usage

Run the script as an Ansible dynamic inventory source:

```bash
ansible-inventory -i dynamic_inventory.py --list
```
## Using with AWX

This dynamic inventory script also works seamlessly with AWX. To integrate the script with AWX, follow these steps:

1. **Add the project in AWX:**
   - Go to the **Projects** section in AWX and add a new project.
   - Set the project type to **Git** and provide the repository URL where the script is hosted.
   - Make sure the project syncs successfully.

2. **Create an Inventory:**
   - Go to the **Inventories** section and create a new inventory.
   
3. **Configure the Inventory Source:**
   - In the **Sources** tab of the inventory, click to add a new source.
   - Choose **Project** as the source type and select the project you created earlier.
   - Set the **Inventory File** to `dynamic_inventory.py` (the script you added in your project).

4. **AWX will now interpret `dynamic_inventory.py` as an inventory source:**
   - When AWX runs a job using this inventory, it will execute the script and generate a dynamic inventory based on the hosts in the specified subnet.
   - The hosts will be grouped as defined in the script, and you can use this dynamic inventory in your playbooks as usual.

Now your AWX environment is ready to use dynamic inventory based on hosts in the subnet!

## Requirements

- Python 3.x
- Socket library (included in Python standard library)

## Notes

- Ensure you have network access to the target subnet.
- The script uses port 22 (SSH) for reachability checks.
- Modify the subnet or grouping rules as needed to suit your environment.

