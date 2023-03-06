from .. import cypyonate as cypy

import win32process
import win32api
import win32con
import win32event
import ctypes
import os


class PROCESS_INFORMATION(ctypes.Structure):
	_fields_ = [
		("hProcess", ctypes.c_void_p),
		("hThread", ctypes.c_void_p),
		("dwProcessId", ctypes.c_ulong),
		("dwThreadId", ctypes.c_ulong)
	]


class STARTUPINFO(ctypes.Structure):
	_fields_ = [
		("cb", ctypes.c_ulong),
		("lpReserved", ctypes.c_char_p),
		("lpDesktop", ctypes.c_char_p),
		("lpTitle", ctypes.c_char_p),
		("dwX", ctypes.c_ulong),
		("dwY", ctypes.c_ulong),
		("dwXSize", ctypes.c_ulong),
		("dwYSize", ctypes.c_ulong),
		("dwXCountChars", ctypes.c_ulong),
		("dwYCountChars", ctypes.c_ulong),
		("dwFillAttribute", ctypes.c_ulong),
		("dwFlags", ctypes.c_ulong),
		("wShowWindow", ctypes.c_ushort),
		("cbReserved2", ctypes.c_ushort),
		("lpReserved2", ctypes.c_void_p),
		("hStdInput", ctypes.c_void_p),
		("hStdOutput", ctypes.c_void_p),
		("hStdError", ctypes.c_void_p)
	]

def ebinject(handler, target, payload, as_dll):
	if not os.path.exists(target):
		cypy.printe("Early bird injections require a valid path to a process")
		return

	shellcode = b""
	abstarget = os.path.abspath(target)

	if not as_dll:
		cypy.printv("Attempting injection via shellcode")
		if not os.path.exists(payload):
			cypy.printe("Early bird shellcode injections require a valid path to a shellcode file")
			return

		with open(payload, "rb") as f:
			shellcode = f.read()
			# It's a PE file, but continue ig?
			if shellcode[:2] == b"MZ":
				cypy.printw("Payload appears to be a PE file")
				cypy.printw("If you're trying to inject a DLL, use -f ebdll")
				
			cypy.printv(f"Reading shellcode file {payload} ({len(shellcode)} bytes)")
	else:
		if not os.path.exists(payload):
			cypy.printe("Early bird DLL injections require a valid path to a DLL file")
			return

		abspayload = os.path.abspath(payload).encode() + b"\x00"
		shellcode = SHELLCODE
		cypy.printv("Attempting injection via DLL")

		# Need to add the payload to the end of the shellcode because we're using LoadLibraryA as the parameter
		# It's easier this way. Doing it the other way around would require 2 allocations/patches rather than just 1
		if cypy.is64bit():
			lea = shellcode.find(b"\x48\x8D\x0D\x00\x00\x00\x00")
			if lea != -1:
				# lea rcx, [offs_to_dll]
				shellcode = shellcode[:lea + 3] + (len(shellcode) - lea - 7).to_bytes(4, "little") + shellcode[lea + 7:]

		shellcode += abspayload

	si = STARTUPINFO()
	pi = PROCESS_INFORMATION()
	si.cb = ctypes.sizeof(si)

	if not ctypes.windll.kernel32.CreateProcessA(abstarget.encode() + b"\x00", None, None, None, False, win32con.CREATE_SUSPENDED, None, None, ctypes.byref(si), ctypes.byref(pi)):
		cypy.printe("Could not create process")
		cypy.printe(f"Error code: {ctypes.windll.kernel32.GetLastError()}")
		return

	cypy.printv(f"Successfully created process {abstarget} (PID {pi.dwProcessId})")

	mem = win32process.VirtualAllocEx(pi.hProcess, 0, len(
		shellcode), win32con.MEM_COMMIT | win32con.MEM_RESERVE, win32con.PAGE_EXECUTE_READWRITE)

	if not cypy.is64bit():
		lea = shellcode.find(b"\x68\x00\x00\x00\x00")
		if lea != -1:
			# push offs_to_dll
			shellcode = shellcode[:lea + 1] + (mem + len(shellcode) - len(abspayload)).to_bytes(4, "little") + shellcode[lea + 5:]

	win32process.WriteProcessMemory(pi.hProcess, mem, shellcode)

	cypy.printv(f"Successfully allocated {len(shellcode)} bytes of memory at 0x{mem:X} in {abstarget} (PID {pi.dwProcessId})")

	arg = 0
	if as_dll:
		arg = ctypes.windll.kernel32.LoadLibraryA

	os.system("pause")

	ctypes.windll.kernel32.QueueUserAPC(ctypes.cast(mem, ctypes.c_void_p), pi.hThread, ctypes.cast(arg, ctypes.c_void_p))

	win32process.ResumeThread(pi.hThread)

	cypy.printv(f"Successfully resumed thread in {abstarget} (PID {pi.dwProcessId})")

#	win32event.WaitForSingleObject(pi.hThread, -1)

	win32api.CloseHandle(pi.hThread)
	win32api.CloseHandle(pi.hProcess)

	cypy.printc(
		f"Successfully injected {payload} into {target} (PID {pi.dwProcessId})")


class EarlyBird(cypy.Module):
	def __init__(self):
		super().__init__("Early Bird", ("earlybird", "eb"), "Early Bird injection")

	def inject(self, handler: cypy.Cypyonate, target: str, payload: str, verbose: bool):
		ebinject(handler, target, payload, False)


EarlyBird()

class EarlyBirdDLL(cypy.Module):
	def __init__(self):
		super().__init__("Early Bird DLL", ("earlybirddll", "ebdll"), "Early Bird DLL injection")

	def inject(self, handler: cypy.Cypyonate, target: str, payload: str, verbose: bool):
		ebinject(handler, target, payload, True)

EarlyBirdDLL()

if cypy.is64bit():
	SHELLCODE = \
			b"\x48\x89\x4C\x24\x08\x48\x83\xEC\x28\x48\x8D\x0D\x00\x00\x00\x00\xFF\x54\x24\x30\x48\x83\xC4\x28\xC3"
else:
	SHELLCODE = b"\x55\x8B\xEC\x68\x00\x00\x00\x00\xFF\x55\x08\x5D\xC2\x04\x00"
