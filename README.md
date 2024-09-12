## Installation
To install the azconnect CLI tool, you'll need `pipx`, which can be found at [pipx installation](https://pipx.pypa.io/stable/installation/#on-linux). Once installed, run the following command:

```bash
pipx install git+https://github.com/joe-macmillan/qconnect
```
## Usage
To test if the azconnect CLI tool works, first connect to Azure using `az login`, then run the following command:
```bash
qc ls
```
This command should output a table listing all available clusters.

Note: `qc` caches the list of available clusters for 24 hours to speed up subsequent runs. However, if clusters are added or deleted, you can update the list by running `qc refresh`.
