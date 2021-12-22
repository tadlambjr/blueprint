import re

class Controller:
    """A Controller class"""

    authentication_re = re.compile(r'^\@PreAuthorize\(\"isAuthenticated\(\)\"\)')
    authentication_missing = True

    request_matching_re = re.compile(r'^\@RequestMapping\(\"(.*)\"\)')
    mapping_root = ''

    get_matching_re    = re.compile(r'\s+\@GetMapping\(\"(.*)\"\)')
    post_matching_re   = re.compile(r'\s+\@PostMapping\(\"(.*)\"\)')
    put_matching_re    = re.compile(r'\s+\@PutMapping\(\"(.*)\"\)')
    patch_matching_re  = re.compile(r'\s+\@PatchMapping\(\"(.*)\"\)')
    delete_matching_re = re.compile(r'\s+\@DeleteMapping\(\"(.*)\"\)')
    mappings = []

    def __init__(self, filename):
        self._filename = filename
        self._class_name = re.match(r'^.*\/(.*)\.java', filename).group(1)
        self.parse_file()
        print(self)

    def parse_file(self):
        lines = open(self._filename).readlines()
        for line in lines:
            match = self.authentication_re.match(line)
            if match:
                self.authentication_missing = False
            match = self.request_matching_re.match(line)
            if match:
                self.mapping_root = match.group(1)
            match = self.get_matching_re.match(line)
            if match:
                self.mappings.append(f'GET {self.mapping_root}{match.group(1)}')
            match = self.post_matching_re.match(line)
            if match:
                self.mappings.append(f'POST {self.mapping_root}{match.group(1)}')
            match = self.put_matching_re.match(line)
            if match:
                self.mappings.append(f'PUT {self.mapping_root}{match.group(1)}')
            match = self.patch_matching_re.match(line)
            if match:
                self.mappings.append(f'PATCH {self.mapping_root}{match.group(1)}')
            match = self.delete_matching_re.match(line)
            if match:
                self.mappings.append(f'DELETE {self.mapping_root}{match.group(1)}')

    def get_filename(self):
        return self._filename

    def __str__(self):
        mappings = "\n\t    ".join(self.mappings)
        secured = '  ' if self.authentication_missing else u'\U0001F512 '
        return f'\n\t{secured}{self._class_name}\n\t    {mappings}'
