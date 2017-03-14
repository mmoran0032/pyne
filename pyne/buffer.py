

from binascii import hexlify
from collections import namedtuple
from datetime import datetime
from enum import IntEnum
import sys

Header = namedtuple('header', 'words type run buffer events')
Run = namedtuple('run', 'title date')
Event = namedtuple('event', 'count channel value overflow underflow valid')


class Buffer:
    def __init__(self, filename, *,
                 buffer_size=0, header_size=0, word_size=2):
        self.filename = filename
        self.buffer_size_bytes = buffer_size * word_size
        self.header_size_bytes = header_size * word_size
        self.word_size = word_size
        self.Type = None
        self.ValidBit = None

    def __enter__(self):
        self.f = open(self.filename, 'rb')
        return self

    def __exit__(self, *args):
        self.f.close()

    def process_buffer(self):
        raise NotImplementedError

    def _convert_word_sequence(self, buffer):
        buffer = [buffer[i:i + self.word_size]
                  for i in range(0, len(buffer), self.word_size)]
        return list(map(self._convert_int, buffer))

    def _convert_int(self, b):
        return int.from_bytes(b, byteorder=sys.byteorder)

    def _decode_bytes(self, b):
        return hexlify(b).decode('utf-8')


class EVT_Buffer(Buffer):
    def __init__(self, filename):
        super().__init__(filename, buffer_size=13328, header_size=16)
        self.Type = IntEnum('Type',
                            {'DATA': 1, 'HEADER': 11, 'FOOTER': 12})
        self.ValidBit = IntEnum('VALID',
                                {'VALID': 4, 'UNDERFLOW': 2, 'OVERFLOW': 1})
        self.boundary = b'\xff\xff\xff\xff'

    def process_buffer(self):
        desc, data = self._read_buffer()
        if desc.type == self.Type.HEADER:
            info = self._convert_run(data)
        elif desc.type == self.Type.DATA:
            info = self._process_all_events(data, desc.events)
        elif desc.type == self.Type.FOOTER:
            info = self._convert_run(data)
            self.__exit__(None, None, None)
        else:
            info = 0
        return desc, info

    def _read_buffer(self):
        buffer = self.f.read(self.buffer_size_bytes)
        desc = self._convert_header(buffer)
        data = buffer[self.header_size_bytes:desc.words * self.word_size]
        return desc, data

    def _convert_header(self, buffer):
        header = buffer[:self.header_size_bytes]
        data = self._convert_word_sequence(header[:8])
        words, buffer_type, _, run_number = data
        buffer_number = self._convert_int(header[8:12])
        events = self._convert_int(header[12:14])
        return Header(words, self.Type(buffer_type),
                      run_number, buffer_number, events)

    def _convert_run(self, buffer):
        title = buffer[:80].decode('utf-8').replace('\x00', '')
        date = self._convert_word_sequence(buffer[84:96])
        month, day, year, hour, minute, second = date
        date = datetime(year + 1900, month + 1, day, hour, minute, second)
        return Run(title, date)

    def _process_all_events(self, buffer, number_events):
        events = []
        for _ in range(number_events):
            length = (self._convert_int(buffer[:2]) + 1) * self.word_size
            event, buffer = buffer[2:length], buffer[length:]
            events.append(self._convert_single_event(event))
        return events

    def _convert_single_event(self, buffer):
        if not buffer.startswith(self.boundary):
            count = int(self._decode_bytes(buffer[:4])[2:4], 16)
            if count != 0:
                temp_value = self._decode_bytes(buffer[4:8])
                channel = int(temp_value[4:6], 16)
                valid_bit = self.ValidBit(int(temp_value[2]))
                value = '{}{}'.format(temp_value[2:4], temp_value[:2])[1:]
                value = int(value, 16)
                return Event(count, channel, value,
                             valid_bit == self.ValidBit.OVERFLOW,
                             valid_bit == self.ValidBit.UNDERFLOW,
                             valid_bit == self.ValidBit.VALID)
            return count


class CHN_Buffer(Buffer):
    def __init__(self, filename):
        super().__init__(filename, buffer_size=16, header_size=0)
        self.Type = IntEnum('Type',
                            {'DATA': 0, 'HEADER': 65535, 'FOOTER': 65434})

    def process_buffer(self):
        type, data = self._read_buffer()
        if type == self.Type.HEADER:
            info = self.convert_run(data)
        elif type == self.Type.DATA:
            info = self.process_all_events(data)
        elif type == self.Type.FOOTER:
            info = self.convert_run(data)
            self.__exit__(None, None, None)
        else:
            info = 0
        return info

    def _read_buffer(self):
        buffer = self.f.read(self.buffer_size_bytes)
        type = self._check_buffer_type(buffer[:2 * self.word_size])
        return type, buffer

    def _check_buffer_type(self, b):
        value = self._convert_int(b)
        try:
            return self.Type(value)
        except ValueError:
            return self.Type.DATA
