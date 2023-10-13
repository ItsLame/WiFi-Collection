# Working Environment
## Specs
- macOS Ventura 13.6
- MacBook Pro (14-inch, 2021)
- Apple M1 Pro, 32 GB
## Package Version
- python 3.12.0
- pandas 2.1.1
- pyobjc 10.0
- tabulate 0.9.0
## Troubleshooting
- Enable location services for python to retrieve bssid value from CoreWLAN
  - returns `null` if not enabled

# Files
## Main File
- `wifi_data.py`: to get data of surrounding networks
  - automated columns: (1) time, (2) OS, (3) network interface, (4) ssid, (5) bssid, (6) frequency, (7) network channel, (8) channel width, (9) rssi, (10) noise level, (11) public ip address, (12) network delay
  - to be filled separately: gps ((1) latitude, (2) longitude, (3) accuracy), (4) wi-fi standard
  - 16 columns in total

## Post-processing Files
- `clean_gps.py`: to clean up GPS data from 'GPS Tracks'
  - calculates gps accuracy using cep
  - drops redundant columns
- `clean_protocol.py`: to clean up protocol data from 'Wireless Diagnostic > Scan'
  - drops redundant columns
  - drop duplicate rows
- `clean_data.py`: to clean up wifi data (inserts protocol data, and (wip) gps data)
  - inserts cleaned up protocol list into column
  - inserts cleaned up gps data into column
  - drop duplicate rows

## Recommended Sequence
1. Collect wifi data using `wifi_data.py`, 'Wireless Diagnostic > Scan', and 'GPS Tracks' tracks.
>**Wireless Diagnostic**:
>1. Press 'Scan Now' in 'Wireless Diagnostic > Scan', select all, copy.
>2. Paste to protocol > list > day_time.txt
>3. Save and repeat

>**GPS Tracks**:
>1. Walk to destination
>2. Press the pin icon
>3. Repeat
2. In 'GPS Tracks', export GPS data as CSV and then place into gps folder
3. Clean up gps
4. Clean up protocol
5. Clean up wifi data