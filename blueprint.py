import argparse
from controller import Controller
from platform import Platform
import logging
import sys
import os
import re

rootdir = os.getenv('PROJECT_FOLDER')
master_config_location = rootdir + '/ofl-next-accelerators/master-config/master_config.yml'
platform_names = ['accounting', 'carrier', 'customer', 'ecosystem', 'pot', 'shared', 'supplier', 'all']
platforms = {'accounting': {}, 'carrier': {}, 'customer': {}, 'ecosystem': {}, 'pot': {}, 'shared': {}, 'supplier': {}, 'shared-logging': {}, 'pot': {}, 'clam-av-gcp-client': {}}

platform_re = re.compile(r'\s{2}-\sname:\s(.*)')
service_re = re.compile(r'\s{6}-\sname:\s(.*)')
repo_re = re.compile(r'\s{8}repo_name:\s(.*)')
port_re = re.compile(r'\s{8}port:\s(.*)')
publish_re = re.compile(r'\s{8}publish_topics:\s(.*)')
subscribe_re = re.compile(r'\s{8}subscribe_topics:\s(.*)')
publish_topic_re = re.compile(r'\s{10}-\s(.*)')
subscribe_topic_re = re.compile(r'\s{10}-\sname:\s(.*)')
end_pubsub_re = re.compile(r'\s{0,8}[^\s]')

def process_platforms(platform_list):
    logging.info(f'Root directory: {rootdir}\n')
    # dot = Digraph(comment='Monarch')

    # Process platforms
    for platform_name in platform_list:
        services = platforms[platform_name]['services'] if 'services' in platforms[platform_name] else None
        platform = Platform(rootdir, platform_name, platforms[platform_name])
        # platforms[platform_name]['platform'] = platform
        # dot.node(p, p)

    # dot.render('blueprint', view=True)

def process_master_config():
    lines = open(master_config_location).readlines()
    curr_platform = None
    curr_service = None
    subscribing = False
    publishing = False

    for line in lines:
        # Check for platform
        match = platform_re.match(line)
        if match:
            curr_platform = platforms[match.group(1)]
            curr_platform['services'] = []
            logging.debug(f'PLATFORM: {match.group(1)}')
            continue

        # Check for a service file
        match = service_re.match(line)
        if match:
            curr_service = { 'name': match.group(1)}
            curr_platform['services'].append(curr_service)
            curr_service['publishes'] = []
            curr_service['subscribes'] = []
            logging.debug(f'  service: {match.group(1)}')
            continue

        # Check for repository
        match = repo_re.match(line)
        if match:
            curr_service['repo_name'] = match.group(1)
            continue

        # Check for port
        match = port_re.match(line)
        if match:
            logging.debug(f'\tport: {match.group(1)}')
            curr_service['port'] = match.group(1)
            continue

        if publishing or subscribing:
            # Check for topic being published to
            match = publish_topic_re.match(line)
            if match:
                if publishing:
                    logging.debug(f'\tpublishing to: {match.group(1)}')
                    curr_service['publishes'].append(match.group(1))
                    continue

            # Check for topic being subscribed to
            match = subscribe_topic_re.match(line)
            if match:
                if subscribing:
                    logging.debug(f'\tsubscribing to: {match.group(1)}')
                    curr_service['subscribes'].append(match.group(1))
                    continue

            # Check for line after a pub or sub
            match = end_pubsub_re.match(line)
            if match:
                x = 'pub' if publishing else 'sub'
                logging.debug(f'Turning off {x} with {line}')
                publishing = False
                subscribing = False

        # Check for start of publish topics
        match = publish_re.match(line)
        if match:
            logging.debug(f'Turning on publishing with {line}')
            publishing = True
            continue

        # Check for start of subscribe topics
        match = subscribe_re.match(line)
        if match:
            logging.debug(f'Turning on subscribing with {line}')
            subscribing = True
            continue

if __name__ == "__main__":
    targets = logging.StreamHandler(sys.stdout), logging.FileHandler('blueprint.txt', mode='w')

    parser = argparse.ArgumentParser(description='Provide an overview of the microservice architecture')
    parser.add_argument('--target', '-t', choices=platform_names, required=True, type=str, metavar='target', help='The platform to target', nargs='+')
    parser.add_argument('--verbose', '-v',  help="debug level logging", action="store_true")

    args = vars(parser.parse_args())
    log_level = logging.DEBUG if args['verbose'] else logging.INFO
    logging.basicConfig(format='%(message)s', level=log_level, handlers=targets)

    process_master_config()
    target_string = args['target'][0]
    if target_string == 'all':
        process_platforms(platform_names[:-1])
    else:
        process_platforms(target_string.split(','))