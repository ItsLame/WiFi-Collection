# OS: MACOS
import os, glob
import pandas as pd

# FOR DEBUGGING
# from tabulate import tabulate


# print in color
class print_color:
    def red(self, string, end="\n"):
        print(f"\033[91m{string}\033[0m", end=end)

    def green(self, string, end="\n"):
        print(f"\033[92m{string}\033[0m", end=end)

    def cyan(self, string, end="\n"):
        print(f"\033[96m{string}\033[0m", end=end)

    def orange(self, string, end="\n"):
        print(f"\033[93m{string}\033[0m", end=end)

    def purple(self, string, end="\n"):
        print(f"\033[95m{string}\033[0m", end=end)


# build class object
pc = print_color()

# data folder path consisting of all the gps data
data_folder = "data"

# protocol file path consisting of the master protocol csv list
protocol_file = "protocol/protocol.csv"
p_df = pd.read_csv(protocol_file)

# gps folder path consisting of the coordinates and accuracy
gps_file = "gps/cleaned"

# create master list
master_list = []

# glob through file path (gps)
for gps_csv_file in glob.iglob(f"{gps_file}/*.csv"):
    # checker: if it's a file, if it has a csv extension
    if not os.path.isfile(gps_csv_file):
        pc.orange(f"Warning: {gps_csv_file} not a file! Skipping...")
        continue
    elif not gps_csv_file.endswith(".csv"):
        pc.orange(f"Warning: {gps_csv_file} not a CSV file! Skipping...")
        continue

    # get day and time
    time_group = os.path.basename(gps_csv_file[:-4]).split("_")
    gps_day = time_group[0]
    gps_time = time_group[1]

    # read csv file
    g_df = pd.read_csv(gps_csv_file)

    # glob through file path (day)
    for day in glob.iglob(f"{data_folder}/*"):
        # checker: if it's a folder
        if not os.path.isdir(day):
            continue

        # skip if different day
        if gps_day != os.path.basename(day):
            continue

        # glob through file path (time)
        for time in glob.iglob(f"{day}/*"):
            # checker: if it's a folder
            if not os.path.isdir(day):
                continue

            # skip if different time
            if gps_time != os.path.basename(time):
                continue

            # print log
            print(f"Cleaning files in {time}:", end=" ")

            # glob through file path (csv files)
            for index, csv_file in enumerate(glob.iglob(f"{time}/*.csv"), 1):
                # checker: if it's a file,  if it has a csv extension
                if not os.path.isfile(csv_file):
                    pc.orange(f"Warning: {csv_file} not a file! Skipping...")
                    continue
                elif not csv_file.endswith(".csv"):
                    pc.orange(f"Warning: {csv_file} not a CSV file! Skipping...")
                    continue

                # read csv file
                df = pd.read_csv(csv_file)
                valid_columns = [
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

                # check columns/format
                if not all(i in df.columns for i in valid_columns):
                    pc.red(
                        f"Error: {csv_file} has invalid columns/format! Please fix file."
                    )
                    continue

                # merge by BSSID
                df = df.merge(p_df, on=["BSSID"])

                # fillna from gps data
                df = df.fillna(g_df.iloc[index - 1])

                # drop redundant columns
                df = df.drop("Wi-Fi Standard", axis=1)

                # move and rename column
                wifi_standard = df.pop("Protocol")
                df.insert(8, "Wi-Fi Standard", wifi_standard)

                # initialize variables
                output_path = f"{os.path.dirname(csv_file)}/cleaned"
                output_file = f"{output_path}/{os.path.basename(csv_file)}"

                # make new directory
                if not os.path.exists(output_path):
                    os.makedirs(output_path)

                # save to csv
                df.to_csv(output_file, index=False)

                # append to master list
                master_list.append(df)

            # print confirmation log
            pc.cyan(f"merged with {protocol_file} & {gps_csv_file} ➔", end=" ")
            pc.green(f"{index} >> Saved to {output_path}")

# save sorted master dataframe to csv
master_output_file = "data/master.csv"
master_df = pd.concat(master_list, ignore_index=True)
master_df = master_df.sort_values(by=["Time"], ascending=True)
master_df = master_df.drop_duplicates()
rows = master_df.index.size
master_df.to_csv(master_output_file, index=False)
pc.purple(f"➥ Saved master list to {master_output_file} ({rows} rows)")

# FOR DEBUGGING
# print(tabulate(df.head(1), headers="keys", tablefmt="psql"))
# print("SIZE:", df.index.size)
# print(df.head(1))
