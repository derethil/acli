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
acli login:set username=myusername password=mypassword
```

## Usage


To add `x` hours to the current date's log:

```
acli log x
```

Deleting a shift:
```
acli delete <shift>
```

Displaying your submitted hours:
```
acli hours
```
