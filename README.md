# hyper-python-sdk

Python SDK for interacting with the Hyper.systems platform.

Check [here](./antora/modules/ROOT/pages/index.adoc) for usage and other documentation.

**Pypi.org:**

[![Supported Versions](https://img.shields.io/pypi/pyversions/hyper-systems.svg)](https://pypi.org/project/hyper-systems)

## Installing

Install the latest version globally using pip:

```shell
pip install -U hyper-systems
```

### Adding as a dependency to your project

Add to `requirements.txt` for pip:

```shell
echo "hyper-systems==1.3.0" >> requirements.txt
```

Consider using [venv](https://docs.python.org/3/tutorial/venv.html), if you want to have an isolated environment for your project with pip.

Alternatively, install with poetry:

```shell
poetry add "hyper-systems==1.3.0"
```

### Installing the latest development version of the package globally

```shell
$ pip install -U git+https://github.com/hyper-systems/hyper-python-sdk.git@master
```

## Using this repo for development

This repo uses [poetry](https://python-poetry.org/) (please check the [docs](https://python-poetry.org/docs/)) for development and building. It is currentlu set up to create a `.venv` directory in the root of this project on install.


Installing the environment:

```shell
$ poetry install
```

### Shell usage

After installing you can use the environment created with poetry, for example to:

- update the environment:

```shell
$ poetry update
```

- execute scripts:

```shell
$ poetry run tests/test_devices.py
```

### VSCode

You can also use the environment in VSCode by opening one of the python files in this repo and selecting the poetry python interpreter in the bottom left corner (`('.venv': poetry)`). You then reload the VSCode window (or open and close VSCode) and VSCode should be now using the `.venv` environment created by poetry.
