import argparse
from controller import Controller
from platform import Platform
import logging
import sys
import os

rootdir = os.getenv('PROJECT_FOLDER')
platform_names = ['accounting', 'carrier', 'customer', 'ecosystem', 'pot', 'shared', 'supplier', 'all']
platforms = []

def process_platforms(platform_list):
    logging.info(f'Root directory: {rootdir}\n')

    # Process platforms
    for platform_name in platform_list:
        platform = Platform(rootdir, platform_name)
        platforms.append(platform)

def get_mappings(filename):
    controller = Controller(filename)
    controller.parse_file()

if __name__ == "__main__":
    targets = logging.StreamHandler(sys.stdout), logging.FileHandler('blueprint.txt', mode='w')
    logging.basicConfig(format='%(message)s', level=logging.INFO, handlers=targets)

    parser = argparse.ArgumentParser(description='Provide an overview of the microservice architecture')
    parser.add_argument('--target', '-t', choices=platform_names, required=True, type=str, metavar='target', help='The platform to target', nargs='+')
    args = vars(parser.parse_args())

    target_string = args['target'][0]
    if target_string == 'all':
        process_platforms(platform_names[:-1])
    else:
        process_platforms(target_string.split(','))
