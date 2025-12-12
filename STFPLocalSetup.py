import os
import time
from functools import partial
import requests
import os, sys
import winshell
from pathlib import Path


currentUser = os.environ.get('USERNAME')
print(f"Creating SFTP client for {currentUser}")

root_directory = f'C:/Users/{currentUser}/AppData/Roaming/SFTPLocal'
print(f"Install Location: {root_directory}")
list = ('Configs', 'Downloads', 'Logs', 'Temp', 'Uploads')
print(f"Creating Subfolders...")
concat_root_path = partial(os.path.join, root_directory)
make_directory = partial(os.makedirs, exist_ok=True)

for path_items in map(concat_root_path, list):
    try:
        make_directory(path_items)
        print(f"\033[32m{path_items} created!\033[0m")
    except Exception as e:
        print(f"\033[33m{e}\033[0m")

bridgeLink = 'https://raw.githubusercontent.com/SpicyCuban/KRTNA/refs/heads/main/SFTP_Bridge.py'
print(f"Installing SFTP_Bridge.py from: {bridgeLink}... ")
response = requests.get(bridgeLink)
file_Path = f'{root_directory}/SFTP_Bridge.py'

if response.status_code == 200:
    with open(file_Path, 'wb') as file:
        file.write(response.content)
    print('\033[42mGithub pull request successful!\033[0m')
else:
    print('\033[33mERROR: Could not download SFTP_Bridge.py, status code:\033[0m', response.status_code)

print('Creating Shortcut to Desktop...')
link_filepath = os.path.join(winshell.desktop(), "SFTPServer.lnk")
with winshell.shortcut(link_filepath) as link:
  link.path = f'{root_directory}/SFTP_Bridge.py'
  link.description = "SFTP Bridge"
a = Path(f"{link_filepath}")
if a.exists():
    print("\033[42mSuccessfully created Shortcut to Desktop.\033[0m")
else:
    print("\033[33mCould not create Shortcut to Desktop.\033[0m")
    time.sleep(3)
print("\033[42mSuccesfully setup SFTPLocal Side!\033[0m")
time.sleep(5)
