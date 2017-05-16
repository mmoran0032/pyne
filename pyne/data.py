

from . import buffer
from . import detector
from . import file

date_format = '%Y-%m-%dT%H:%M:%S'


class Data:
    def __init__(self, data_file, buffer_file):
        self.buffer_file = buffer_file
        self.data_file = data_file
        self.run_information = {}
        self.f = file.File(self.data_file)

    def load_data(self):
        if self.f:
            self.read_data()
        else:
            print('reading from buffer...this may take some time')
            self.read_buffer()
            self.convert_data()

    def read_data(self):
        raise NotImplementedError

    def save_data(self):
        raise NotImplementedError

    def read_buffer(self):
        with self.buffer(self.buffer_file) as b:
            desc, info = b.process_buffer()
            self._get_start_information(desc, info)
            desc, info = b.process_buffer()
            while desc.type != b.Type.FOOTER:
                self._get_events(desc, info)
                desc, info = b.process_buffer()
            self._get_end_information(desc, info)

    def _get_start_information(self, desc, info):
        self.run_information['run_number'] = desc.run
        self.run_information['title'] = info.title
        self.run_information['start_time'] = info.date

    def _get_end_information(self, desc, info):
        assert self.run_information['run_number'] == desc.run
        assert self.run_information['title'] == info.title
        self.run_information['end_time'] = info.date

    def _get_events(self, desc, info):
        assert desc.events == len(info)
        for event in info:
            if event is not None and event != 0 and event.valid:
                self.adc.add_event(event.channel, event.value)

    def convert_data(self):
        self.adc.convert_detector()
        start, end = (self.run_information['start_time'],
                      self.run_information['end_time'])
        self.run_information['run_time'] = (end - start).seconds
        self.run_information['start_time'] = start.strftime(date_format)
        self.run_information['end_time'] = end.strftime(date_format)


class EVTData(Data):
    def __init__(self, data_file, buffer_file=None):
        super().__init__(data_file, buffer_file)
        self.adc = detector.DetectorArray(32, 4096)
        self.buffer = buffer.EVT_Buffer

    def read_data(self):
        print('reading from {}...'.format(self.data_file))
        self.run_information = self.f.read_attributes()
        for adc in self.adc:
            adc.bins, adc.counts, adc.energies = self.f.read_adc(adc.name)

    def save_data(self):
        print(f'writing to {self.data_file}...')
        self.f.save_attributes(self.run_information)
        for adc in self.adc:
            self.f.save_adc(adc.name, adc.bins, adc.counts, adc.energies)


class CHNData(Data):
    def __init__(self, data_file, buffer_file=None):
        super().__init__(data_file, buffer_file)
        self.adc = detector.Detector(channels=2048, binned=True)
        self.buffer = buffer.CHN_Buffer

    def read_data(self):
        print(f'reading from {self.data_file}...')
        self.run_information = self.f.read_attributes()
        adc = self.adc
        adc.bins, adc.counts, adc.energies = self.f.read_adc('adc')

    def save_data(self):
        print(f'writing to {self.data_file}...')
        self.f.save_attributes(self.run_information)
        adc = self.adc
        self.f.save_adc(adc.name, adc.bins, adc.counts, adc.energies)
