import os
import re
import logging
import configparser
from controller import Controller
from service import Service

class Repository:
    # port
    git_path = '.git/config'
    java_path = 'src/main/java'

    controllers = []
    services = []
    repo_services = []

    def __init__(self, dir, name, services):
        self._dir = dir
        self._name = name
        self._services = services
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

    # def convert_to_yml_name(self, service_name):
    #     shortened = service_name[:-len('Service')]
    #     output = [shortened[0].lower()]
    #     for c in shortened[1:]:
    #         if c in ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    #             output.append('-')
    #             output.append(c.lower())
    #         else:
    #                  output.append(c)            
    #     return str.join('', output)

    # def locate_service_dict(self, service_name):
    #     yml_name = self.convert_to_yml_name(service_name)
    #     logging.info(f'Trying to find {yml_name} in\n{self.repo_services}')

    def scan_code(self):
        full_java_path = f'{self._dir}/{self._name}/{self.java_path}'
        for root, dirs, files in os.walk(full_java_path):
            if len(files) > 0:
                for file in files:
                    if file.endswith('.java'):
                        if file.endswith('Controller.java'):
                            controller = Controller(f'{root}/{file}')
                            self.controllers.append(controller)
                        elif file.endswith('Service.java'):
                            class_name = re.match(r'(.*)\.java', file).group(1)
                            # self.locate_service_dict(class_name)
                            service = Service(f'{root}/{file}')
                            self.services.append(service)

    def get_repo_detail_string(self):
        output = []
        if 'services' in self._services:
            for service in self._services['services']:
                if 'repo_name' in service and service['repo_name'] == self._name:
                    if 'name' in service:
                        output.append(f"\t\tname: {service['name']}")
                    if 'port' in service:
                        output.append(f"port: {service['port']}")
                    if len(service['publishes']) > 0:
                        output.append('PUBLISHES TO:')
                        for topic in service['publishes']:
                            output.append(u'  \U000021e8' + f' {topic}')
                    if len(service['subscribes']) > 0:
                        output.append('SUBSCRIBES TO:')
                        for topic in service['subscribes']:
                            output.append(u'  \U000021e6' + f' {topic}')
        return str.join('\n\t\t', output)

    def __str__(self):
        return f'\n\tRepository: {self._name} ({self.git_repo})\n{self.get_repo_detail_string()}'