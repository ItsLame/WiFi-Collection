# OS: MACOS
import os, math, glob
import pandas as pd


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


# circular error probability calculation
def cep(horizontal_accuracy, vertical_accuracy):
    cep = math.sqrt(horizontal_accuracy**2 + vertical_accuracy**2)
    return cep


# to re-format name column's data
def name_format(date, name):
    n = name.split()
    day = n[0]
    month = n[1]
    year = n[2]

    d = date.split()
    day_name = pd.Timestamp(d[0])
    time = d[1][:-3]

    return f"{day_name.day_name()[:3]}_{day}{month}{year}_{time}"


# build class object
pc = print_color()

# gps folder path consisting of all the gps data
gps_folder = "gps"

# glob through file path
for index, csv_file in enumerate(glob.iglob(f"{gps_folder}/*.csv"), 1):
    # checker: if it's a file, if it exists, if it has a csv extension
    if not os.path.isfile(csv_file):
        pc.orange(f"Warning: {csv_file} not a file! Skipping...")
        continue
    elif not os.path.exists(csv_file):
        pc.orange(f"Warning: {csv_file} file does not exist! Skipping...")
        continue
    elif not csv_file.endswith(".csv"):
        pc.orange(f"Warning: {csv_file} not a CSV file! Skipping...")
        continue

    # read csv file
    df = pd.read_csv(csv_file)
    valid_columns = ["Date", "Name", "Latitude", "Longitude", "Altitude (m)", "Notes"]

    # check columns/format
    if not all(i in df.columns for i in valid_columns):
        pc.red(f"Error: {csv_file} has invalid columns/format! Please fix file.")
        continue

    # check "Notes" column and split into "Horizontal Accuracy (m)" and "Vertical Accuracy (m)"
    df["Horizontal Accuracy (m)"] = (
        df["Notes"].str.extract(r"Horizontal Accuracy: ± (\d+)").astype(float)
    )
    df["Vertical Accuracy (m)"] = (
        df["Notes"].str.extract(r"Vertical Accuracy: ± (\d+)").astype(float)
    )

    # calculate CEP
    df["GPS Accuracy (meters)"] = list(
        map(cep, df["Horizontal Accuracy (m)"], df["Vertical Accuracy (m)"])
    )

    # re-format name column's data
    df["Name"] = list(map(name_format, df["Date"], df["Name"]))

    # sort by date (ascending)
    df = df.sort_values(by=["Date"], ascending=True)

    # drop redundant columns
    df.drop(
        columns=[
            "Date",
            "Notes",
            "Altitude (m)",
            "Horizontal Accuracy (m)",
            "Vertical Accuracy (m)",
        ],
        inplace=True,
    )

    # rename
    df.rename(
        columns={
            "Name": "Time",
            "Latitude": "GPS Latitude",
            "Longitude": "GPS Longitude",
        },
        inplace=True,
    )

    # drop time column
    df.drop(columns=["Time"], inplace=True)

    # initialise variables
    path = "gps/cleaned"
    filename = os.path.basename(csv_file)
    output_file = f"{filename}"

    # make new directory
    if not os.path.exists(path):
        os.makedirs(path)

    # save to csv
    df.to_csv(os.path.join(path, output_file), index=False)
    pc.green(f"{index} >> Saved modified {csv_file} to {path}/{output_file}")
