import paramiko
import os


class SFTPClient:
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.transport = None
        self.sftp = None

    def connect(self):
        try:
            print(f"Connecting to {self.host}:{self.port} ...")
            self.transport = paramiko.Transport((self.host, self.port))
            self.transport.connect(username=self.username, password=self.password)
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
            print("Connected successfully!")
        except Exception as e:
            print(f"Connection failed: {e}")
            raise

    def list_files(self, remote_path="."):
        try:
            return self.sftp.listdir(remote_path)
        except Exception as e:
            print(f"Failed to list directory: {e}")
            return []

    def upload(self, local_path, remote_path):
        try:
            print(f"Uploading {local_path} → {remote_path}")
            self.sftp.put(local_path, remote_path)
            print("Upload complete!")
        except Exception as e:
            print(f"Upload failed: {e}")

    def download(self, remote_path, local_path):
        try:
            print(f"Downloading {remote_path} → {local_path}")
            self.sftp.get(remote_path, local_path)
            print("Download complete!")
        except Exception as e:
            print(f"Download failed: {e}")

    def close(self):
        if self.sftp:
            self.sftp.close()
        if self.transport:
            self.transport.close()
        print("Connection closed.")

def upload_Setup(client):
    local_path = input("Select file to upload: ")
    remote_path = "/uploads/" + os.path.basename(local_path)
    client.upload(local_path, remote_path)

def menu():
    print("[1] Upload files to server")
    print("[2] Download files from server")
    print("[3] Console\n\n [q] to quit and terminate connection")

    choice = input("Please choose between the different options: ")
    if choice == "1":
        upload_Setup(client)

if __name__ == "__main__":
    HOST = "34.141.175.188"
    PORT = 22
    USER = "sftpuser"
    PASSWORD = "root"

    client = SFTPClient(HOST, PORT, USER, PASSWORD)

    client.connect()
    menu()



    print("\nFiles on server (/uploads):")
    print(client.list_files("/uploads"))

    # Example upload
    #client.upload("test_upload.txt", "/uploads/test_upload.txt")

    # Example download
    #client.download("/uploads/test_upload.txt", "downloaded_test.txt")

    #client.close()
