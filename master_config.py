import logging
import re

class MasterConfig:

    def __init__(self, rootdir, platforms, platform_list, suppress_airs, suppress_dlqs):
        self.process_file(rootdir, platforms, platform_list, suppress_airs, suppress_dlqs)

    def strip_parens(self, topic):
        return re.sub('\(.*\)', '', topic)

    def process_file(self, rootdir, platforms, platform_list, suppress_airs, suppress_dlqs):
        master_config_location = rootdir + '/ofl-next-accelerators/master-config/master_config.yml'
        platform_re = re.compile(r'\s{2}-\sname:\s(.*)')
        service_re = re.compile(r'\s{6}-\sname:\s(.*)')
        repo_re = re.compile(r'\s{8}repo_name:\s(.*)')
        port_re = re.compile(r'\s{8}port:\s(.*)')
        publish_re = re.compile(r'\s{8}publish_topics:\s(.*)')
        subscribe_re = re.compile(r'\s{8}subscribe_topics:\s(.*)')
        publish_topic_re = re.compile(r'\s{10}-\s(.*)')
        subscribe_topic_re = re.compile(r'\s{10}-\sname:\s(.*)')
        end_pubsub_or_feature_re = re.compile(r'\s{0,8}[^\s]')
        features_re = re.compile(r'\s{0,8}features')
        feature_re = re.compile(r'\s{0,10}-\sname:\s(.*)')

        lines = open(master_config_location).readlines()
        curr_platform = None
        curr_service = None
        features = False
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
                    continue
                else:
                    skipping = True

            if skipping:
                continue

            # Check for a service file
            match = service_re.match(line)
            if match:
                name = match.group(1)
                if not suppress_airs or name != 'accounting-invoice-resource':
                    curr_service = { 'name': name}
                    curr_platform['services'].append(curr_service)
                    curr_service['publishes'] = []
                    curr_service['subscribes'] = []
                    curr_service['features'] = []
                    logging.debug(f'  service: {name}')
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
                        name = self.strip_parens(match.group(1))
                        logging.debug(f'\tpublishing to: {name}')
                        if not suppress_dlqs or not name.endswith('-dlq'):
                            curr_service['publishes'].append(name)
                        continue

                # Check for topic being subscribed to
                match = subscribe_topic_re.match(line)
                if match:
                    if subscribing:
                        name = self.strip_parens(match.group(1))
                        logging.debug(f'\tsubscribing to: {name}')
                        if not suppress_dlqs or not name.endswith('-dlq'):
                            curr_service['subscribes'].append(name)
                        continue

                # Check for line after a pub or sub
                match = end_pubsub_or_feature_re.match(line)
                if match:
                    x = 'pub' if publishing else 'sub'
                    logging.debug(f'Turning off {x} with {line}')
                    publishing = False
                    subscribing = False

            if features:
                match = feature_re.match(line)
                if match:
                    logging.debug(f'Adding feature: {match.group(1)}')
                    curr_service['features'].append(match.group(1))

                # Check for line after features list
                match = end_pubsub_or_feature_re.match(line)
                if match:
                    logging.debug(f'Turning off features with {line}')
                    features = False

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

            # Check for start of features
            match = features_re.match(line)
            if match:
                logging.debug(f'Turning on list of features with {line}')
                features = True
                continue
