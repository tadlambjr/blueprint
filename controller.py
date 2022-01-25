import re
import logging

class Controller:
    """A Controller class"""

    request_matching_re = re.compile(r'^\@RequestMapping\(\"(.*)\"\)')
    authentication_re = re.compile(r'^\@PreAuthorize\(\"isAuthenticated\(\)\"\)')
    authentication_missing = True

    method_request_re = re.compile(r'\s+\@RequestMapping\(\"(.*)\"\)')
    method_re = re.compile(r'\s+public.*\(')
    method_auth_re = re.compile(r'^\s+\@PreAuthorize\(\"isAuthenticated')

    get_matching_def_re    = re.compile(r'\s+\@GetMapping[^\(]')
    post_matching_def_re   = re.compile(r'\s+\@PostMapping$[^\(]')
    delete_matching_def_re = re.compile(r'\s+\@DeleteMapping$[^\(]')

    get_matching_val_re   = re.compile(r'\s+\@GetMapping\(value\s*=\s*\"(.*?)\".*\)')
    get_matching_path_re  = re.compile(r'\s+\@GetMapping\(path\s*=\s*\"(.*?)\".*\)')
    get_matching_re       = re.compile(r'\s+\@GetMapping\(\"(.*)\"\)')
    post_matching_re      = re.compile(r'\s+\@PostMapping\(\"(.*)\"\)')
    post_matching_val_re  = re.compile(r'\s+\@PostMapping\(value\s*=\s*\"(.*?)\".*\)')
    post_matching_path_re = re.compile(r'\s+\@PostMapping\(path\s*=\s*\"(.*?)\".*\)')
    put_matching_re       = re.compile(r'\s+\@PutMapping\(\"(.*)\"\)')
    patch_matching_re     = re.compile(r'\s+\@PatchMapping\(\"(.*)\"\)')
    delete_matching_re    = re.compile(r'\s+\@DeleteMapping\(\"(.*)\"\)')
    delete_matching_path_re = re.compile(r'\s+\@DeleteMapping\(path\s*=\s*\"(.*?)\"\)')

    def __init__(self, filename):
        self._filename = filename
        self._class_name = re.match(r'^.*\/(.*)\.java', filename).group(1)
        self.mapping_root = ''
        self.mappings = []
        self.parse_file()
        logging.info(self)
    
    def add_match(self, line, regex, rest_type):
        match = regex.match(line)
        if match:
            secured = u'\U0001F512 ' if self.method_auth else ''
            self.mappings.append(f'{secured}{rest_type} {self.mapping_root}{match.group(1)}')
            self.method_auth = False

    def complete_mapping(self):
        if self.rest_type:
            secured = u'\U0001F512 ' if self.method_auth else ''
            current_mapping = self.current_mapping if self.current_mapping else ''
            self.mappings.append(f'{secured}{self.rest_type} {self.mapping_root}{current_mapping}')
        self.rest_type = None
        self.current_mapping = None
        self.method_auth = False

    def store_match(self, line, regex, rest_type):
        match = regex.match(line)
        if match:
            self.rest_type = rest_type

    def parse_file(self):
        self.rest_type = None
        self.current_mapping = None
        self.method_auth = False

        lines = open(self._filename).readlines()
        for line in lines:
            match = self.authentication_re.match(line)
            if match:
                self.authentication_missing = False

            match = self.request_matching_re.match(line)
            if match:
                self.mapping_root = match.group(1)

            match = self.method_auth_re.match(line)
            if match:
                self.method_auth = True

            self.add_match(line, self.get_matching_re, 'GET')
            self.add_match(line, self.get_matching_val_re, 'GET')
            self.add_match(line, self.get_matching_path_re, 'GET')
            self.add_match(line, self.post_matching_re, 'POST')
            self.add_match(line, self.post_matching_val_re, 'POST')
            self.add_match(line, self.post_matching_path_re, 'POST')
            self.add_match(line, self.put_matching_re, 'PUT')
            self.add_match(line, self.patch_matching_re, 'PATCH')
            self.add_match(line, self.delete_matching_re, 'DELETE')
            self.add_match(line, self.delete_matching_path_re, 'DELETE')

            self.store_match(line, self.get_matching_def_re, 'GET')
            self.store_match(line, self.post_matching_def_re, 'POST')
            self.store_match(line, self.delete_matching_def_re, 'DELETE')

            match = self.method_request_re.match(line)
            if match:
                self.current_mapping = match.group(1)

            match = self.method_re.match(line)
            if match:
                self.complete_mapping()


    def get_filename(self):
        return self._filename

    def node_string(self):
        mappings = "\l".join(self.mappings)
        secured = '  ' if self.authentication_missing else u'\U0001F512 '
        return f'{secured}{self._class_name}\l{mappings}'

    def __str__(self):
        mappings = "\n\t\t ".join(self.mappings)
        secured = '  ' if self.authentication_missing else u'\U0001F512 '
        return f'\n\t  {secured}{self._class_name}\n\t\t {mappings}'
