import requests
import docker
import json
from datetime import datetime, timedelta, timezone
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
        self.print_lock = Lock()
        self.reveise_connections = datetime.now() + timedelta(hours=5)
        
        for entry in docker_containers:
            self.poke_docker_container(entry['container_id'])
            port_entry = {'http': f'http://localhost:{entry["port"]}','https': f'http://localhost:{entry["port"]}',}
            
            entry['proxy_config'] = port_entry
            entry['successful'] = 0
            entry['failed'] = 0
            entry['black_list'] = {}
            entry['status'] = self.test_connection(port_entry)
            
            self.connections[entry['location']] = entry

    def test_connection(self,proxy):
        response = requests.get('https://api.bigdatacloud.net/data/client-ip', proxies=proxy)
        if response.status_code == 200:
            self.local_print(response.text)
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
            
            for platform,black_list_time in connection_details['black_list'].items():
                if curr_time - black_list_time > timedelta(days=1):
                    del connection_details['black_list'][platform]
                    
            connection_details['status'] = self.test_connection(connection_details['proxy_config'])
    
    def perform_get_request(self,platform,url,headers,params=None,retry=True):
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
        
        if platform in connection_details['black_list'] or connection_details['status'] == False:
            return None
        elif min_tunnel == None:
            if headers == None:
                responce = requests.get(url=url,params=params)
            else:
                responce = requests.get(url=url,params=params,headers=headers)
        else:
            if headers == None:
                responce = requests.get(url=url,params=params,proxies=min_tunnel['proxy_config'])
            else:
                responce = requests.get(url=url,params=params,headers=headers,proxies=min_tunnel['proxy_config'])
            
        if not responce.status_code == 200:
            min_tunnel['black_list'][platform] = datetime.now().astimezone(timezone.utc)
            self.local_print(f"{platform} has been black_listed from {min_tunnel['location']}")
            with self.lock:
                min_tunnel['failed'] += 1
            if retry:
                return self.perform_get_request(platform,url,headers,params,retry=False)
            else:
                return None
        with self.lock:
            min_tunnel['successful'] += 1
            
        if self.reveise_connections < curr_time:
            self.revise_connections()
            
        return json.loads(responce.text)
    
    def local_print(self,msg):
        with self.print_lock:
            print(f"hydra: {msg}")

