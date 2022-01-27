import logging
import graphviz
import re

class BlueprintGraph:
    BUCKET_COLOR = '#A36A2C'
    INSTANCE_COLOR = '#000000'
    DATABASE_COLOR = '#E3913E'
    TOPIC_COLOR = '#59A5D8'
    CONTROLLER_COLOR = '#CDE6B2'

    def __init__(self, dot, platforms, target_platforms):
        for name in target_platforms:
             self.create_platform_graph(dot, name, platforms[name])

    def create_platform_graph(self, dot, name, properties):
        # logging.info(f'ALL PROPERTIES: {properties}')
        font_color = properties['titleColor'] if 'titleColor' in properties else 'black'
        label = f'<<b>{name.upper()}</b>>'
        curr_graph = graphviz.Digraph('cluster_'+name, graph_attr={"label": label, "fontname": "Helvetica", "fontsize": "32", "fontcolor": font_color}, edge_attr={"edge": "ortho"}, node_attr={"fontname": "Helvetica", "nodesep": ".25"})
        self.add_buckets(curr_graph, properties)
        self.add_instances(curr_graph, properties)
        self.add_services(curr_graph, properties)
        dot.subgraph(curr_graph)

    def add_instances(self, graph, properties):
        font_color = properties['titleColor'] if 'titleColor' in properties else 'black'
        cloud_config = properties['cloud_config']
        for instance in cloud_config['gcp']['instances']:
            name = instance['name']
            label = f"{name}\lcpu: {instance['cpu']}  memory: {instance['memory']}  storage: {instance['storage']}"
            curr_graph = graphviz.Digraph('cluster_'+name, graph_attr={"label": label, "fontname": "Helvetica", "fontsize": "16", "fontcolor": font_color}, edge_attr={"edge": "ortho"}, node_attr={"fontname": "Helvetica", "nodesep": ".25"})
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
            logging.info(f'SERVICE: {service}')
            name = service['name']
            cluster_label = f'{name}\l' + u'\u2387  git: ' + f" {service['repo_name']}"
            curr_graph = graphviz.Digraph('cluster_'+name, graph_attr={"label": cluster_label, "fontsize": "16"})
            
            if 'controllers' in service:
                for controller in service['controllers']:
                    curr_graph.node(controller.node_string(), shape='box', style='filled', fillcolor=self.CONTROLLER_COLOR)
                    logging.info(f'CONTROLLER: {controller.node_string()}')
# controller_cluster = graphviz.Digraph('cluster_controllers', graph_attr={"rankdir": "TB", "rank": "same", "label": "Controllers", "fontname": "Helvetica", "fontsize": "32"}, edge_attr={"edge": "ortho"}, node_attr={"fontname": "Helvetica", "nodesep": ".25"})
# for controller in self.controllers:
#     controller_cluster.node(controller.node_string(), shape='box', style='filled', fillcolor=self.CONTROLLER_COLOR)
# self._graph.subgraph(controller_cluster)

            curr_graph.node(f'{name}-service', label=f"{name}:{service['port']}", shape='box', fillcolor=properties['serviceColor'], style='filled')
            for topic in service['publishes']:
                curr_graph.node(topic, shape='box', fontcolor='white', fillcolor=self.TOPIC_COLOR, style='filled')
                curr_graph.edge(f'{name}-service', topic)
            for topic in service['subscribes']:
                curr_graph.node(topic, shape='box', fontcolor='white', fillcolor=self.TOPIC_COLOR, style='filled')
                curr_graph.edge(topic, f'{name}-service')
            graph.subgraph(curr_graph)


