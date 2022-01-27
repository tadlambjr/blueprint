import os
import re
import logging
import configparser
# import graphviz
from controller import Controller
from service import Service

class Repository:
    CONTROLLER_COLOR = '#CDE6B2'
    git_path = '.git/config'
    java_path = 'src/main/java'

    services = []
    repo_services = []
    service_files = []

    def __init__(self, dir, name, properties):
        self._dir = dir
        self._name = name
        self._properties = properties
        self._services = properties['services'] if 'services' in properties else []
        self.get_git_repo()
        self.scan_code()
        logging.debug(f'PROPERTIES: {properties}')

    def get_git_repo(self):
        config = configparser.ConfigParser()
        git_filepath = f'{self._dir}/{self._name}/{self.git_path}'
        config.read(git_filepath)
        try:
            self.git_repo = u'\u2387  git: ' + config.get('remote "origin"', 'url')
        except:
            self.git_repo = 'git repo section not found'

    def scan_code(self):
        controllers = []
        full_java_path = f'{self._dir}/{self._name}/{self.java_path}'
        for root, dirs, files in os.walk(full_java_path):
            if len(files) > 0:
                for file in files:
                    service_name = re.match(r'^.*/(.*)/src/.*$', root).group(1)
                    if file.endswith('.java'):
                        if file.endswith('Controller.java'):
                            controller = Controller(f'{root}/{file}')
                            controllers.append(controller)
                        elif file.endswith('Service.java'):
                            service = Service(f'{root}/{file}')
                            self.service_files.append(service)
                            if len(controllers) > 0:
                                for located_service in self._services:
                                    if located_service['name'] == service_name:
                                        located_service['controllers'] = controllers
                                        controllers = []

    def get_repo_detail_string(self):
        output = []
        if len(self._services) > 0:
            for service in self._services:
                logging.debug(f"SERVICE: [{service}]")
                if 'repo_name' in service and service['repo_name'] == self._name:
                    if 'name' in service:
                        logging.debug(f"NAME: {service['name']}")
                        self._graph.node(service['name'], shape='box', style='filled', fillcolor=self._properties['serviceColor'])
                        output.append(f"\t\tname: {service['name']}")
                    if 'port' in service:
                        output.append(f"port: {service['port']}")
                    if len(service['publishes']) > 0:
                        output.append('PUBLISHES TO:')
                        for topic in service['publishes']:
                            # self._graph.edge(service['name'], topic)
                            output.append(u'  \U000021e8' + f' {topic}')
                    if len(service['subscribes']) > 0:
                        output.append('SUBSCRIBES TO:')
                        for topic in service['subscribes']:
                            # self._graph.edge(topic, service['name'])
                            output.append(u'  \U000021e6' + f' {topic}')
        return str.join('\n\t\t', output)

    def __str__(self):
        return f'\n\tRepository: {self._name} ({self.git_repo})\n{self.get_repo_detail_string()}'