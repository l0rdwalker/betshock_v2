import requests
import docker
import json
from datetime import datetime, timedelta
import subprocess
import os
from threading import Lock

class hydra():
    def __init__(self) -> None:
        current_file = os.path.dirname(os.path.abspath(__file__))
        docker_info = os.path.join(current_file,'docker_info.json')

        with open(docker_info, 'r') as file:
            file_content = file.read()

        self.docker_engine = docker.from_env()
        docker_containers = json.loads(file_content)['data']
        
        self.connections = {}
        self.lock = Lock()
        self.reveise_connections = datetime.now() + timedelta(hours=5)
        
        for entry in docker_containers:
            self.poke_docker_container(entry['container_id'])
            port_entry = {'http': f'http://localhost:{entry["port"]}','https': f'http://localhost:{entry["port"]}',}
            
            entry['proxy_config'] = port_entry
            entry['succesful'] = 0
            entry['failed'] = 0
            entry['black_list'] = set()
            entry['status'] = self.test_connection(port_entry)
            
            self.connections[entry['location']] = entry

    def test_connection(self,proxy):
        response = requests.get('https://api.bigdatacloud.net/data/client-ip', proxies=proxy)
        if response.status_code == 200:
            print(response.text)
            return True
        return False
    
    def poke_docker_container(self, container_id):
        container = self.docker_engine.containers.get(container_id)
        if container.status != 'running':
            subprocess.run(["docker-compose", "up", "-d", container_id])
    
    def revise_connections(self):
        curr_time = datetime.now()
        for loc, connection_details in self.connections.items():
            self.poke_docker_container(connection_details['container_id'])
            
            for platform in connection_details['black_list']:
                if curr_time - platform[1] < timedelta(days=1):
                    connection_details['black_list'].remove(platform)
                    
            connection_details['status'] = self.test_connection(connection_details['proxy_config'])
    
    def perform_get_request(self,platform,url,params,headers):
        min_calls = None
        min_tunnel = None
        curr_time = datetime.now()
        
        for loc, connection_details in self.connections.items():
            if platform in connection_details['black_list'] or connection_details['status'] == False:
                continue
            if min_calls == None or min_tunnel == None:
                min_calls = connection_details['successful']
                min_tunnel = connection_details
            elif connection_details['successful'] < min_calls:
                min_calls = connection_details['successful']
                min_tunnel = connection_details
        
        responce = requests.get(url=url,params=params,headers=headers,proxies=min_tunnel['proxy_config'])
        if not responce.status_code == 200:
            min_tunnel['black_list'].add((platform,datetime.now()))
            with self.lock:
                min_tunnel['failed'] += 1
            return None
        with self.lock:
            min_tunnel['successful'] += 1
            
        if self.reveise_connections < curr_time:
            self.revise_connections()
            
        return json.loads(responce)

