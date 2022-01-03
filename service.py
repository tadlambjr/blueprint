import re
import logging

class Service:

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
            x = 1

    def get_filename(self):
        return self._filename

    def __str__(self):
        return f'\t  {self._class_name}'
