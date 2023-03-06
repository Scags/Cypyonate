import argparse
import win32api
import win32con
import win32com.client
import os
import importlib
import inspect

from colorama import just_fix_windows_console


class colors(object):
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKCYAN = '\033[96m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'


class Cypyonate(object):
	def __init__(self):
		self._modules = []
		self._map = {}
		self.argparse = argparse.ArgumentParser(
			prog="cypy", description="Command-line injector", prefix_chars="-/", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

	def _call(self, name, *args, **kwargs):
		for module in self._modules:
			if hasattr(module, name):
				getattr(module, name)(*args, **kwargs)

	def _setup_args(self):
		self.argparse.add_argument("-i", "--inject", dest="target",
		                           metavar="injection", help="target process (ID or name)")
		self.argparse.add_argument(
			"-p", "--payload", dest="payload", metavar="payload", help="payload file path")
		self.argparse.add_argument("-v", "--verbose", dest="verbose",
		                           action="store_true", help="verbosely print output")
		self.argparse.add_argument("-f", "--form", dest="form", metavar="form",
		                           default="default", help="form of injection (see --list)")
		self.argparse.add_argument("-l", "--list", dest="list",
		                           action="store_true", help="list available injection forms")
		self.argparse.add_argument("-w", "--wait", dest="duration", metavar="duration", type=int, default=10000,
		                           help="duration of time to wait for remote thread to finish in milliseconds, in applicable injection techniques")
		self.argparse.add_argument(
			"--install", dest="install", metavar="module", help="install a module")
		self.argparse.add_argument("--remove", dest="remove", metavar="module", help="remove a module")
		self.argparse.add_argument("--arch", dest="arch", action="store_true", help="view Cypyonate's current architecture")

		self._call("add_to_argparse", self.argparse)

	def _run(self):
		args = self.argparse.parse_args(namespace=self)

		self._call("run", self)

		if args.list:
			self._list()
		elif args.install:
			self._install_module()
		elif args.remove:
			self._remove_module()
		elif args.arch:
			self._print_arch()
		elif args.target:
			self._inject()
		elif args.payload:
			self.argparse.print_help()
			printe("No target specified (-i)")
		else:
			self.argparse.print_help()

		self._call("run_post", self)

	def _print_arch(self):
		printc(f"Cypyonate is currently running in {'x64' if is64bit() else 'x86'} mode")

	def _remove_module(self):
		# Try to remove by file name
		file = self.remove
		path = os.path.dirname(os.path.abspath(__file__))
		if not file.endswith(".py"):
			file += ".py"

		module_path = f"{path}/modules/{file}"
		if os.path.exists(module_path):
			os.remove(module_path)
			printc(f"Successfully removed module {self.remove}")
			return

		# Try to remove by format name
		frmat = self.remove
		module = self._map.get(frmat.lower())
		if module:
			if os.path.exists(module.filename):
				os.remove(module.filename)
				printc(f"Successfully removed module {frmat}")
				return
			printe(f"Module file does not exist at {module.filename}???")

		printe(f"Could not find module {self.remove}")
		printe("Target either a file name or a format name (e.g. 'default')")

	def _install_module(self):
		path = os.path.dirname(os.path.abspath(__file__))
		if not self.install.endswith(".py"):
			self.install += ".py"

		if not os.path.exists(self.install):
			printe(f"Could not find module {self.install}")
			return

		file_name = self.install
		if "/" in file_name:
			file_name = file_name.split("/")[-1]

		module_path = f"{path}/modules/{file_name}"
		if os.path.exists(module_path):
			printw(f"Overwriting existing module {file_name}")

		with open(module_path, "w") as f:
			with open(self.install, "r") as f2:
				f.write(f2.read())

		printc(f"Successfully installed module {self.install}")

	def _init_modules(self):
		path = os.path.dirname(os.path.abspath(__file__))
		module_names = [os.path.splitext(f)[0] for f in os.listdir(
			f"{path}/modules") if f.endswith(".py")]
		for name in module_names:
			importlib.import_module(f".{name}", "cypyonate.modules")

	def _list(self):
		print("Available injection forms:")
		maxname = 30
		maxformat = 30
		lastname = 0
		lastformat = 0

		# First iteration of modules
		for module in self._modules:
			formats = module.format
			if not isinstance(formats, str):
				formats = ",".join(module.format)

			currname = min(maxname, len(module.name))
			currformat = min(maxformat, len(formats))

			lastname = max(lastname, currname)
			lastformat = max(lastformat, currformat)

		lastname += 2
		lastformat += 2

		# Dynamic size formatting :D
		print(f"{'Name':<{lastname}}{'Format(s)':<{lastformat}}{'Description'}")
		for module in self._modules:
			formats = module.format
			if not isinstance(formats, str):
				formats = ",".join(module.format)

			print(f"{module.name:<{lastname}}{formats:<{lastformat}}{module.description}")

	def _inject(self):
		if not self.payload:
			self.argparse.print_help()
			printe("No payload specified (-p)")
			return

		form = self.form
		if not form:
			form = "default"

		# Get the module
		module = self._map.get(form.lower())
		if not module:
			printe(f"Could not find injection form {form.lower()}")
			return

		# Make sure we are injecting a valid file
		if not os.path.isfile(self.payload):
			printe(f"Payload path {self.payload} is not a valid file")
			return

		# Run the module
		printv(f"Injecting {self.payload} into {self.target}")
		module.inject(self, self.target, self.payload, self.verbose)

	def _add_module(self, module):
		self._modules.append(module)

		if isinstance(module.format, tuple):
			for x in module.format:
				self._map[x.lower()] = module
		else:
			self._map[module.format.lower()] = module


CYPY = None


# Print error
def printe(s):
	print(f"{colors.FAIL}[!]{s}{colors.ENDC}")


# Print continuation output
def printg(s):
	print(f"{colors.OKGREEN}[+]{colors.ENDC}{s}")


# Print cyan output
def printc(s):
	print(f"{colors.OKCYAN}{s}{colors.ENDC}")


# Verbose log output
def printv(s):
	if CYPY.verbose:
		print(f"{colors.OKBLUE}[*]{colors.ENDC}{s}")


# Warning output
def printw(s):
	print(f"{colors.WARNING}[!]{s}{colors.ENDC}")


# Get a process handle from an input string
def get_process(inpt: str):
	# If target is proc id, get the process from it
	proc = 0
	if inpt.isdigit():
		printv(f"Getting process from PID {inpt}")
		proc = win32api.OpenProcess(
			win32con.PROCESS_ALL_ACCESS, False, int(inpt))
	# Otherwise, get the process by name
	else:
		printv(f"Getting process from name {inpt}")
		wmi = win32com.client.GetObject("winmgmts:")
		pids = wmi.ExecQuery(
			f"Select * from Win32_Process where Name = '{inpt}'")

		if not pids or not len(pids):
			return 0

		proc = win32api.OpenProcess(
			win32con.PROCESS_ALL_ACCESS, False, pids[0].ProcessId)

	printv(f"Acquired process {proc}")
	return proc

# Is Cypy running in 64 bit mode
def is64bit():
	import sys
	return sys.maxsize > 2**32


class Module(object):
	def __init__(self, name: str, frmat: str | tuple, desc: str = ""):
		self.name = name
		self.format = frmat
		self.description = desc
		self.filename = inspect.stack()[1].filename
		CYPY._add_module(self)

	# Add arguments to the argparse parser
	def add_to_argparse(self, parser: argparse.ArgumentParser):
		pass

	# Run the module
	def inject(self, target: str, payload: str, verbose: bool):
		raise NotImplementedError(f"{self.name}: Module.inject() not implemented")

	# When cypy is run
	# Return true to stop further cypy execution
	def run(self, handler: Cypyonate):
		return False

	# When cypy is run, after everything goes
	def run_post(self, handler: Cypyonate):
		pass


def main():
	just_fix_windows_console()
	global CYPY
	CYPY = Cypyonate()
	CYPY._init_modules()
	CYPY._setup_args()
	CYPY._run()


if __name__ == "__main__":
	main()
