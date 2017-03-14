

from binascii import hexlify
from collections import namedtuple
from datetime import datetime, timedelta
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
        desc, data = self.read_buffer()
        if desc.type == self.Type.HEADER:
            info = self.convert_header(data)
        elif desc.type == self.Type.DATA:
            info = self.process_all_events(data, desc.events)
        elif desc.type == self.Type.FOOTER:
            info = self.convert_footer(data)
            self.__exit__(None, None, None)
        else:
            info = 0
        return desc, info

    def read_buffer(self):
        raise NotImplementedError

    def convert_header(self, buffer):
        raise NotImplementedError

    def process_all_events(self, buffer, number_events):
        raise NotImplementedError

    def convert_footer(self, buffer):
        raise NotImplementedError

    def _convert_word_sequence(self, buffer, converter):
        buffer = [buffer[i:i + self.word_size]
                  for i in range(0, len(buffer), self.word_size)]
        return list(map(converter, buffer))

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

    def read_buffer(self):
        buffer = self.f.read(self.buffer_size_bytes)
        desc = self._convert_buffer_header(buffer)
        data = buffer[self.header_size_bytes:desc.words * self.word_size]
        return desc, data

    def _convert_buffer_header(self, buffer):
        header = buffer[:self.header_size_bytes]
        data = self._convert_word_sequence(header[:8], self._convert_int)
        words, buffer_type, _, run_number = data
        buffer_number = self._convert_int(header[8:12])
        events = self._convert_int(header[12:14])
        return Header(words, self.Type(buffer_type),
                      run_number, buffer_number, events)

    def convert_header(self, buffer):
        title = buffer[:80].decode('utf-8').replace('\x00', '')
        date = self._convert_word_sequence(buffer[84:96], self._convert_int)
        month, day, year, hour, minute, second = date
        date = datetime(year + 1900, month + 1, day, hour, minute, second)
        return Run(title, date)

    def process_all_events(self, buffer, number_events):
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

    def convert_footer(self, buffer):
        return self.convert_header(buffer)


class CHN_Buffer(Buffer):
    def __init__(self, filename):
        super().__init__(filename, buffer_size=16)
        self.Type = IntEnum('Type',
                            {'DATA': 0, 'HEADER': -1, 'FOOTER': -102})
        self.current_channel = 0
        self.number_channels = 0

    def read_buffer(self):
        buffer = self.f.read(self.buffer_size_bytes)
        buffer_type = self._check_buffer_type(buffer[:self.word_size])
        return Header(0, self.Type(buffer_type), 0, 0, 8), buffer

    def _check_buffer_type(self, b):
        value = self._convert_int(b) ^ ~0xFFFF
        try:
            return self.Type(value)
        except ValueError:
            return self.Type.DATA

    def convert_header(self, buffer):
        title = self.filename[:-4]
        self.number_channels = self._convert_int(buffer[14:])
        self._start_date = self._create_date(buffer)
        self._save_runtime(buffer[8:12])
        return Run(title, self._start_date)

    def _create_date(self, buffer):
        second = buffer[6:8].decode('utf-8')
        date = (buffer[16:23] + buffer[24:28]).decode('utf-8')
        return datetime.strptime('{}{}'.format(second, date), '%S%d%b%y%H%M')

    def _save_runtime(self, time_buffer):
        temp = self._decode_bytes(time_buffer)
        temp = '{}{}{}{}'.format(temp[6:8], temp[4:6], temp[2:4], temp[:2])
        temp = int(temp, 16) / 50  # time was clicks of a 50 Hz clock
        self._run_time = timedelta(seconds=temp)

    def process_all_events(self, buffer, number_events):
        return [0, 0, 0, 0, 0, 0, 0, 0]

    def convert_footer(self, buffer):
        title = self.filename[:-4]
        end_time = self._start_date + self._run_time
        return Run(title, end_time)
