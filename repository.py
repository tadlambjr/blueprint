import os
import logging
import configparser
from controller import Controller

class Repository:
    # port
    git_path = '.git/config'
    java_path = 'src/main/java'

    controllers = []

    def __init__(self, dir, name):
        self._dir = dir
        self._name = name
        self.get_git_repo()
        logging.info(self)
        self.scan_code()

    def get_git_repo(self):
        config = configparser.ConfigParser()
        git_filepath = f'{self._dir}/{self._name}/{self.git_path}'
        config.read(git_filepath)
        try:
            self.git_repo = u'\u2387  git: ' + config.get('remote "origin"', 'url')
        except:
            self.git_repo = 'git repo section not found'

    def scan_code(self):
        full_java_path = f'{self._dir}/{self._name}/{self.java_path}'
        for root, dirs, files in os.walk(full_java_path):
            if len(files) > 0:
                for file in files:
                    if file.endswith('.java'):
                        if 'Controller' in file:
                            controller = Controller(f'{root}/{file}')
                            self.controllers.append(controller)


    def __str__(self):
        return f'\n\tRepository: {self._name} ({self.git_repo})'