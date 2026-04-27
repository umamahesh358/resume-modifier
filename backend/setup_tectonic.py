import os
import platform
import urllib.request
import tarfile
import zipfile
import stat
import sys

def get_tectonic_url():
    """Returns the correct download URL for the tectonic binary based on the OS."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    base_url = "https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%400.15.0/"

    if system == "linux":
        if "aarch64" in machine or "arm64" in machine:
            return base_url + "tectonic-0.15.0-aarch64-unknown-linux-musl.tar.gz"
        return base_url + "tectonic-0.15.0-x86_64-unknown-linux-musl.tar.gz"
    elif system == "darwin": # macOS
        if "arm64" in machine:
            return base_url + "tectonic-0.15.0-aarch64-apple-darwin.tar.gz"
        return base_url + "tectonic-0.15.0-x86_64-apple-darwin.tar.gz"
    elif system == "windows":
        return base_url + "tectonic-0.15.0-x86_64-pc-windows-msvc.zip"
    else:
        raise Exception(f"Unsupported operating system: {system}")

def download_and_extract():
    url = get_tectonic_url()
    filename = url.split("/")[-1]
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    download_path = os.path.join(backend_dir, filename)

    print(f"Downloading Tectonic from {url}...")
    urllib.request.urlretrieve(url, download_path)
    print("Download complete. Extracting...")

    # Extract
    if filename.endswith(".tar.gz"):
        with tarfile.open(download_path, "r:gz") as tar:
            tar.extractall(path=backend_dir)
    elif filename.endswith(".zip"):
        with zipfile.ZipFile(download_path, 'r') as zip_ref:
            zip_ref.extractall(backend_dir)

    # Clean up archive
    os.remove(download_path)

    # Make executable on Unix
    if platform.system().lower() != "windows":
        tectonic_path = os.path.join(backend_dir, "tectonic")
        if os.path.exists(tectonic_path):
            st = os.stat(tectonic_path)
            os.chmod(tectonic_path, st.st_mode | stat.S_IEXEC)
            print("Successfully installed and made executable.")
        else:
            print("Error: Extracted binary not found.")
            sys.exit(1)
    else:
        print("Successfully installed Tectonic (Windows).")

if __name__ == "__main__":
    download_and_extract()
