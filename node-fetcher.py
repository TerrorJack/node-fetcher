#!/usr/bin/env python3

from argparse import ArgumentParser
from io import BytesIO
import json
import os
from pathlib import Path
import shutil
import sys
import tarfile
from urllib.request import urlopen
from zipfile import ZipFile


def get_bytes(url):
    return urlopen(url).read()


def get_node_index(chan):
    return json.load(urlopen("https://nodejs.org/download/{0}/index.json".format(chan)))


def get_node_ver(idx, platform, ver_prefix):
    f = {"win-x64": "win-x64-zip", "linux-x64": "linux-x64",
         "darwin-x64": "osx-x64-tar"}[platform]
    for item in idx:
        if item["version"].startswith(ver_prefix) and f in item["files"]:
            return item["version"]


def get_node_url(chan, platform, ver):
    return "https://nodejs.org/download/{0}/{2}/node-{2}-{1}{3}".format(chan, platform, ver, ".zip" if platform == "win-x64" else ".tar.xz")


def get_node_bytes(chan, platform, ver):
    return get_bytes(get_node_url(chan, platform, ver))


def get_node_tar(chan, platform, ver):
    return tarfile.open(mode="r:xz", fileobj=BytesIO(get_node_bytes(chan, platform, ver)))


def extract_node_tar(chan, platform, ver, path):
    with get_node_tar(chan, platform, ver) as t:
        t.extractall(path=path)
    sub_path = Path(path, "node-{1}-{0}".format(platform, ver))
    for f in sub_path.iterdir():
        shutil.move(str(f), path)
    sub_path.rmdir()


def get_node_zip(chan, platform, ver):
    return ZipFile(BytesIO(get_node_bytes(chan, platform, ver)))


def extract_node_zip(chan, platform, ver, path):
    with get_node_zip(chan, platform, ver) as z:
        z.extractall(path=path)
    sub_path = Path(path, "node-{1}-{0}".format(platform, ver))
    for f in sub_path.iterdir():
        shutil.move(str(f), path)
    sub_path.rmdir()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--channel", help="The release channel to check, e.g. v8-canary, defaults to release")
    parser.add_argument(
        "--version", help="The version string prefix to match, e.g. v13")
    parser.add_argument(
        "--path", help="The destination to extract, defaults to current working directory")
    args = parser.parse_args()
    chan = args.channel if args.channel else "release"
    platform = {"win32": "win-x64", "linux": "linux-x64",
                "darwin": "darwin-x64"}[sys.platform]
    ver = get_node_ver(get_node_index(chan), platform,
                       args.version if args.version else "")
    path = args.path if args.path else os.getcwd()
    (extract_node_zip if platform ==
     "win-x64" else extract_node_tar)(chan, platform, ver, path)
