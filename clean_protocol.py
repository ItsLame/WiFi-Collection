# OS: MACOS
import os, glob, re
import pandas as pd

# FOR DEBUGGING
from tabulate import tabulate


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


# build class object
pc = print_color()

# protocol folder path consisting of all the protocols
protocol_folder = "protocol/list"

# create dataframe
df = pd.DataFrame(
    columns=[
        "SSID",
        "BSSID",
        "Protocol",
    ]
)

# glob through file path
for index, txt_file in enumerate(glob.iglob(f"{protocol_folder}/*.txt"), 1):
    # checker: if it's a file, if it exists, if it has a txt extension
    if not os.path.isfile(txt_file):
        pc.orange(f"Warning: {txt_file} not a file! Skipping...")
        continue
    elif not os.path.exists(txt_file):
        pc.orange(f"Warning: {txt_file} file does not exist! Skipping...")
        continue
    elif not txt_file.endswith(".txt"):
        pc.orange(f"Warning: {txt_file} not a txt file! Skipping...")
        continue

    with open(txt_file, "r") as f:
        for line in f:
            l = line.strip().split(",")
            if len(l) > 1:
                ssid = re.search(r"'(.*)'|.*", l[0]).group(0)

                if "HIDDEN" in ssid:
                    offset = 1
                else:
                    offset = 0

                bssid = l[2 - offset].split("=")[1]
                protocol = l[6 - offset].split("=")[1]

                df.loc[len(df) + 1] = [
                    ssid,
                    bssid,
                    f"802.{protocol}",
                ]

# drop duplicates
df = df.drop_duplicates()
length = df.index.size

# export to csv
# output_file = "protocol/protocol_all.csv"
# df.to_csv(output_file, index=False)
# print(
#     f"\033[1m\033[92m>> Saved protocol master list w/ hidden SSIDs ({length} unique BSSIDs) to {output_file}\033[0m"
# )

# FOR DEBUGGING
# print("\n5 head of dataframe:")
# print(tabulate(df.head(5), headers="keys", tablefmt="psql"))

# drop hidden SSIDs
df = df[~df["SSID"].str.contains("HIDDEN")]
length = df.index.size

# drop SSID column
df = df.drop(columns=["SSID"])

# export to csv
output_file = "protocol/protocol.csv"
df.to_csv(output_file, index=False)
print(
    f"\033[1m\033[92m>> Saved protocol master list ({length} unique BSSIDs) to {output_file}\033[0m"
)

# FOR DEBUGGING
print("\n5 head of dataframe:")
print(tabulate(df.head(5), headers="keys", tablefmt="psql"))
