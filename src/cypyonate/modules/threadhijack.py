from .. import cypyonate as cypy

import win32process
import win32api
import win32con
import ctypes
import os

TH32CS_SNAPTHREAD = 0x00000004
THREAD_ALL_ACCESS = 0x001FFFFF
if cypy.is64bit():
	CONTEXT_FULL = 0x10000b
else:
	CONTEXT_FULL = 0x100007


class THREADENTRY32(ctypes.Structure):
	_fields_ = [
		("dwSize", ctypes.c_ulong),
		("cntUsage", ctypes.c_ulong),
		("th32ThreadID", ctypes.c_ulong),
		("th32OwnerProcessID", ctypes.c_ulong),
		("tpBasePri", ctypes.c_ulong),
		("tpDeltaPri", ctypes.c_ulong),
		("dwFlags", ctypes.c_ulong)
	]


class M128A(ctypes.Structure):
    _fields_ = [
        ("Low", ctypes.c_ulonglong),
        ("High", ctypes.c_ulonglong)
    ]


class XMM_SAVE_AREA32(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('ControlWord', ctypes.c_int16),
        ('StatusWord', ctypes.c_int16),
        ('TagWord', ctypes.c_byte),
        ('Reserved1', ctypes.c_byte),
        ('ErrorOpcode', ctypes.c_int16),
        ('ErrorOffset', ctypes.c_int32),
        ('ErrorSelector', ctypes.c_int16),
        ('Reserved2', ctypes.c_int16),
        ('DataOffset', ctypes.c_int32),
        ('DataSelector', ctypes.c_int16),
        ('Reserved3', ctypes.c_int16),
        ('MxCsr', ctypes.c_int32),
        ('MxCsr_Mask', ctypes.c_int32),
        ('FloatRegisters', M128A * 8),
        ('XmmRegisters', M128A * 16),
        ('Reserved4', ctypes.c_byte * 96)
    ]


class FLOATING_SAVE_AREA(ctypes.Structure):
	_fields_ = [
		('ControlWord', ctypes.c_int32),
		('StatusWord', ctypes.c_int32),
		('TagWord', ctypes.c_int32),
		('ErrorOffset', ctypes.c_int32),
		('ErrorSelector', ctypes.c_int32),
		('DataOffset', ctypes.c_int32),
		('DataSelector', ctypes.c_int32),
		('RegisterArea', ctypes.c_byte * 80),
		('Cr0NpxState', ctypes.c_int32)
	]


class DUMMYSTRUCTNAME(ctypes.Structure):
    _fields_ = [
        ("Header", M128A * 2),
        ("Legacy", M128A * 8),
        ("Xmm0", M128A),
        ("Xmm1", M128A),
        ("Xmm2", M128A),
        ("Xmm3", M128A),
        ("Xmm4", M128A),
        ("Xmm5", M128A),
        ("Xmm6", M128A),
        ("Xmm7", M128A),
        ("Xmm8", M128A),
        ("Xmm9", M128A),
        ("Xmm10", M128A),
        ("Xmm11", M128A),
        ("Xmm12", M128A),
        ("Xmm13", M128A),
        ("Xmm14", M128A),
        ("Xmm15", M128A)
    ]


class DUMMYUNIONNAME(ctypes.Union):
    _fields_ = [
        ("FltSave", XMM_SAVE_AREA32),
        ("DummyStruct", DUMMYSTRUCTNAME)
    ]


