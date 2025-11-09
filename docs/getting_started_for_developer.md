# Getting Started for Developers

## Develop using 'development mode'

```bash
python3 -m virtualenv .venv
. .venv/bin/activate

pip3 install -e .
# modifications in src folder are available without re-packaging or re-installation
deactivate
```

## Building with tox

This project uses *tox* as a central build management tool.

Install tox and show all available commands (environments):

```bash
pip3 install -r requirements.txt
python3 -m tox -a -v
```

The first call of tox usually takes some time, further calls are faster.

### Generate HTML Documentation

Generate documentation which is placed at `build/docs/`:

```bash
python3 -m tox -e docs
```

**Note:** The file `CHANGELOG.md` is copied from project root directory into `docs/`. The copied file must not be changed.

### Run Tests

Run tests in *developer*/*editable* mode:

```bash
python3 -m tox --develop -e tests
```

Reports are located in `build/tests`.

### Run Code Analysis & Style Checks

```bash
python3 -m tox -e check_code
python3 -m tox -e check_style
python3 -m tox -e check_types
```

### Build Wheel Package

Build the wheel package with tox and an isolated environment is not yet possible.
It can be built with:

```bash
pip3 install build
python3 -m build --wheel .
```

It is located in `dist/`.
