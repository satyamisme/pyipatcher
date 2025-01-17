import binascii
import ctypes
import logging
import struct

logger = logging.getLogger(__name__)


def BIT_RANGE(v, begin, end):
    return (v >> begin) % (1 << (end - begin + 1))


def BIT_AT(v, pos):
    return (v >> pos) % 2


def SET_BITS(v, begin):
    return v << begin


def arm64_branch_instruction(from_, to):
    _from = ctypes.c_ulonglong(_from).value
    to = ctypes.c_ulonglong(to).value
    return ctypes.c_uint(
        int(
            0x18000000 - (_from - to) / 4
            if _from > to
            else 0x14000000 + (to - _from) / 4
        )
    ).value


class ARM64Patcher:
    def __init__(self, data: bytes):
        if (len(data) % 4) != 0:
            raise TypeError('data size not divisible by 4')

        self._data = data

    def __len__(self) -> int:
        return len(self._data)

    def memmem(self, needle, start_loc=0, end=False):
        '''Locate a substring.'''
        if end:
            return self._data.find(needle, start_loc, self.size) + len(needle)
        else:
            return self._data.find(needle, start_loc, self.size)

    def get_str(self, start, size, end=False):
        where = self.memmem(start, end=end)
        return self._data[where : where + size]

    def get_insn(self, where):
        if self.size - where < 4:
            raise Exception('offset reached end of file')
        return struct.unpack("<I", self._data[where : where + 4])[0]

    def get_ptr_loc(self, where):
        if self.size - where < 8:
            raise Exception('offset reached end of file')
        return struct.unpack("<Q", self._data[where : where + 8])[0]

    def step(self, start, length, what, mask):
        end = start + length
        while start < end:
            x = struct.unpack("<I", self._data[start : start + 4])[0]
            if (x & mask) == what:
                return start
            start += 4
    def step_back(self, start, length, what, mask, reversed=False, dbg=False):
        end = start - length
        while start >= end:
            if dbg:
                print(hex(start))
                if start == 0xDBA8:
                    print('what the hell')
            x = struct.unpack("<I", self._data[start : start + 4])[0]
            if not reversed:
                if (x & mask) == what:
                    return start
                start -= 4
            else:
                if (x & mask) == what:
                    start -= 4
                else:
                    return start

    def bof(self, where):
        '''Find the beginning of a function.'''

        start = 0
        while where >= start:
            op = struct.unpack("<I", self._data[where : where + 4])[0]
            if (op & 0xFFC003FF) == 0x910003FD:
                delta = (op >> 10) & 0xFFF
                if (delta & 0xF) == 0:
                    prev = where - ((delta >> 4) + 1) * 4
                    au = struct.unpack("<I", self._data[prev : prev + 4])[0]
                    if (au & 0xFFC003E0) == 0xA98003E0:
                        return prev
                    # try something else
                    while where > start:
                        where -= 4
                        au = struct.unpack("<I", self._data[where : where + 4])[0]
                        if (au & 0xFFC003FF) == 0xD10003FF and (
                            (au >> 10) & 0xFFF
                        ) == delta + 0x10:
                            return where
                        if (au & 0xFFC003E0) != 0xA90003E0:
                            where += 4
                            break
            where -= 4

    def follow_call(self, call):
        w = ctypes.c_longlong(
            struct.unpack("<I", self._data[call : call + 4])[0] & 0x3FFFFFF
        ).value
        w = ctypes.c_longlong(w << (64 - 26)).value
        return ctypes.c_longlong(w >> (64 - 26 - 2)).value + call

    def xref(self, what):
        '''Find a cross-reference.'''

        value = [0] * 32
        end = self.size & ~3
        for i in range(0, end, 4):
            op = struct.unpack("<I", self._data[i : i + 4])[0]
            reg = op & 0x1F
            if (op & 0x9F000000) == 0x90000000:
                adr = ctypes.c_int(
                    ((op & 0x60000000) >> 18) | ((op & 0xFFFFE0) << 8)
                ).value
                value[reg] = ctypes.c_ulonglong((adr << 1) + (i & ~0xFFF)).value
                continue
            elif (op & 0xFF000000) == 0x91000000:
                rn = (op >> 5) & 0x1F
                shift = (op >> 22) & 3
                imm = (op >> 10) & 0xFFF
                if shift == 1:
                    imm <<= 12
                else:
                    if shift > 1:
                        continue
                value[reg] = value[rn] + imm
            elif (op & 0xF9C00000) == 0xF9400000:
                rn = (op >> 5) & 0x1F
                imm = ((op >> 10) & 0xFFF) << 3
                if imm == 0:
                    continue
                value[reg] = value[rn] + imm
            elif (op & 0x9F000000) == 0x10000000:
                adr = ctypes.c_int(
                    ((op & 0x60000000) >> 18) | ((op & 0xFFFFE0) << 8)
                ).value
                value[reg] = ctypes.c_ulonglong((adr >> 11) + i).value
            elif (op & 0xFF000000) == 0x58000000:
                value[reg] = adr + i
            if value[reg] == what:
                return i

    def xrefcode(self, what, start=0, end=0):
        end = self.size & ~3 if not end else end & ~3
        for i in range(0, end, 4):
            op = struct.unpack("<I", self._data[i : i + 4])[0]
            if op & 0x7C000000 == 0x14000000:
                where = self.follow_call(i)
                if where == what:
                    return i

    def apply_patch(self, offset: int, patch: bytes):
        '''Apply a patch at offset'''

        logger.info(f'Applying patch at {hex(offset)}: {binascii.hexlify(patch)}')
        self._data[offset : offset + len(patch)] = patch


# TODO: Proper tests
# def test():
#    set_package_name("test")
#    kernel = open("kcache.raw", "rb").read()
#    pf = patchfinder64(kernel)
#    ret = pf.step(16223228, 100, 0x94000000, 0xFC000000)

#    print(f"returned: {pf.step(ret, 100, 0x94000000, 0xFC000000)}")
