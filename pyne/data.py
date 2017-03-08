''' data.py -- holds processed data

    Data creates a pyne.Buffer for the given filename and extracts the
    information from it. It stores the run information and, if requested,
    converts the data event stream into useful units.
'''


from . import buffer
from . import detector


class Data:
    def __init__(self, filename):
        self.buffer = buffer.Buffer(filename)
        self.run_information = {}
        self.adc = detector.DetectorArray(32, 4096)
        self.events = {'valid': 0, 'overflow': 0, 'underflow': 0}

    def read_buffer(self):
        with self.buffer as b:
            desc, info = b.process_buffer()
            self._get_start_information(desc, info)
            desc, info = b.process_buffer()
            while desc.type != buffer.Type.FOOTER:
                self._get_events(desc, info)
                desc, info = b.process_buffer()
            self._get_end_information(desc, info)
        self.adc.convert_detectors()

    def _get_start_information(self, desc, info):
        self.run_information['run_number'] = desc.run
        self.run_information['title'] = info.title
        self.run_information['start_time'] = info.date

    def _get_end_information(self, desc, info):
        assert self.run_information['run_number'] == desc.run
        assert self.run_information['title'] == info.title
        self.run_information['end_time'] = info.date
        start, end = (self.run_information['start_time'],
                      self.run_information['end_time'])
        self.run_information['run_time'] = (end - start).seconds

    def _get_events(self, desc, info):
        assert desc.events == len(info)
        for event in info:
            if event is not None and event != 0:
                self.events['valid'] += event.valid
                self.events['underflow'] += event.underflow
                self.events['overflow'] += event.overflow
                if event.valid:
                    self.adc.add_event(event.channel, event.value)
