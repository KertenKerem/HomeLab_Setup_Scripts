#!/usr/bin/env python3

import subprocess
import yaml
import os

def get_interface_info(interface):
    """
    Gets the current IP configuration of the specified network interface.
    """
    try:
        result = subprocess.run([
            'ip', 'addr', 'show', interface
        ], capture_output=True, text=True, check=True)

        output = result.stdout
        
        # Extract IP address
        ip_line = [line for line in output.splitlines() if 'inet ' in line]
        if not ip_line:
            raise ValueError("No IP address found on the interface")
        
        ip_info = ip_line[0].split()
        ip_address = ip_info[1].split('/')[0]
        
        # Extract subnet mask
        subnet_mask = ip_info[1].split('/')[1]

        # Extract gateway (assuming default route for the interface)
        result = subprocess.run([
            'ip', 'route', 'show', 'default', 'dev', interface
        ], capture_output=True, text=True, check=True)

        route_output = result.stdout.strip()
        gateway = None
        if route_output:
            gateway = route_output.split()[2]

        return {
            'ip_address': ip_address,
            'subnet_mask': subnet_mask,
            'gateway': gateway
        }

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Command failed: {e}")


def create_netplan_config(interface1, interface2, config1, config2):
    """
    Creates a Netplan YAML configuration file for the specified interfaces.
    """
    netplan_config = {
        'network': {
            'version': 2,
            'ethernets': {
                interface1: {
                    'addresses': [f"{config1['ip_address']}/{config1['subnet_mask']}"],
                    'routes': [
                        {
                            'to': '0.0.0.0/0',
                            'via': config1['gateway']
                        }
                    ],
                    'nameservers': {
                        'addresses': ['8.8.8.8', '8.8.4.4']  # Default DNS servers
                    }
                },
                interface2: {
                    'addresses': [f"{config2['ip_address']}/{config2['subnet_mask']}"],
                    'routes': [
                        {
                            'to': '192.168.56.0/24',
                            'via': '192.168.56.1'
                        }
                    ],
                    'nameservers': {
                        'addresses': ['1.1.1.1', '8.8.8.8']  # DNS servers for enp0s8
                    }
                }
            }
        }
    }

    netplan_file = '/etc/netplan/01-netcfg.yaml'
    
    with open(netplan_file, 'w') as file:
        yaml.dump(netplan_config, file, default_flow_style=False)

    # Ensure permissions are secure
    os.chmod(netplan_file, 0o600)

    print("Netplan configuration saved to /etc/netplan/01-netcfg.yaml")

    # Automatically remove 50-cloud-init.yaml if it exists
    cloud_init_file = '/etc/netplan/50-cloud-init.yaml'
    if os.path.exists(cloud_init_file):
        os.remove(cloud_init_file)
        print("Removed 50-cloud-init.yaml to avoid conflicts.")


def main():
    interface1 = 'enp0s3'
    interface2 = 'enp0s8'

    try:
        print(f"Fetching current configuration for {interface1}...")
        config1 = get_interface_info(interface1)

        print(f"Fetching current configuration for {interface2}...")
        config2 = get_interface_info(interface2)

        print("Current configurations:")
        print(f"{interface1}: {config1}")
        print(f"{interface2}: {config2}")

        print("Creating Netplan static IP configuration...")
        create_netplan_config(interface1, interface2, config1, config2)

        print("Configuration complete. Apply it using 'sudo netplan apply'.")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    main()
