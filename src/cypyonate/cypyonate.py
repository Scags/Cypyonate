import argparse
import win32api
import win32con
import win32process
import win32com.client
import os

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
		p = argparse.ArgumentParser(prog="cypy", description="Command-line DLL injector")
		p.add_argument("-i", "--inject", dest="injection", metavar="injection", help="target process (ID or name)")
		p.add_argument("-p", "--payload", dest="payload", metavar="payload", help="payload file path")
#		p.add_argument("-v", "--version", dest="version", action="store_true", help="Print version and exit")
#		p.add_argument("-l", "--list", dest="listprocs", action="store_true", help="List injectable processes")

		args = p.parse_args(namespace=self)
#		if args.listprocs:
#			self.list()
		if args.injection:
			self.inject(args.injection, args.payload)
		elif args.payload:
			self.printe("No target specified (-i)")
		else:
			p.print_help()

	def printe(self, s, witherror=True):
		# Print error
		print(f"{colors.FAIL}[!]{s}{colors.ENDC}")
		# if witherror:
		# 	er = win32api.GetLastError()
		# 	if er != 0:
		# 		self.printe(f"Error code: {er}", False)

	def printg(self, s):
		# Print continuation output
		print(f"{colors.OKGREEN}[+]{colors.ENDC}{s}")

	def printc(self, s):
		# Print cyan output
		print(f"{colors.OKCYAN}{s}{colors.ENDC}")
	
	def inject(self, target: str, payload: str):
		if not payload:
			self.printe("No payload specified (-p)")
			return

		# If target is proc id, get the process from it
		proc = 0
		if target.isdigit():
			proc = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, int(target))
		# Otherwise, get the process by name
		else:
			wmi = win32com.client.GetObject("winmgmts:")
			pids = wmi.ExecQuery(f"Select * from Win32_Process where Name = '{target}'")
			if not pids or not len(pids):
				self.printe(f"Could not find process {target}")
				return

			proc = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, pids[0].ProcessId)

		if not proc:
			self.printe("Could not open process")
			return

		# Make sure we are injecting a valid file
		if not os.path.isfile(payload):
			self.printe(f"Payload path {payload} is not a valid file")
			return

		self.printg(f"Injecting {payload} into {target}")

		# Allocate memory the size of the payload name
		abspath = os.path.abspath(payload)
		b = bytes(abspath, 'utf-8') + b'\x00'

		mem = win32process.VirtualAllocEx(proc, 0, len(b), win32con.MEM_COMMIT|win32con.MEM_RESERVE, win32con.PAGE_READWRITE)
		if not mem:
			self.printe("Could not allocate memory")
			return

		# Write the payload name to the allocated memory
		written = win32process.WriteProcessMemory(proc, mem, b)
		if not written:
			self.printe("Could not write to memory")
			return

		# Get the address of LoadLibraryA
		load_library = win32api.GetProcAddress(win32api.GetModuleHandle("kernel32"), "LoadLibraryA")
		if not load_library:
			self.printe("Could not get address of LoadLibraryA")
			return
		
		# Create a thread to call LoadLibraryA
		threadhandle, _ = win32process.CreateRemoteThread(proc, None, 0, load_library, mem, 0)
		if not threadhandle:
			self.printe("Could not create thread")
			return

		# Close handles
		win32api.CloseHandle(threadhandle)
		win32api.CloseHandle(proc)
		
		self.printc("Injection successful")

	def list(self):
		pass
		

def main():
	Cypyonate()

if __name__ == "__main__":
	main()