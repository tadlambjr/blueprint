import logging
import graphviz
import re

class BlueprintGraph:
    BUCKET_COLOR = '#A36A2C'
    INSTANCE_COLOR = '#000000'
    DATABASE_COLOR = '#E3913E'
    TOPIC_COLOR = '#59A5D8'
    CONTROLLER_COLOR = '#CDE6B2'
    UI_COLOR = '#FDECB1'

    def __init__(self, dot, platforms, target_platforms):
        for name in target_platforms:
             self.create_platform_graph(dot, name, platforms[name], target_platforms)

    def create_platform_graph(self, dot, name, properties, target_platforms):
        font_color = properties['titleColor'] if 'titleColor' in properties else 'black'
        label = f'<<b>{name.upper()}</b>>'
        curr_graph = graphviz.Digraph('cluster_'+name, graph_attr={"label": label, "fontname": "Helvetica", "fontsize": "32", "fontcolor": font_color}, edge_attr={"fontname": "Helvetica", "edge": "ortho"}, node_attr={"fontname": "Helvetica", "nodesep": ".25"})
        # self.add_buckets(curr_graph, properties)
        # self.add_instances(curr_graph, properties)
        self.add_services(curr_graph, properties)
        # self.add_ui(curr_graph, name)
        # self.add_additions(curr_graph, target_platforms)
        dot.subgraph(curr_graph)

    def add_instances(self, graph, properties):
        font_color = properties['titleColor'] if 'titleColor' in properties else 'black'
        cloud_config = properties['cloud_config']
        for instance in cloud_config['gcp']['instances']:
            name = instance['name']
            label = f"{name}\lcpu: {instance['cpu']}  memory: {instance['memory']}  storage: {instance['storage']}"
            curr_graph = graphviz.Digraph('cluster_'+name, graph_attr={"label": label, "fontname": "Helvetica", "fontsize": "16", "fontcolor": font_color}, edge_attr={"fontname": "Helvetica", "edge": "ortho"}, node_attr={"fontname": "Helvetica", "nodesep": ".25"})
            self.add_databases(name, curr_graph, properties)
            graph.subgraph(curr_graph)

    def add_buckets(self, graph, properties):
        cloud_config = properties['cloud_config']
        buckets = cloud_config['gcp']['buckets']
        for bucket in buckets:
            bucket_name = re.sub('-stage$', '', bucket['name'])
            graph.node(bucket_name, shape='box3d', fontcolor='white', fillcolor=self.BUCKET_COLOR, style='filled')
            logging.debug(f'BUCKET: {bucket}')
            if len(bucket['notifications']) > 0:
                topic_name = re.sub('-stage$', '', bucket['notifications'][0]['topic'])
                graph.edge(bucket_name, topic_name)

    def add_databases(self, instance_name, graph, properties):
        cloud_config = properties['cloud_config']
        databases = cloud_config['gcp']['databases']
        for database in databases:
            if database['instance'] != instance_name:
                continue
            name = database['name']
            graph.node(f'{name}-db', label=name, shape='cylinder', fontcolor='white', fillcolor=self.DATABASE_COLOR, style='filled')
            logging.debug(f'DATABASE: {database}')

    def add_services(self, graph, properties):
        for service in properties['services']:
            name = service['name']
            cluster_label = f'{name}\l' + u'\u2387  git: ' + f" {service['repo_name']}" if 'repo_name' in service else name
            curr_graph = graphviz.Digraph('cluster_'+name, graph_attr={"label": cluster_label, "fontsize": "16"})
            
            # if 'controllers' in service:
            #     for controller in service['controllers']:
            #         curr_graph.node(controller.node_name(), controller.node_label(), shape='Mrecord', style='filled', fillcolor=self.CONTROLLER_COLOR)

            service_label = f"{name}:{service['port']}" if 'port' in service else name
            service_color = properties['serviceColor'] if 'serviceColor' in properties else 'lightgrey'
            curr_graph.node(f'{name}-service', label=service_label, shape='box', fillcolor=service_color, style='filled')
            for topic in service['publishes']:
                curr_graph.node(topic, shape='box', fontcolor='white', fillcolor=self.TOPIC_COLOR, style='filled')
                curr_graph.edge(f'{name}-service', topic)
            for topic in service['subscribes']:
                curr_graph.node(topic, shape='box', fontcolor='white', fillcolor=self.TOPIC_COLOR, style='filled')
                curr_graph.edge(topic, f'{name}-service')
            graph.subgraph(curr_graph)

    def add_ui(self, graph, platform_name):
        if platform_name == 'accounting':
            graph.node('accounting', label='<<b>Accounting UI</b>>', shape='Mcircle', fillcolor=self.UI_COLOR, style='filled')
        if platform_name == 'carrier':
            graph.node('carrier', label='<<b>Carrier UI</b>>', shape='Mcircle', fillcolor=self.UI_COLOR, style='filled')

    def add_additions(self, graph, target_platforms):
        file = open('additions.txt', 'r')
        for line in file.readlines():
            if line.startswith('#'):
                continue
            platform, source, target, label = line.split(',')
            if platform in target_platforms:
                graph.edge(source, target, label)