class CONTEXT64(ctypes.Structure):
    _pack_ = 16
    _fields_ = [
        ("P1Home", ctypes.c_ulonglong),
        ("P2Home", ctypes.c_ulonglong),
        ("P3Home", ctypes.c_ulonglong),
        ("P4Home", ctypes.c_ulonglong),
        ("P5Home", ctypes.c_ulonglong),
        ("P6Home", ctypes.c_ulonglong),
        ("ContextFlags", ctypes.c_int32),
        ("MxCsr", ctypes.c_int32),
        ("SegCs", ctypes.c_int16),
        ("SegDs", ctypes.c_int16),
        ("SegEs", ctypes.c_int16),
        ("SegFs", ctypes.c_int16),
        ("SegGs", ctypes.c_int16),
        ("SegSs", ctypes.c_int16),
        ("EFlags", ctypes.c_int32),
        ("Dr0", ctypes.c_ulonglong),
        ("Dr1", ctypes.c_ulonglong),
        ("Dr2", ctypes.c_ulonglong),
        ("Dr3", ctypes.c_ulonglong),
        ("Dr6", ctypes.c_ulonglong),
        ("Dr7", ctypes.c_ulonglong),
        ("Rax", ctypes.c_ulonglong),
        ("Rcx", ctypes.c_ulonglong),
        ("Rdx", ctypes.c_ulonglong),
        ("Rbx", ctypes.c_ulonglong),
        ("Rsp", ctypes.c_ulonglong),
        ("Rbp", ctypes.c_ulonglong),
        ("Rsi", ctypes.c_ulonglong),
        ("Rdi", ctypes.c_ulonglong),
        ("R8", ctypes.c_ulonglong),
        ("R9", ctypes.c_ulonglong),
        ("R10", ctypes.c_ulonglong),
        ("R11", ctypes.c_ulonglong),
        ("R12", ctypes.c_ulonglong),
        ("R13", ctypes.c_ulonglong),
        ("R14", ctypes.c_ulonglong),
        ("R15", ctypes.c_ulonglong),
        ("Rip", ctypes.c_ulonglong),
        ("DebugControl", ctypes.c_ulonglong),
        ("LastBranchToRip", ctypes.c_ulonglong),
        ("LastBranchFromRip", ctypes.c_ulonglong),
        ("LastExceptionToRip", ctypes.c_ulonglong),
        ("LastExceptionFromRip", ctypes.c_ulonglong),
        ("DUMMYUNIONNAME", DUMMYUNIONNAME),
        ("VectorRegister", M128A * 26),
        ("VectorControl", ctypes.c_ulonglong)
    ]

# If GitHub Copilot didn't exist, I probably would've killed myself at this point


class CONTEXT32(ctypes.Structure):
	_fields_ = [
		("ContextFlags", ctypes.c_int32),
		("Dr0", ctypes.c_int32),
		("Dr1", ctypes.c_int32),
		("Dr2", ctypes.c_int32),
		("Dr3", ctypes.c_int32),
		("Dr6", ctypes.c_int32),
		("Dr7", ctypes.c_int32),
		("FloatSave", FLOATING_SAVE_AREA),
		("SegGs", ctypes.c_int32),
		("SegFs", ctypes.c_int32),
		("SegEs", ctypes.c_int32),
		("SegDs", ctypes.c_int32),
		("Edi", ctypes.c_int32),
		("Esi", ctypes.c_int32),
		("Ebx", ctypes.c_int32),
		("Edx", ctypes.c_int32),
		("Ecx", ctypes.c_int32),
		("Eax", ctypes.c_int32),
		("Ebp", ctypes.c_int32),
		("Eip", ctypes.c_int32),
		("SegCs", ctypes.c_int32),
		("EFlags", ctypes.c_int32),
		("Esp", ctypes.c_int32),
		("SegSs", ctypes.c_int32),
		("ExtendedRegisters", ctypes.c_byte * 512)
	]


