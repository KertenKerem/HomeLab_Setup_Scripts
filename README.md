# HomeLab_Setup_Scripts
Here I collect the scripts that automate the routine and boring tasks I do in every virtual server installation.
## dhcpTOstaticIP.py
It converts your DHCP-assigned IP addresses into static IP addresses and saves them as /etc/netplan/01-netcfg.yaml. It also deletes the 50-cloud-init.yaml file if present.
