import os
import win32process
import win32con
import win32api
import win32event

from .. import cypyonate as cypy


class DefaultInjector(cypy.Module):
	def __init__(self):
		super().__init__("Default", ("default", "loadlibrary"), "Basic loadlibrary injection")

	def inject(self, handler: cypy.Cypyonate, target: str, payload: str, verbose: bool):
		is64 = cypy.is64bit()
		proc = cypy.get_process(target)
		if not proc:
			cypy.printe(f"Could not find process {target}")
			return

		# if (win32process.IsWow64Process(proc) and not is64) or (not win32process.IsWow64Process(proc) and is64):
		# 	cypy.printe(
		# 		f"Cannot inject into {target} because Cypyonate is running in {'32-bit' if is64 else '64-bit'} mode. Please execute Cypyonate in {'64-bit' if is64 else '32-bit'} mode.")
		# 	return

		abspath = os.path.abspath(payload)
		b = abspath.encode() + b"\x00"
		cypy.printv(f"Allocating DLL file at {abspath} ({len(b)} bytes)")

		mem = win32process.VirtualAllocEx(proc, 0, len(
			b), win32con.MEM_COMMIT | win32con.MEM_RESERVE, win32con.PAGE_READWRITE)

		if not mem:
			cypy.printe("Could not allocate memory")
			return

		cypy.printv(f"Allocated {len(b)} bytes at {mem:X}")

		written = win32process.WriteProcessMemory(proc, mem, b)
		if not written:
			cypy.printe("Could not write to memory")
			return

		cypy.printv(f"Wrote {written} bytes to {mem:X}")

		# Get the address of LoadLibraryA
		cypy.printv("Getting address of LoadLibraryA")
		startaddr = win32api.GetProcAddress(
			win32api.GetModuleHandle("kernel32"), "LoadLibraryA")
		if not startaddr:
			cypy.printe("Could not get address of LoadLibraryA")
			return

		# Create a thread
		cypy.printv(
			f"Creating thread at address {startaddr:X}")
		threadhandle, _ = win32process.CreateRemoteThread(
			proc, None, 0, startaddr, mem, 0)
		if not threadhandle:
			cypy.printe("Could not create thread")
			return

		cypy.printv("Waiting for thread to finish")
		# Wait for the thread to finish
		win32event.WaitForSingleObject(threadhandle, handler.duration)

		# Free the allocated memory
		cypy.printv("Freeing allocated memory")
		win32process.VirtualFreeEx(proc, mem, 0, win32con.MEM_RELEASE)

		cypy.printv("Closing handles")
		# Close handles
		win32api.CloseHandle(threadhandle)
		win32api.CloseHandle(proc)

		cypy.printc(f"Injected {payload} into {target}")


DefaultInjector()
