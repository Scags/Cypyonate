# Cypyonate
Cypyonate is an extendable command-line injector built entirely in Python. It is named after testosterone cypionate, an injectable form of the hormone.

# Features
Cypyonate currently has 5 injection forms which can be selected with the `--form` argument
- LoadLibrary DLL Injection
- Shellcode Injection
- Manual Map DLL Injection
- Thread Hijack LoadLibrary Injection (Only seems to work ~90% of the time)
- Early Bird APC Shellcode Injection

More methods can be added with relative ease. See [Adding Injection Methods](https://github.com/Scags/cypyonate#adding-injection-methods).

# Installation
### Requirements
Latest tested with Python 3.11.0

The following Python packages are required by Cypyonate and can be install with `pip install -r requirements.txt`
- pefile
- pywin32
- colorama
- setuptools

### Installation Process
```
PS C:\Dev> git clone https://github.com/Scags/Cypyonate.git
PS C:\Dev> pip install .\Cypyonate\
//OR
PS C:\Dev> cd .\Cypyonate\
PS C:\Dev\Cypyonate> py .\setup.py install
```

### Installing Multiple Architectures
Cypyonate cannot execute under a different architecture than what it was installed with. If you want to install Cypyonate for another architecture (e.g. x86), you must download that version of Python, then run `pip install` from that Python version.

Cypyonate changes its command depending on the architecture of the Python installation that installs it. If running x64, the command is `cypy`. If running x86, the command is `cypy32`. Assure that your Python installation's `Scripts/` directory is added to your PATH.
# Usage
```
usage: cypy [-h] [-i injection] [-p payload] [-v] [-f form] [-l] [-w duration]
            [--clear-header clear_header]
            [--clear-unneeded-sections clear_unneeded_sections]
            [--sehsupport sehsupport]
            [--adjust-protections adjust_protections] [--fdwreason fdwReason]
            [--lpvreserved lpvReserved] [--check-time check_time]

Command-line injector

options:
  -h, --help            show this help message and exit
  -i injection, --inject injection
                        target process (ID or name) (default: None)
  -p payload, --payload payload
                        payload file path (default: None)
  -v, --verbose         Verbosely print output (default: False)
  -f form, --form form  Form of injection (see --list) (default: default)
  -l, --list            List available injection forms (default: False)
  -w duration, --wait duration
                        Duration of time to wait for remote thread to finish
                        in milliseconds, in applicable injection techniques
                        (default: 10000)

Manual Map:
  Manual mapping injection

  --clear-header clear_header
                        Don't clear the header of the payload after injection
                        (default: 1)
  --clear-unneeded-sections clear_unneeded_sections
                        Don't clear unneeded sections for the target binary to
                        run after injection (default: 1)
  --sehsupport sehsupport
                        If clearing unneeded sections, clear .pdata as well
                        (default: 1)
  --adjust-protections adjust_protections
                        Don't adjust the protections of target binary after
                        injection (default: 1)
  --fdwreason fdwReason
                        The fdwReason parameter to pass to DllMain (default:
                        1)
  --lpvreserved lpvReserved
                        The lpvReserved parameter to pass to DllMain (default:
                        0)
  --check-time check_time
                        Time to wait between checks for shellcode to finish
                        execution, if applicable (default: 1.0)
```
# Adding Injection Methods
Create a new .py file, import the main cypyonate module, and create a class that inherits from cypyonate.Module. Overload the `inject()` function and implement your code.

You *must* use a relative import like below, as installing the module with place it within the "modules" subfolder in the project.

```py
from .. import cypyonate as cypy

class MyInjection(cypy.Module):
	def __init__(self):
		super().__init__(name="My Injection", frmat="myinjection", desc="My custom injection method")

  def add_to_argparse(self, parser):
    # If you want to add options to the "cypy" command argument handler
    pass

  def inject(self, handler: cypy.Cypyonate, target: str, payload: str, verbose: bool):
    # Run code here
    pass
```

To finalize adding your module, enter the command `cypy --install myfile.py`. This will copy the file to the project modules folder.