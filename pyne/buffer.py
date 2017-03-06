

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
        self.buffer_size_bytes = buffer_size * word_size
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
        data = self._convert_word_sequence(header[:8])
        words, buffer_type, _, run_number = data
        buffer_number = self._convert_int(header[8:12])
        events = self._convert_int(header[12:14])
        return Header(words, Type(buffer_type),
                      run_number, buffer_number, events)

    def convert_run(self, buffer):
        title = buffer[:80].decode('utf-8').replace('\x00', '')
        date = self._convert_word_sequence(buffer[84:96])
        month, day, year, hour, minute, second = date
        date = datetime(year + 1900, month + 1, day, hour, minute, second)
        return Run(title, date)

    def process_all_events(self, buffer, number_events):
        events = []
        for _ in range(number_events):
            length = (self._convert_int(buffer[:2]) + 1) * self.word_size
            event, buffer = buffer[2:length], buffer[length:]
            events.append(self.convert_single_event(event))
        return events

    def convert_single_event(self, buffer):
        if not buffer.startswith(boundary):
            count = int(self._decode_bytes(buffer[:4])[2:4], 16)
            if count != 0:
                temp_value = self._decode_bytes(buffer[4:8])
                channel = int(temp_value[4:6], 16)
                valid_bit = ValidBit(int(temp_value[2]))
                value = '{}{}'.format(temp_value[2:4], temp_value[:2])[1:]
                value = int(value, 16)
                return Event(count, channel, value,
                             valid_bit == ValidBit.OVERFLOW,
                             valid_bit == ValidBit.UNDERFLOW,
                             valid_bit == ValidBit.VALID)
            return count

    def _convert_word_sequence(self, buffer):
        buffer = [buffer[i:i + self.word_size]
                  for i in range(0, len(buffer), self.word_size)]
        return list(map(self._convert_int, buffer))

    def _convert_int(self, b):
        return int.from_bytes(b, byteorder=sys.byteorder)

    def _decode_bytes(self, b):
        return hexlify(b).decode('utf-8')
