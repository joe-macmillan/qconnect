## Installation
Run the following command to install the cli tool
```bash
pipx install git+https://github.com/joe-macmillan/qconnect
```
To test if the cli tool works, make sure to run `az login` to connect to Azure and then run the following command:
```bash
qc list
```
The output should look like a table listing all the clusters available.