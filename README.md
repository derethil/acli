# aggietime_cli
A small CLI app to easily add hours onto into Aggietime.

### Dependencies 
This app expects you to have a supported keyring backend installed. For more info, read [Keyring's](https://pypi.org/project/keyring/) homepage.

## Installation

```
git clone https://github.com/jarenglenn/acli.git
cd acli
pip install .
```

You'll also need to set up your login information with
```
acli login username password
```

## Usage


Punching in or out of Aggietime:

```
acli punch
```

Displays whether or not you are punched into Aggietime:
```
acli status
```
