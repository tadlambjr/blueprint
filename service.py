import re
import logging

class Service:

    get_re    = re.compile(r'.*getForObject\((.*)\)')
    post_re   = re.compile(r'.*postForObject\((.*)\)')

    def __init__(self, filename):
        self._filename = filename
        self._class_name = re.match(r'^.*\/(.*)\.java', filename).group(1)
        self.mapping_root = ''
        self.mappings = []
        self.parse_file()
        logging.info(self)

    def parse_file(self):
        self.rest_type = None
        self.current_mapping = None
        self.method_auth = False

        lines = open(self._filename).readlines()
        for line in lines:
            match = self.get_re.match(line)
            if match:
                logging.info(f'{self._class_name} GET {match.group(1)}')

            match = self.post_re.match(line)
            if match:
                logging.info(f'{self._class_name} POST {match.group(1)}')


    def get_filename(self):
        return self._filename

    def __str__(self):
        return f'\t  {self._class_name}'
