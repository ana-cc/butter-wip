#!/usr/bin/env python3

import subprocess
import re

CONFIG_FILE = "/etc/hostapd/hostapd.conf"

def find_ap_interface():
    try:
        iw_dev_output = subprocess.check_output(["iw", "dev"], text=True)
    except Exception as e:
        print(f"Error running iw dev: {e}")
        return None

    interfaces = re.findall(r"Interface\s+(\w+)", iw_dev_output)

    for iface in interfaces:
        try:
            modes_output = subprocess.check_output(["iw", "dev", iface, "info"], text=True)
            # Check for AP mode support
            phy_output = subprocess.check_output(["iw", iface, "info"], text=True, stderr=subprocess.DEVNULL)
        except Exception:
            continue

        try:
            phy_name = re.search(r"wiphy (\d+)", modes_output)
            if not phy_name:
                continue
            phy_info = subprocess.check_output(["iw", "phy", f"phy{phy_name.group(1)}", "info"], text=True)
            if "AP" in phy_info:
                return iface
        except Exception:
            continue
    return None

def update_config(interface_name):
    try:
        with open(CONFIG_FILE, "r") as f:
            lines = f.readlines()

        with open(CONFIG_FILE, "w") as f:
            for line in lines:
                if line.strip().startswith("interface="):
                    f.write(f"interface={interface_name}\n")
                else:
                    f.write(line)
        print(f"Updated {CONFIG_FILE} to use interface: {interface_name}")
    except Exception as e:
        print(f"Error updating config: {e}")

if __name__ == "__main__":
    iface = find_ap_interface()
    if iface:
        update_config(iface)
    else:
        print("No AP-capable interface found.")
