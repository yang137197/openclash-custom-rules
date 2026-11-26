"""Fetch pinned public validation tools into an explicitly supplied temp directory."""
import argparse
import gzip
import hashlib
import platform
import urllib.request
from pathlib import Path

CORE_URL = "https://github.com/MetaCubeX/mihomo/releases/download/v1.19.34/mihomo-linux-amd64-compatible-v1.19.34.gz"
CORE_SHA = "2763f5b414527f7baf6dc57e3f82f3ab561eedf34bfd7c2f2cde1f7e592efe06"
YAML_URL = "https://raw.githubusercontent.com/vernesong/OpenClash/e553e82e01c697aefbe1555261a503f425e00ccd/luci-app-openclash/root/usr/share/openclash/YAML.rb"
YAML_SHA = "1249abf411e1df9e8fe542fb3584f34a27e6e3a587942e5d9f759a32b1bd8261"


def download(url, expected):
    request = urllib.request.Request(url, headers={"User-Agent": "openclash-candidate-validation"})
    with urllib.request.urlopen(request, timeout=90) as response:
        value = response.read()
    if hashlib.sha256(value).hexdigest() != expected:
        raise ValueError("public validation download hash mismatch")
    return value


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    if platform.system() != "Linux" or platform.machine() not in ("x86_64", "AMD64"):
        parser.error("this downloader is for Linux amd64 CI; Windows validation uses the separately verified official ZIP")
    args.directory.mkdir(parents=True, exist_ok=True)
    core = args.directory / "mihomo"
    core.write_bytes(gzip.decompress(download(CORE_URL, CORE_SHA)))
    core.chmod(0o700)
    (args.directory / "YAML.rb").write_bytes(download(YAML_URL, YAML_SHA))
    print("Pinned native core and official OpenClash merge library verified")
