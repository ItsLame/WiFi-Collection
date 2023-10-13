# OS: MACOS
import subprocess, re, objc, os
import pandas as pd
from datetime import datetime

# doc: https://developer.apple.com/documentation/corewlan/
# ref: https://clburlison.com/macos-wifi-scanning/
from CoreWLAN import CWInterface

# print in color
class print_color:
    def red(self, string):
        print(f"\033[91m{string}\033[0m")

    def green(self, string):
        print(f"\033[92m{string}\033[0m")

    def cyan(self, string):
        print(f"\033[96m{string}\033[0m")

    def orange(self, string):
        print(f"\033[93m{string}\033[0m")

pc = print_color()

# ping to an address
def ping():
    address = "cse.unsw.edu.au"
    print(f"Pinging \033[95m\033[1m{address}\033[0m...", end="")

    p = subprocess.run(
        f"ping -c 1 {address}", shell=True, capture_output=True
    ).stdout.decode()

    filt = re.findall(r"time=(\S+)", p)
    
    try:
        ip = subprocess.run("curl ifconfig.me", shell=True, capture_output=True).stdout.decode().strip()
        delay = "timeout" if len(filt) < 1 else filt[0]
    except:
        pc.red("failed!")
        exit()

    # print ping result
    print(f"{" success!" if delay != 'timeout' else delay}")

    return ip, delay


# scan surrounding wifi using CoreWLAN
# ref: https://github.com/pkruk/osx-wifi-scanner/blob/master/wifi-scan.py
def scan():
    bundle_path = "/System/Library/Frameworks/CoreWLAN.framework"
    objc.loadBundle("CoreWLAN", bundle_path=bundle_path, module_globals=globals())

    # get interface to get access to various WLAN interface parameters
    iface = CWInterface.interface()
    networks = iface.scanForNetworksWithName_includeHidden_error_(None, True, None)

    # ssid and bssid of connected wifi
    connected_ssid = iface.ssid()
    connected_bssid = iface.bssid()
    print(f"Connected to \033[95m\033[1m{connected_ssid}\033[0m")
    
    # check if interface and corresponding network service is enabled
    if not iface.serviceActive():
        pc.red("Error: connection has no service!")
        exit(1)

    # create dataframe
    df = pd.DataFrame(
        columns=[
            "Time",
            "OS",
            "Network Interface",
            "GPS Latitude",
            "GPS Longitude",
            "GPS Accuracy (meters)",
            "SSID",
            "BSSID",
            "Wi-Fi Standard",
            "Frequency",
            "Network Channel",
            "Channel Width (in MHz)",
            "RSSI (in dBm)",
            "Noise Level (in dBm)",
            "Public IP Address",
            "Network Delay (in ms)",
        ]
    )

    # ref: https://developer.apple.com/documentation/corewlan/cwnetwork?changes=l_2&language=objc
    for i in networks[0].allObjects():
        # if i.ssid() is not None:
            # retrieve hardware data (hardcoded because value always the same; improves performance)
            osys = "MACOS"
            network_interface = "Airport"

            # for timestamp
            dt = datetime.now()

            # retrieve network data
            ssid = i.ssid()
            channel = i.wlanChannel().channelNumber()
            bssid = i.bssid()
            frequency = "2.4" if i.wlanChannel().channelBand() == 2 else "5"
            width = re.search(r"(\d+)MHz", str(i.wlanChannel())).group(1)

            # retrieve ip and delay only for connected wifi
            if connected_ssid == ssid and connected_bssid == bssid:
                ip, delay = ping()
            else:
                ip, delay = None, None

            # add data to table
            df.loc[len(df) + 1] = [
                f"{dt.timestamp():.0f}",
                osys,
                network_interface,
                "",  # fill in manually (GPS Latitude)
                "",  # fill in manually (GPS Longitude)
                "",  # fill in manually (GPS Accuracy)
                ssid,
                bssid,
                "",  # fill in manually (Wi-Fi Standard)
                f"{frequency}GHz",
                channel,
                i.rssiValue(),
                f"{width}",
                i.noiseMeasurement(),
                ip,
                delay,
            ]

    return dt, df


# scan surrounding wifi using CoreWLAN, get dataframe, and drop duplicates
dt, df = scan()
df = df.drop_duplicates()

# initialise variables
aps = df.index.size
if aps == 0:
    print(f"\033[1m\033[91mZERO APs\033[0m\033[91m found, quiting...")
    exit()
path = "data"
output_file = f"{dt.strftime('%a_%d%b%Y_%H:%M:%S')}.csv"

# print current time
print(f"Current time: {dt.strftime('%A, %d %B %Y %H:%M:%S')}")

# make new directory
if not os.path.exists(path):
    os.makedirs(path)

# save to csv
df.to_csv(os.path.join(path, output_file), index=False)
print(f"\033[1m\033[92m>> Saved {aps} APs to {path}/{output_file}\033[0m")
