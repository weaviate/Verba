# Installing Python and Setting Up a Virtual Environment

Before you can use Verba, you'll need to ensure that `Python >=3.10.0` is installed on your system and that you can create a virtual environment for a safer and cleaner project setup.

## Installing Python

Python is required to run Verba. If you don't have Python installed, follow these steps:

### For Windows:

Download the latest Python installer from the official Python website.
Run the installer and make sure to check the box that says `Add Python to PATH` during installation.

### For macOS:

You can install Python using Homebrew, a package manager for macOS, with the following command in the terminal:

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Then install Python:

```
brew install python
```

### For Linux:

Python usually comes pre-installed on most Linux distributions. If it's not, you can install it using your distribution's package manager. You can read more about it [here](https://opensource.com/article/20/4/install-python-linux)

## Setting Up a Virtual Environment

It's recommended to use a virtual environment to avoid conflicts with other projects or system-wide Python packages.

### Install the virtualenv package:

First, ensure you have pip installed (it comes with Python if you're using version 3.4 and above).
Install virtualenv by running:

```
pip install virtualenv
```

### Create a Virtual Environment:

Navigate to your project's directory in the terminal.
Run the following command to create a virtual environment named venv (you can name it anything you like):

```
python3 -m virtualenv venv
```

### Activate the Virtual Environment:

- On Windows, activate the virtual environment by running:

```
venv\Scripts\activate.bat
```

- On macOS and Linux, activate it with:

```
source venv/bin/activate
```

Once your virtual environment is activated, you'll see its name in the terminal prompt. Now you're ready to install Verba using the steps provided in the Quickstart sections.

> Remember to deactivate the virtual environment when you're done working with Verba by simply running deactivate in the terminal.
