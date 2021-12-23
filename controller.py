import re
import logging

class Controller:
    """A Controller class"""

    authentication_re = re.compile(r'^\@PreAuthorize\(\"isAuthenticated\(\)\"\)')
    authentication_missing = True

    request_matching_re = re.compile(r'^\@RequestMapping\(\"(.*)\"\)')

    get_matching_def_re   = re.compile(r'\s+\@GetMapping\(\"(.*)\"\)')

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
            self.mappings.append(f'{rest_type} {self.mapping_root}{match.group(1)}')            

    def parse_file(self):
        in_class = False
        lines = open(self._filename).readlines()
        for line in lines:
            if line.startswith('public class'):
                in_class = True

            match = self.authentication_re.match(line)
            if match:
                self.authentication_missing = False

            match = self.request_matching_re.match(line)
            if match:
                self.mapping_root = match.group(1)

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

    def get_filename(self):
        return self._filename

    def __str__(self):
        mappings = "\n\t    ".join(self.mappings)
        secured = '  ' if self.authentication_missing else u'\U0001F512 '
        return f'\n\t{secured}{self._class_name}\n\t    {mappings}'
