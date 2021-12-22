import os
import configparser
import pathlib
import sys
from controller import Controller
from platform import Platform

rootdir = '/Users/tad.lamb/devl/ofl-next'

java_file = '/Users/tad.lamb/devl/ofl-next/accounting/ofl-next-accounting-experience-api/src/main/java/com/cardinalhealth/accounting/experience/controller/PendingReviewExperienceController.java'

controllers = []
platforms = []

def load_properties():
    config = configparser.ConfigParser()
    config.read('blueprint.properties')
    project_root = config.get('General', 'project-root')
    print(f'Root directory: {project_root}\n')
    for platform in config.get('General', 'platforms').split(','):
        platforms.append(Platform(platform))

def get_mappings(filename):
    controller = Controller(filename)
    controller.parse_file()
    controllers.append(controller)

if __name__ == "__main__":
    load_properties()
    get_mappings(java_file)
    for controller in controllers:
        print(controller)
    # for subdir, dirs, files in os.walk('.'):
    #     for file in files:
    #         print(file)
    #         print os.path.join(subdir, file)

