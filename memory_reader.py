import ctypes
import struct
import psutil
from ctypes import wintypes

PROCESS_VM_READ = 0x0010
PROCESS_QUERY_INFORMATION = 0x0400

kernel32 = ctypes.windll.kernel32
kernel32.ReadProcessMemory.argtypes = [
    wintypes.HANDLE,
    wintypes.LPCVOID,
    wintypes.LPVOID,
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_size_t)
]
kernel32.ReadProcessMemory.restype = wintypes.BOOL

class MemoryReader:
    PROCESS_NAME = "BNSR.exe"
    COMBAT_LOG_LENGTH = 600
    OFFSETS = [0x7485118, 0xA0, 0x670, 0x8]
    POINTER_CHAIN_VALIDITY = 5  # seconds before revalidating pointer chain

    def __init__(self):
        self.pid = self.get_process_id(self.PROCESS_NAME)
        if self.pid is None:
            raise Exception(f"Process {self.PROCESS_NAME} not found.")
        self.process_handle = self.open_process(self.pid)
        self.base_module_address = self.get_base_address(self.pid)
        if not self.base_module_address:
            raise Exception("Failed to get base module address.")
        print(f"[DEBUG] Base module address: 0x{self.base_module_address:016X}")

        # Initialize caching for the pointer chain
        self.cached_chat_address = None
        self.last_chain_validation = 0

    def get_process_id(self, process_name):
        for proc in psutil.process_iter(attrs=["pid", "name"]):
            try:
                if proc.info["name"].lower() == process_name.lower():
                    print(f"[DEBUG] Found process {process_name} with PID {proc.info['pid']}")
                    return proc.info["pid"]
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None

    def open_process(self, pid):
        handle = kernel32.OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, pid)
        if not handle:
            raise Exception(f"Failed to open process {pid}.")
        return handle

    def get_base_address(self, pid):
        hProcess = self.open_process(pid)
        psapi = ctypes.WinDLL("psapi.dll")
        module_array = (ctypes.c_void_p * 1024)()
        cb = ctypes.sizeof(module_array)
        needed = ctypes.c_ulong()
        if not psapi.EnumProcessModules(hProcess, ctypes.byref(module_array), cb, ctypes.byref(needed)):
            kernel32.CloseHandle(hProcess)
            return None
        base_addr = module_array[0]
        kernel32.CloseHandle(hProcess)
        return base_addr

    def read_memory(self, address, size):
        buffer = ctypes.create_string_buffer(size)
        bytesRead = ctypes.c_size_t(0)
        if not kernel32.ReadProcessMemory(self.process_handle, ctypes.c_void_p(address),
                                          buffer, size, ctypes.byref(bytesRead)):
            return None
        if bytesRead.value != size:
            return None
        return buffer.raw

    def read_pointer(self, base_address, offset):
        addr = base_address + offset
        data = self.read_memory(addr, 8)
        if data is None:
            raise Exception(f"Failed to read memory at 0x{addr:016X}")
        pointer = struct.unpack("Q", data)[0]
        hex_pointer = f"0x{pointer:016X}"
        if not hex_pointer.startswith("0x0000"):
            print(f"[DEBUG] Read pointer at offset 0x{offset:X}: {hex_pointer}")
        return pointer


    def resolve_pointer_chain(self):
        current_address = self.base_module_address
        for i, offset in enumerate(self.OFFSETS[:-1]):
            try:
                current_address = self.read_pointer(current_address, offset)
                if current_address == 0:
                    print(f"[DEBUG] Null pointer encountered at index {i} (offset: 0x{offset:X}).")
                    raise Exception(f"Null pointer encountered at offset index {i}")
                else:
                    print(f"[DEBUG] Pointer at index {i} (offset: 0x{offset:X}): 0x{current_address:016X}")
            except Exception as e:
                print(f"[DEBUG] Exception at pointer index {i} (offset: 0x{offset:X}): {e}")
                raise
        return current_address


    def get_cached_chat_address(self):
        import time
        # Revalidate if the cached address is too old or not set
        if (time.time() - self.last_chain_validation > self.POINTER_CHAIN_VALIDITY or
                self.cached_chat_address is None):
            try:
                self.cached_chat_address = self.resolve_pointer_chain()
                self.last_chain_validation = time.time()
                print(f"[DEBUG] Updated cached combat log base address: 0x{self.cached_chat_address:016X}")
            except Exception as e:
                raise Exception("Failed to revalidate pointer chain: " + str(e))
        return self.cached_chat_address

    def get_combat_chat_log(self):
        lines = []
        try:
            base_chat_address = self.get_cached_chat_address()
            print(f"[DEBUG] Using combat log base address: 0x{base_chat_address:016X}")
            entry_stride = self.OFFSETS[-1]
            for i in range(self.COMBAT_LOG_LENGTH):
                try:
                    log_entry_ptr = self.read_pointer(base_chat_address, i * entry_stride)
                    if log_entry_ptr != 0:
                        raw = self.read_memory(log_entry_ptr, 512)
                        if raw:
                            line = self.read_string(raw, 512)
                            period_index = line.find('.')
                            if period_index != -1:
                                line = line[:period_index + 1]
                            lines.append(line)
                        else:
                            lines.append("")
                    else:
                        lines.append("")
                except Exception as e:
                    print(f"[DEBUG] Error reading entry {i}: {e}")
                    lines.append("")
        except Exception as ex:
            raise Exception("Error reading combat chat log: " + str(ex))
        return lines



    def read_string(self, data, size):
        terminator = data.find(b'\x00\x00')
        if terminator != -1:
            data = data[:terminator]
        try:
            return data.decode("utf-16le", errors="ignore")
        except Exception:
            return ""


