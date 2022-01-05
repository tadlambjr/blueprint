import os
import logging

from repository import Repository
class Platform:

    ignore_list = ['.DS_Store', '.gradle']
    repositories = []

    def __init__(self, root_dir, name, services):
        self._name = name
        self._root_dir = root_dir
        self._services = services
        logging.info(self)
        logging.info('=========================')
        self.find_repositories()

    def find_repositories(self):
        current_dir = f'{self._root_dir}/{self._name}'
        for dir in os.listdir(current_dir):
            if dir not in self.ignore_list:
                repository = Repository(current_dir, dir, self._services)
                self.repositories.append(repository)

    def __str__(self):
        return f'\nPLATFORM: {self._name}'