# Adapted from http://www.rohitab.com/discuss/topic/40579-dll-injection-via-thread-hijacking/
class ThreadExecutionHijack(cypy.Module):
	def __init__(self):
		super().__init__("Thread Execution Hijack",
                  ("threadhijack", "teh"), "Thread Execution Hijack DLL injection")

	def inject(self, handler: cypy.Cypyonate, target: str, payload: str, verbose: bool):
		is64 = cypy.is64bit()
		proc = cypy.get_process(target)
		if not proc:
			cypy.printe(f"Could not find process {target}")
			return
		
		if handler.reflective:
			cypy.printe("Reflective injection is not supported by this module")
			return

		if not proc:
			cypy.printe(f"Could not find process {target}")
			return

		payload = os.path.abspath(payload)

		# CreateToolhelp32Snapshot
		snapshot = ctypes.windll.kernel32.CreateToolhelp32Snapshot(
			TH32CS_SNAPTHREAD, int(proc))
		if snapshot == -1:
			cypy.printe("Could not create snapshot")
			return

		cypy.printv(f"Snapshot: {snapshot}")

		thread = THREADENTRY32()
		thread.dwSize = ctypes.sizeof(THREADENTRY32)
		if not ctypes.windll.kernel32.Thread32First(snapshot, ctypes.byref(thread)):
			cypy.printe("Could not get first thread")
			return

		while True:
			cypy.printv(f"Trying thread {thread.th32ThreadID}")
			if thread.th32OwnerProcessID == win32process.GetProcessId(proc):
				break

			if not ctypes.windll.kernel32.Thread32Next(snapshot, ctypes.byref(thread)):
				cypy.printe(f"Could not get next thread")
				return

		ctypes.windll.kernel32.CloseHandle(snapshot)

		# OpenThread
		thread = win32api.OpenThread(THREAD_ALL_ACCESS, False, thread.th32ThreadID)

		# Suspend thread
		win32process.SuspendThread(thread)

		cypy.printv("Thread suspended")

		if is64:
			ctx = CONTEXT64()
		else:
			ctx = CONTEXT32()

		ctx.ContextFlags = CONTEXT_FULL
		ctypes.windll.kernel32.GetThreadContext(int(thread), ctypes.byref(ctx))

		cypy.printv("Got thread context")

		buffer = SHELLCODE
		loadlibrarya = win32api.GetProcAddress(
			win32api.GetModuleHandle("kernel32.dll"), "LoadLibraryA")

		payload = payload.encode() + b"\x00"
		if is64:
			buffer += \
				b"\x50" +\
				b"\x48\xb8" + ctx.Rip.to_bytes(8, "little") + \
				b"\x48\x87\x04\x24" +\
				b"\xc3"

			# Align
			buffer += b"\x00\x00"
			buffer += payload

			saddr = buffer.find(b"\x48\x8D\x0d\x00\x00\x00\x00")
			if saddr != -1:
				# lea rcx, [rip + offset_to_payloadstr]
				buffer = buffer[:saddr+3] + (len(buffer) - len(payload) -
				                             saddr - 7).to_bytes(4, "little") + buffer[saddr+7:]

			lla = buffer.find(b"\x48\xb8\x00\x00\x00\x00\x00\x00\x00\x00")
			if lla != -1:
				# movabs rax, LoadLibraryA
				buffer = buffer[:lla+2] + \
					ctypes.c_uint64(loadlibrarya).value.to_bytes(
						8, "little") + buffer[lla+10:]
		else:
			buffer += b"\x00"
			buffer += payload

			lla = buffer.find(b"\xBB\x00\x00\x00\x00")
			if lla != -1:
				# mov ebx, LoadLibraryA
				buffer = buffer[:lla+1] + \
					ctypes.c_uint32(loadlibrarya).value.to_bytes(4, "little") + buffer[lla+5:]

			eip = buffer.find(b"\x68\x00\x00\x00\x00")
			if eip != -1:
				# push eip
				buffer = buffer[:eip+1] + ctx.Eip.to_bytes(4, "little") + buffer[eip+5:]

		cypy.printv("Generated shellcode")

		mem = win32process.VirtualAllocEx(
			proc, 0, len(buffer), win32con.MEM_COMMIT, win32con.PAGE_EXECUTE_READWRITE)

		if not is64:
			# Since lea is absolute, need to do this after allocating
			leaeax = buffer.find(b"\x8D\x05\x00\x00\x00\x00")
			if leaeax != -1:
				# lea eax, [payloadstr]
				buffer = buffer[:leaeax+2] + (mem + len(buffer) -
				                              len(payload)).to_bytes(4, "little") + buffer[leaeax+6:]

		win32process.WriteProcessMemory(proc, mem, buffer)

		cypy.printv(f"Wrote shellcode to {mem:X}")

		if is64:
			ctx.Rip = mem
		else:
			ctx.Eip = mem

		ctypes.windll.kernel32.SetThreadContext(int(thread), ctypes.byref(ctx))
		win32process.ResumeThread(thread)
		win32api.CloseHandle(thread)
		win32api.CloseHandle(proc)

		cypy.printc(f"Successfully injected into {target}")


ThreadExecutionHijack()

if cypy.is64bit():
	SHELLCODE = b"\x9C\x50\x51\x52\x53\x55\x56\x57\x41\x50\x41\x51\x41\x52\x41\x53\x41\x54\x41\x55\x41\x56"+\
	b"\x41\x57\x48\x83\xEC\x28\x48\x8d\x0d\x00\x00\x00\x00\x48\xB8\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xD0"+\
	b"\x48\x83\xC4\x28\x41\x5F\x41\x5E\x41\x5D\x41\x5C\x41\x5B\x41\x5A\x41\x59\x41\x58\x5F\x5E\x5D\x5B\x5A"+\
	b"\x59\x58\x9D\x50\x48\xB8\x37\x37\x37\x37\x37\x37\x37\x37\x48\x87\x04\x24\xC3"
	# Jmp to rip is dynamic
else:
	SHELLCODE = b"\x60\x9C\x8D\x05\x00\x00\x00\x00\x50\xBB\x00\x00\x00\x00\xFF\xD3\x9D\x61\x68\x00\x00\x00\x00\xC3"
