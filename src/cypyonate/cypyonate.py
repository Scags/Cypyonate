import argparse
import win32api
import win32con
import win32process
import win32com.client
import win32event
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
		p = argparse.ArgumentParser(
			prog="cypy", description="Command-line DLL injector")
		p.add_argument("-i", "--inject", dest="target",
		               metavar="injection", help="target process (ID or name)")
		p.add_argument("-p", "--payload", dest="payload",
		               metavar="payload", help="payload file path")
		p.add_argument("-s", "--shellcode", dest="useshellcode",
		               action="store_true", help="inject as shellcode")
		p.add_argument("-w", "--wait", dest="duration", metavar="duration", type=int, default=10000,
		               help="Duration of time to wait for thread to finish (in milliseconds, default 10000)")
#		p.add_argument("-n", "--no-free", dest="no_free", action="store_true", help="skip freeing allocated memory")
		p.add_argument("-v", "--verbose", dest="verbose",
		               action="store_true", help="Verbosely print output")
#		p.add_argument("-l", "--list", dest="listprocs", action="store_true", help="List injectable processes")

		args = p.parse_args(namespace=self)
#		if args.listprocs:
#			self.list()
		if args.target:
			self.inject()
		elif args.payload:
			self.printe("No target specified (-i)")
		else:
			p.print_help()

	def printe(self, s):
		# Print error
		print(f"{colors.FAIL}[!]{s}{colors.ENDC}")

	def printg(self, s):
		# Print continuation output
		print(f"{colors.OKGREEN}[+]{colors.ENDC}{s}")

	def printc(self, s):
		# Print cyan output
		print(f"{colors.OKCYAN}{s}{colors.ENDC}")

	def printv(self, s):
		# Verbose log output
		if self.verbose:
			print(f"{colors.OKBLUE}[*]{colors.ENDC}{s}")

	def inject(self):
		if not self.payload:
			self.printe("No payload specified (-p)")
			return

		# If target is proc id, get the process from it
		proc = 0
		if self.target.isdigit():
			self.printv(f"Getting process from PID {self.target}")
			proc = win32api.OpenProcess(
				win32con.PROCESS_ALL_ACCESS, False, int(self.target))
		# Otherwise, get the process by name
		else:
			self.printv(f"Getting process from name {self.target}")
			wmi = win32com.client.GetObject("winmgmts:")
			pids = wmi.ExecQuery(
				f"Select * from Win32_Process where Name = '{self.target}'")
			if not pids or not len(pids):
				self.printe(f"Could not find process {self.target}")
				return

			proc = win32api.OpenProcess(
				win32con.PROCESS_ALL_ACCESS, False, pids[0].ProcessId)

		if not proc:
			self.printe("Could not open process")
			return

		self.printv(f"Process {proc} opened")

		# Make sure we are injecting a valid file
		if not os.path.isfile(self.payload):
			self.printe(f"Payload path {self.payload} is not a valid file")
			return

		self.printv(f"Injecting {self.payload} into {self.target}")

		# Allocate memory the size of the payload name
		if self.useshellcode:
			with open(self.payload, "rb") as f:
				b = f.read()
				self.printv(f"Reading shellcode file {self.payload} ({len(b)} bytes)")
		else:
			abspath = os.path.abspath(self.payload)
			b = bytes(abspath, 'utf-8') + b'\x00'
			self.printv(f"Allocating DLL file at {abspath} ({len(b)} bytes)")

		flags = win32con.PAGE_EXECUTE_READWRITE if self.useshellcode else win32con.PAGE_READWRITE
		mem = win32process.VirtualAllocEx(proc, 0, len(
			b), win32con.MEM_COMMIT | win32con.MEM_RESERVE, flags)

		if not mem:
			self.printe("Could not allocate memory")
			return
		self.printv(f"Allocated {len(b)} bytes at {hex(mem)}")

		# Write the payload name to the allocated memory
		written = win32process.WriteProcessMemory(proc, mem, b)
		if not written:
			self.printe("Could not write to memory")
			return
		self.printv(f"Wrote {written} bytes to {hex(mem)}")

		# Get the address of LoadLibraryA
		startaddr = mem
		if not self.useshellcode:
			self.printv("Getting address of LoadLibraryA")
			startaddr = win32api.GetProcAddress(
				win32api.GetModuleHandle("kernel32"), "LoadLibraryA")
			if not startaddr:
				self.printe("Could not get address of LoadLibraryA")
				return

		parameter = 0
		if not self.useshellcode:
			parameter = mem

		# Create a thread
		self.printv(
			f"Creating thread at address {hex(startaddr)} with parameter {hex(parameter)}")
		threadhandle, _ = win32process.CreateRemoteThread(
			proc, None, 0, startaddr, parameter, 0)
		if not threadhandle:
			self.printe("Could not create thread")
			return

		if not self.useshellcode:
			self.printv("Waiting for thread to finish")
			# Wait for the thread to finish
			win32event.WaitForSingleObject(threadhandle, self.duration)

			# Free the allocated memory
			self.printv("Freeing allocated memory")
			win32process.VirtualFreeEx(proc, mem, 0, win32con.MEM_RELEASE)

		self.printv("Closing handles")
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
