

from binascii import hexlify
from collections import namedtuple
from datetime import datetime
from enum import Enum
import sys

Header = namedtuple('header', 'words type run buffer events')
Run = namedtuple('run', 'title date')
Event = namedtuple('event', 'count channel value overflow underflow valid')

boundary = b'\xff\xff\xff\xff'


class Type(Enum):
    HEADER = 11
    DATA = 1
    FOOTER = 12


class ValidBit(Enum):
    VALID = 4
    UNDERFLOW = 2
    OVERFLOW = 1


class Buffer:
    def __init__(self, filename, *,
                 buffer_size=13328, header_size=16, word_size=2):
        self.filename = filename
        self.buffer_size = buffer_size
        self.buffer_size_bytes = buffer_size * word_size
        self.header_size = header_size
        self.header_size_bytes = header_size * word_size
        self.word_size = word_size

    def __enter__(self):
        self.f = open(self.filename, 'rb')
        return self

    def __exit__(self, *args):
        self.f.close()

    def process_buffer(self):
        desc, data = self.read_buffer()
        if Type(desc.type) == Type.HEADER:
            info = self.convert_run(data)
        elif Type(desc.type) == Type.DATA:
            info = self.process_all_events(data, desc.events)
        elif Type(desc.type) == Type.FOOTER:
            info = self.convert_run(data)
            self.__exit__(None, None, None)
        else:
            info = 0
        return desc, info

    def read_buffer(self):
        buffer = self.f.read(self.buffer_size_bytes)
        desc = self.convert_header(buffer)
        data = buffer[self.header_size_bytes:desc.words * self.word_size]
        return desc, data

    def convert_header(self, buffer):
        header = buffer[:self.header_size_bytes]
        words = int.from_bytes(header[:2], byteorder=sys.byteorder)
        buffer_type = int.from_bytes(header[2:4], byteorder=sys.byteorder)
        run_number = int.from_bytes(header[6:8], byteorder=sys.byteorder)
        buffer_number = int.from_bytes(header[8:12], byteorder=sys.byteorder)
        events = int.from_bytes(header[12:14], byteorder=sys.byteorder)
        return Header(words, buffer_type, run_number, buffer_number, events)

    def convert_run(self, buffer):
        title = buffer[:80].decode('utf-8').replace('\x00', '')
        date = buffer[84:]
        month = int.from_bytes(date[:2], byteorder=sys.byteorder) + 1
        day = int.from_bytes(date[2:4], byteorder=sys.byteorder)
        year = int.from_bytes(date[4:6], byteorder=sys.byteorder) + 1900
        hour = int.from_bytes(date[6:8], byteorder=sys.byteorder)
        minute = int.from_bytes(date[8:10], byteorder=sys.byteorder)
        second = int.from_bytes(date[10:12], byteorder=sys.byteorder)
        date = datetime(year, month, day, hour, minute, second)
        return Run(title, date)

    def process_all_events(self, buffer, number_events):
        events = buffer.split(boundary)[::2][:number_events]
        print(len(events), number_events)
        return [self.convert_single_event(e) for e in events]

    def convert_single_event(self, buffer):
        count = int(hexlify(buffer[2:6]).decode('utf-8')[2:4], 16)
        if count != 0:
            temp_value = hexlify(buffer[6:10]).decode('utf-8')
            channel = int(temp_value[4:6], 16)
            valid_bit = int(temp_value[2])
            value = int('{}{}'.format(temp_value[2:4], temp_value[:2])[1:], 16)
            return Event(count, channel, value,
                         ValidBit(valid_bit) == ValidBit.OVERFLOW,
                         ValidBit(valid_bit) == ValidBit.UNDERFLOW,
                         ValidBit(valid_bit) == ValidBit.VALID)
        return count
