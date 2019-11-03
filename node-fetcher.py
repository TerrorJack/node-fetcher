#!/usr/bin/env python3

from argparse import ArgumentParser
from html.parser import HTMLParser
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


def get_str(url):
    return get_bytes(url).decode()


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


class V8SuccessBuildURLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.flag = False
        self.url = None

    def handle_starttag(self, tag, attrs):
        if self.url:
            return
        if attrs == [("class", "status SUCCESS")]:
            self.flag = True
        if self.flag and tag == "a":
            self.url = "https://ci.chromium.org{0}".format(attrs[0][1])


def get_node_v8_success_build_url():
    p = V8SuccessBuildURLParser()
    p.feed(get_str("https://ci.chromium.org/p/v8/builders/luci.v8.ci/V8%20Linux64%20-%20node.js%20integration%20ng"))
    return p.url


class V8ZipURLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.url = None

    def handle_starttag(self, tag, attrs):
        if len(attrs) >= 3 and attrs[2][1] and attrs[2][1].startswith("https://storage.googleapis.com/chromium-v8/node-linux-rel"):
            self.url = attrs[2][1]


def get_node_v8_zip_url(build_url):
    p = V8ZipURLParser()
    p.feed(get_str(build_url))
    return p.url


def extract_node_v8_zip(path):
    with ZipFile(BytesIO(get_bytes(get_node_v8_zip_url(get_node_v8_success_build_url())))) as z:
        z.extractall(path=path)
    for f in Path(path, "bin").iterdir():
        f.chmod(0o755)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--channel", help="The release channel to check, e.g. \"v8-canary\", defaults to \"release\"")
    parser.add_argument(
        "--platform", help="Supported platforms: {win,linux,darwin}-x64, defaults to current platform")
    parser.add_argument(
        "--version", help="The version string prefix to match, e.g. v13")
    parser.add_argument(
        "--path", help="The destination to extract, defaults to current working directory")
    args = parser.parse_args()
    path = args.path if args.path else os.getcwd()
    chan = args.channel if args.channel else "release"
    if chan == "v8":
        extract_node_v8_zip(path)
    else:
        platform = args.platform if args.platform else {"win32": "win-x64", "linux": "linux-x64",
                                                        "darwin": "darwin-x64"}[sys.platform]
        ver = get_node_ver(get_node_index(chan), platform,
                           args.version if args.version else "")

        (extract_node_zip if platform ==
         "win-x64" else extract_node_tar)(chan, platform, ver, path)
