# Cypyonate
Cypyonate is an extendable command-line injector built entirely in Python. It is named after testosterone cypionate, an injectable form of the hormone.

# Features
Cypyonate currently has 5 injection forms which can be selected with the `--form` argument
- LoadLibrary DLL Injection
- Shellcode Injection
- Manual Map DLL Injection
- Thread Hijack LoadLibrary Injection (Only seems to work ~90% of the time)
- Early Bird APC Shellcode Injection
- Early Bird APC DLL Injection

More methods can be added with relative ease. See [Adding Injection Methods](https://github.com/Scags/cypyonate#adding-injection-methods).

# Installation
### Requirements
Latest tested with Python 3.11.0. **Requires** Python 3.10+.

The following Python packages are required by Cypyonate and can be install with `pip install -r requirements.txt` if installing manually:
- pefile
- pywin32
- colorama
- setuptools

### Installation Process
```
PS C:\Dev> git clone https://github.com/Scags/Cypyonate.git
PS C:\Dev> pip install .\Cypyonate\
```

You can also install directly from [Pypi](https://pypi.org/project/Cypyonate/) with `pip install cypyonate`

### Installing Multiple Architectures
Cypyonate cannot execute properly under a different architecture than what it was installed with.

If you want to install Cypyonate for x86, you must download the x86 version of Python, then run `pip install` from that Python version. After doing so, go to your Python installation's `Scripts/` folder and rename `cypy.exe` to something else like `cypy32.exe`. This should be found in `C:\Users\<you>\AppData\Local\Programs\Python\<python-version>\Scripts`.

If you do *not* change the executeable name, then the most recently installed Python version (on your PATH) takes precedent and executes whenever you run the `cypy` command. Sadly, these are the rules for now because pyproject.toml's aren't capable of differentiating between architectures.
# Usage
```
usage: cypy [-h] [-i injection] [-p payload] [-v] [-f form] [-l]    
            [-w duration] [--install module] [--remove module]
            [-V] [-r] [--clear-header clear_header]
            [--clear-unneeded-sections clear_unneeded_sections]     
            [--sehsupport sehsupport]
            [--adjust-protections adjust_protections]
            [--fdwreason fdwReason] [--lpvreserved lpvReserved]     
            [--check-time check_time]

Command-line injector

options:
  -h, --help            show this help message and exit
  -i injection, --inject injection
                        target process (ID or name) (default:       
                        None)
  -p payload, --payload payload
                        payload file path (use '-' for stdin)       
                        (default: None)
  -v, --verbose         verbosely print output (default: False)     
  -f form, --form form  form of injection (see --list) (default:    
                        default)
  -l, --list            list available injection forms (default:    
                        False)
  -w duration, --wait duration
                        duration of time to wait for remote thread  
                        to finish in milliseconds, in applicable    
                        injection techniques (default: 10000)       
  --install module      install a module (default: None)
  --remove module       remove a module (default: None)
  -V, --version         view Cypyonate's current version and        
                        architecture (default: False)
  -r, --reflective      inject reflectively (only applicable to     
                        some injection forms) (default: False)      

manual mapping injection:
  --clear-header clear_header
                        clear the header of the payload after       
                        injection (default: True)
  --clear-unneeded-sections clear_unneeded_sections
                        clear unneeded sections for the target      
                        binary to run after injection (default:     
                        True)
  --sehsupport sehsupport
                        if clearing unneeded sections, clear        
                        .pdata as well (default: True)
  --adjust-protections adjust_protections
                        adjust the protections of target binary     
                        after injection (default: True)
  --fdwreason fdwReason
                        the fdwReason parameter to pass to DllMain  
                        (default: 1)
  --lpvreserved lpvReserved
                        the lpvReserved parameter to pass to        
                        DllMain (default: 0)
  --check-time check_time
                        time to wait between checks for shellcode   
                        to finish execution, if applicable
                        (default: 1.0)
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

# Reflective Injection
*New with V1.3*

Cypyonate is capable of performing reflective injections.

This is currently supported by the current forms:
- Shellcode Injection
- Manual Map DLL Injection
- Early Bird APC Shellcode Injection

To perform a reflective injection, simply pass a base64 encoded string as the payload and add the `-r` argument.