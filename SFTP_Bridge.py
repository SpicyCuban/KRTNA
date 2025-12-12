import paramiko
import os
import shutil
import sys
import time
import logging
from logging.handlers import RotatingFileHandler

currentUser = os.environ.get('USERNAME')
root_directory = f'C:/Users/{currentUser}/AppData/Roaming/SFTPLocal'

class SFTPClient:
    def __init__(self, host, port, username, password,reconnect_attempts=5, reconnect_delay=3):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.reconnect_attempts = reconnect_attempts
        self.reconnect_delay = reconnect_delay

        self.transport = None
        self.sftp = None

        self.logger = self._setup_logger()

    # -------------------------------------------------------
    # LOGGING SETUP
    # -------------------------------------------------------

    def _setup_logger(self):
        logger = logging.getLogger("SFTPClient")
        logger.setLevel(logging.INFO)

        # Console output
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Log file with rotation
        file_handler = RotatingFileHandler(
            "sftp_client.log",
            maxBytes=1_000_000,  # 1 MB
            backupCount=3
        )
        file_handler.setLevel(logging.INFO)

        # Log formatting
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            "%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        return logger

    # -------------------------------------------------------
    # CONNECTION HANDLING
    # -------------------------------------------------------

    def connect(self):
        for attempt in range(1, self.reconnect_attempts + 1):
            try:
                print(f"Connecting to {self.host}:{self.port} ...")
                self.transport = paramiko.Transport((self.host, self.port))
                self.transport.connect(username=self.username, password=self.password)
                self.sftp = paramiko.SFTPClient.from_transport(self.transport)

                print("\033[42mConnected successfully to Server!\033[0m")
                self.logger.info("Connected to SFTP Server")

                return True  # <-- FIXED HERE

            except Exception as e:
                print(f"\033[33mConnection failed: {e}\033[0m")
                self.logger.error(f"Connection failed: {e}")

                if attempt == self.reconnect_attempts:
                    self.logger.critical("All reconnect attempts failed.")
                    raise

                self.logger.info(f"Retrying in {self.reconnect_delay} seconds...")
                time.sleep(self.reconnect_delay)

        return False

    def reconnect(self):
        """Reconnect after a lost connection."""
        self.close()
        return self.connect()

    # -------------------------------------------------------
    # FILE OPERATIONS
    # -------------------------------------------------------

    def safe_operation(self, operation, *args):
        """Wrap SFTP operations with reconnect logic."""
        try:
            return operation(*args)
        except Exception as e:
            self.logger.warning(f"Operation failed: {e}. Trying reconnect...")
            self.reconnect()
            return operation(*args)

    def list_files(self, remote_path="."):
        try:
            self.logger.info(f"Listing files in: {remote_path}")
            result = self.safe_operation(self.sftp.listdir, remote_path)
            self.logger.info(f"Files: {result}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to list directory: {e}")
            return []

    def upload(self, local_path, remote_path):
        self.logger.info(f"Uploading {local_path} → {remote_path}")
        try:
            self.safe_operation(self.sftp.put, local_path, remote_path)
            self.logger.info("Upload complete.")
        except Exception as e:
            self.logger.error(f"Upload failed: {e}")


    def download(self, remote_path, local_path):
        self.logger.info(f"Downloading {remote_path} → {local_path}")
        try:
            self.safe_operation(self.sftp.get, remote_path, local_path)
            self.logger.info("Download complete.")
            script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
            source = f'{script_directory}/{local_path}'
            destination = f'{root_directory}/Downloads'
            dest = shutil.move(source, destination)
        except Exception as e:
            self.logger.error(f"Download failed: {e}")

        # -------------------------------------------------------
        # SHUTDOWN
        # -------------------------------------------------------
    def close(self):
        if self.sftp:
            self.sftp.close()
        if self.transport:
            self.transport.close()
        self.logger.info("Connection closed.")

    def make_dir(self, remote_path):
        try:
            self.sftp.mkdir(f"/{remote_path}/")
            print("Directory Created!")
        except Exception as e:
            print(f"Directory could not be created: {e}")

    def upload_setup(client):
        client.logger.info("User selected: Upload")
        upload_place = input("Do you want to upload in (C)urrent shared or (U)ser folder?[C/U]")
        if upload_place == "C":
            installFolder = 'uploads'
        elif upload_place == "U":
            username = input("Username: ")
            password = input("Password: ")
        local_path = input("Enter the path of the file to upload: ").strip()
        if not os.path.isfile(local_path):
            print("❌ File does not exist.")
            client.logger.error(f"Upload failed: local file missing → {local_path}")
            return

        remote_path = f"/{installFolder}/" + os.path.basename(local_path)
        client.upload(local_path, remote_path)

    def console(client):
        client.logger.info("User entered console mode")

        print("\n📌 SFTP Console Mode")
        print("Type 'help' for a list of commands, or 'back' to return to menu.\n")

        while True:
            cmd = input("console> ").strip().lower()

            if cmd == "back":
                client.logger.info("Exited console mode")
                return

            elif cmd == "help":
                print("\nAvailable commands:")
                print("  help        - Show this menu")
                print("  mkdir       - Create directory on server")
                print("  back        - Return to main menu\n")

            elif cmd == "mkdir":
                dirname = input("Enter name of new remote directory: ").strip()
                client.make_dir(f"/{dirname}/")

            else:
                print("Unknown command. Type 'help'.")

    def download_setup(client):
        client.logger.info("User selected: Download")
        print("\nFiles on server (/uploads/):")
        server_files = client.list_files("/uploads/")
        print(server_files)

        filename = input("Enter the name of the file to download: ").strip()
        remote_path = "/uploads/" + filename
        local_path = filename

        client.download(remote_path, local_path)

def menu(client):
    client.logger.info("Menu started")

    while True:
        print("\n=== SFTP SERVER MENU ===")
        print("[1] Upload file to server")
        print("[2] Download file from server")
        print("[3] Console")
        print("[4] Bridge Updater")
        print("[q] Quit")
        print("========================")

        choice = input("Select an option: ").strip().lower()

        if choice == "1":
            upload_setup(client)
        elif choice == "2":
            download_setup(client)
        elif choice == "3":
            console(client)
        #elif choice == "4":

        elif choice == "q":
            client.logger.info("User quit program")
            client.close()
            print("Goodbye!")
            sys.exit(0)
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    HOST = "34.90.147.78"
    PORT = 22
    USER = "sftpuser"
    PASSWORD = "root"

    client = SFTPClient(HOST, PORT, USER, PASSWORD)

    client.connect()
    menu(client)

    # Example upload
    #client.upload("test_upload.txt", "/uploads/test_upload.txt")

    # Example download
    #client.download("/uploads/test_upload.txt", "downloaded_test.txt")

    #client.close()
