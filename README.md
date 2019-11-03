# `node-fetcher`

A script to fetch and extract `node` release tarballs, useful for testing
multiple versions of `node` on CI.

## Usage

```
usage: node-fetcher.py [-h] [--channel CHANNEL] [--platform PLATFORM]
                       [--version VERSION] [--path PATH]

optional arguments:
  -h, --help           show this help message and exit
  --channel CHANNEL    The release channel to check, e.g. "v8-canary",
                       defaults to "release"
  --platform PLATFORM  Supported platforms: {win,linux,darwin}-x64, defaults
                       to current platform
  --version VERSION    The version string prefix to match, e.g. v13
  --path PATH          The destination to extract, defaults to current working
                       directory

```

Check the `node` [download](https://nodejs.org/download/) page for a list of
channels.

Additionally, we support a `v8` channel which fetches the V8 team's latest
successful
[build](https://ci.chromium.org/p/v8/builders/ci/V8%20Linux64%20-%20node.js%20integration%20ng).
The `--channel v8` flag will ignore `--platform` and `--version`, since the V8
team only provides linux x64 builds, and there isn't a meaningful version number
for those builds. Also, keep in mind that compared to the `v8-canary` builds
provided by the `node` folks, the `v8` builds only comes with a `bin/node`
executable without `npm` packaged.

## Why not `nvm`?

`nvm` is not a proper executable, which makes it tricky to be invoked by
programs. Also, it doesn't support Windows.
