import argparse
from controller import Controller
from repository import Repository
import logging
import sys
import os
import re
import json
import graphviz

rootdir = os.getenv('PROJECT_FOLDER')
master_config_location = rootdir + '/ofl-next-accelerators/master-config/master_config.yml'
platform_names = ['accounting', 'carrier', 'customer', 'ecosystem', 'shared', 'supplier', 'all']
platforms = {'accounting': { "titleColor": "#CF6785", "serviceColor": "#F3D4DE"}, 
             'carrier': {"titleColor": "#7A4683", "serviceColor": "#CDBDD0"}, 
             'customer': {"titleColor": "#87B357", "serviceColor": "#CDE6B2"}, 
             'ecosystem': {"titleColor": "#46937E", "serviceColor": "#A5D3CA"}, 
             'pot': {}, 
             'shared': {}, 
             'supplier': {"titleColor": "#E2913E", "serviceColor": "#F9DCAF"}, 
             'shared-logging': {}, 
             'clam-av-gcp-client': {}}

platform_re = re.compile(r'\s{2}-\sname:\s(.*)')
service_re = re.compile(r'\s{6}-\sname:\s(.*)')
repo_re = re.compile(r'\s{8}repo_name:\s(.*)')
port_re = re.compile(r'\s{8}port:\s(.*)')
publish_re = re.compile(r'\s{8}publish_topics:\s(.*)')
subscribe_re = re.compile(r'\s{8}subscribe_topics:\s(.*)')
publish_topic_re = re.compile(r'\s{10}-\s(.*)')
subscribe_topic_re = re.compile(r'\s{10}-\sname:\s(.*)')
end_pubsub_re = re.compile(r'\s{0,8}[^\s]')

ignore_list = ['.DS_Store', '.gradle']
repositories = []
subgraphs = []


# Topic color: #8EBAE1
# controller color: #CDE6B2

def process_platforms(platform_list, dot):
    logging.info(f'Root directory: {rootdir}\n')

    # Process platforms
    for platform_name in platform_list:
        logging.info(f'PLATFORM: {platform_name.upper()}')
        logging.info('=========================')

        cloud_config = []
        if platform_name == 'pot':
            logging.info('skipping pot platform')
        else:
            cloud_config_path = f'{rootdir}/shared/ofl-next-cloud-config/config/stage/'
            file = open(f'{cloud_config_path}{platform_name}.json')
            cloud_config = json.load(file)


        services = platforms[platform_name]['services'] if 'services' in platforms[platform_name] else None
        current_dir = f'{rootdir}/{platform_name}'
        for dir in os.listdir(current_dir):
            if dir not in ignore_list:
                repository = Repository(current_dir, dir, platforms[platform_name], cloud_config)
                repositories.append(repository)

        # platforms[platform_name]['platform'] = monarch_platform

        buckets = cloud_config['gcp']['buckets']
        for bucket in buckets:
            logging.info(f"BUCKET: {bucket['name']}")

def process_master_config(platform_list):
    lines = open(master_config_location).readlines()
    curr_platform = None
    curr_service = None
    curr_graph = None
    subscribing = False
    publishing = False
    skipping = False

    for line in lines:
        # Check for platform
        match = platform_re.match(line)
        if match:
            name = match.group(1)
            if name in platform_list:
                logging.debug(f'Found {name} in {platform_list}')
                skipping = False
                curr_platform = platforms[name]
                curr_platform['services'] = []
                logging.debug(f'PLATFORM: {name}')
                font_color = platforms[name]['titleColor'] if 'titleColor' in platforms[name] else 'black'
                curr_graph = graphviz.Digraph('cluster_'+name, graph_attr={"label": name.upper(), "fontname": "Helvetica", "fontsize": "32", "fontcolor": font_color}, edge_attr={"edge": "ortho"}, node_attr={"fontname": "Helvetica", "nodesep": ".25"})
                curr_platform['subgraph'] = curr_graph
                subgraphs.append(curr_graph)
                continue
            else:
                skipping = True

        if skipping:
            continue

        # Check for a service file
        match = service_re.match(line)
        if match:
            name = match.group(1)
            curr_service = { 'name': name}
            curr_platform['services'].append(curr_service)
            curr_service['publishes'] = []
            curr_service['subscribes'] = []
            logging.debug(f'  service: {name}')
            curr_graph.node(name, shape='box', style='filled', fillcolor='lightgrey')
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
                    name = match.group(1)
                    logging.debug(f'\tpublishing to: {name}')
                    curr_service['publishes'].append(name)
                    curr_graph.edge(curr_service['name'], name)
                    continue

            # Check for topic being subscribed to
            match = subscribe_topic_re.match(line)
            if match:
                if subscribing:
                    name = match.group(1)
                    logging.debug(f'\tsubscribing to: {name}')
                    curr_service['subscribes'].append(name)
                    curr_graph.edge(name, curr_service['name'])
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

    target_string = args['target'][0]
    target_platforms = platform_names[:-1] if target_string == 'all' else target_string.split(',')

    dot = graphviz.Digraph("Monarch", comment="Monarch Overview", graph_attr={"rankdir": "LR", "layout": "dot"}, edge_attr={"edge": "ortho"}, node_attr={"fontname": "Helvetica"})
    # dot, fdp
    # neato, twopi, circo, sfdp, osage, patchwork, 

    process_master_config(target_platforms)
    process_platforms(target_platforms, dot)

    for graph in subgraphs:
        dot.subgraph(graph)

    dot.render(directory=rootdir+'../../blueprint', view=True).replace('\\', '/')
