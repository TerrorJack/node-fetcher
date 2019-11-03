# `node-fetcher`

A script to fetch and extract `node` release tarballs. Supports `win-x64`,
`linux-x64` and `darwin-x64`. Useful for testing multiple versions of `node` on
CI.

## Usage

```
usage: node-fetcher.py [-h] [--channel CHANNEL] [--version VERSION]
                       [--path PATH]

optional arguments:
  -h, --help         show this help message and exit
  --channel CHANNEL  The release channel to check, e.g. v8-canary, defaults to
                     release
  --version VERSION  The version string prefix to match, e.g. v13
  --path PATH        The destination to extract, defaults to current working
                     directory
```

## Why not `nvm`?

`nvm` is not a proper executable, which makes it tricky to be invoked by
programs. Also, it doesn't support Windows.
