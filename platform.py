import os

from repository import Repository
class Platform:

    ignore_list = ['.DS_Store']
    repositories = []

    def __init__(self, root_dir, name):
        self._name = name
        self._root_dir = root_dir
        print(self)
        self.find_repositories()

    def find_repositories(self):
        current_dir = f'{self._root_dir}/{self._name}'
        for dir in os.listdir(current_dir):
            if dir not in self.ignore_list:
                repository = Repository(current_dir, dir)
                self.repositories.append(repository)

    def __str__(self):
        return f'    Platform: {self._name}'