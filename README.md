# Cypyonate
 Python-based command-line DLL injector. Named after testosterone cypionate, an injectable form of the hormone.

# Installation
```
PS C:\Dev> git clone https://github.com/Scags/Cypyonate.git
PS C:\Dev> pip3 install .\Cypyonate\
//OR
PS C:\Dev> cd .\Cypyonate\
PS C:\Dev\Cypyonate> py .\setup.py install
```
# Usage
```
usage: cypy [-h] [-i injection] [-p payload] [-s] [-w duration] [-v]

Command-line DLL injector

options:
  -h, --help            show this help message and exit
  -i injection, --inject injection
                        target process (ID or name)
  -p payload, --payload payload
                        payload file path
  -s, --shellcode       inject as shellcode
  -w duration, --wait duration
                        Duration of time to wait for thread to finish (in milliseconds, default 10000)
  -v, --verbose         Verbosely print output
```
