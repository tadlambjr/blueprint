import configparser
import argparse
from controller import Controller
from platform import Platform
import pathlib
import sys
import os

rootdir = os.getenv('PROJECT_FOLDER')
java_file = '/Users/tad.lamb/devl/ofl-next/accounting/ofl-next-accounting-experience-api/src/main/java/com/cardinalhealth/accounting/experience/controller/PendingReviewExperienceController.java'
platform_names = ['carrier', 'customer', 'supplier', 'accounting', 'pot', 'ecosystem', 'allocation', 'shared', 'all']
platforms = []

def process_platforms(platform_list):
    # Read config file
    # config = configparser.ConfigParser()
    # config.read('blueprint.properties')
    # project_root = config.get('General', 'project-root')
    print(f'Root directory: {rootdir}\n')

    # Process platforms
    for platform_name in platform_list:
        platform = Platform(rootdir, platform_name)
        platforms.append(platform)

def get_mappings(filename):
    controller = Controller(filename)
    controller.parse_file()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Provide an overview of the microservice architecture')
    parser.add_argument('--target', '-t', choices=platform_names, required=True, type=str, metavar='target', help='The platform to target', nargs='+')
    args = vars(parser.parse_args())

    target_string = args['target'][0]
    if target_string == 'all':
        process_platforms(platform_names[:-1])
    else:
        process_platforms(target_string.split(','))
    get_mappings(java_file)
    # for controller in controllers:
    #     print(controller)
    # for subdir, dirs, files in os.walk('.'):
    #     for file in files:
    #         print(file)
    #         print os.path.join(subdir, file)

