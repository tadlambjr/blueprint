import argparse
from blueprint_graph import BlueprintGraph
from controller import Controller
from repository import Repository
from master_config import MasterConfig
import logging
import sys
import os
import json
import graphviz

rootdir = os.getenv('PROJECT_FOLDER')
ignore_list = ['.DS_Store', '.gradle']
platform_names = ['accounting', 'carrier', 'customer', 'ecosystem', 'shared', 'supplier', 'all']
platforms = {'accounting': {"titleColor": "#CF6785", "serviceColor": "#F3D4DE"}, 
             'carrier':    {"titleColor": "#7A4683", "serviceColor": "#CDBDD0"}, 
             'customer':   {"titleColor": "#87B357", "serviceColor": "#CDE6B2"}, 
             'ecosystem':  {"titleColor": "#46937E", "serviceColor": "#A5D3CA"}, 
             'pot': {}, 
             'shared': {}, 
             'supplier':   {"titleColor": "#E2913E", "serviceColor": "#F9DCAF"}, 
             'shared-logging': {}, 
             'clam-av-gcp-client': {}}

# Topic color: #8EBAE1

def process_platforms(platform_list):
    for platform_name in platform_list:
        logging.info(f'PLATFORM: {platform_name.upper()}')
        logging.info('=========================')

        if platform_name != 'pot':
            cloud_config_path = f'{rootdir}/shared/ofl-next-cloud-config/config/stage/'
            file = open(f'{cloud_config_path}{platform_name}.json')
            platforms[platform_name]['cloud_config'] = json.load(file)

        current_dir = f'{rootdir}/{platform_name}'
        for dir in os.listdir(current_dir):
            if dir not in ignore_list:
                Repository(current_dir, dir, platforms[platform_name])

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
    # good layout engines: dot, fdp
    # other layout engines: neato, twopi, circo, sfdp, osage, patchwork, 

    # process_master_config(target_platforms)
    MasterConfig(rootdir, platforms, target_platforms)
    process_platforms(target_platforms)
    BlueprintGraph(dot, platforms, target_platforms)

    dot.render(directory=rootdir+'../../blueprint', view=True).replace('\\', '/')
