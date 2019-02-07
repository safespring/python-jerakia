# python-jerakia

A Python client library for Jerakia server (https://jerakia.io)

## Getting started

Make a new _virtualenv_ – we are testing with python 2.7, 3.6

```bash
mkvirtualenv --python=python2.7 python-jerakia
```

```bash
pip install -e .
```

## Usage

### Command line tool

```bash
$ jerakia lookup --help
Usage: jerakia lookup [OPTIONS] NAMESPACE KEY

Options:
  -T, --token TEXT
  -P, --port TEXT
  -H, --host TEXT
  --protocol TEXT
  -t, --type TEXT
  -p, --policy TEXT
  -m, --metadata TEXT
  -i, --configfile PATH
  --help                 Show this message and exit.
```

Lookup [KEY] with Jerakia

## configuration

The command line tool use a config file, default location is
`'$HOME/.jerakia/jerakia.yaml'`, or specify the location with the  `-i`-option

The configuration file format is yaml, an see an example below:

```yaml
---
token: "dev:e1b903ecee4e33550c376ed436aaf7ed4c5e6e72cc05a877e155d24f63a344cc881b0e3f4c01fd7f"
host: "localhost"
port: 9843
```

### Python example

With a Jerakia server running on localhost, do

```bash
python
import jerakia
token = 'dev:ac4093fec97c6d52f3b419db9b744d214d7428b0e0f75f2d98b8016df5b79dd819743583c047f47f'
client = jerakia.Client(token=token)
client.lookup(key='test',namespace='common')
```

Example of using the command line tool with a config file:

```bash
jerakia lookup -i jerakia.yaml common open
```

## running tests

```bash
pip install pytest
pytest
```
