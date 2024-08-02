import requests
import docker
import json
from datetime import datetime, timedelta
import subprocess
import os

class hydra():
    def __init__(self) -> None:
        current_file = os.path.dirname(os.path.abspath(__file__))
        docker_info = os.path.join(current_file,'docker_info.json')

        with open(docker_info, 'r') as file:
            file_content = file.read()

        self.docker_engine = docker.from_env()
        docker_containers = json.loads(file_content)['data']
        self.connections = {}
        for entry in docker_containers:
            container = self.docker_engine.containers.get(entry['container_id'])
            if container.status != 'running':
                subprocess.run(["docker-compose", "up", "-d", entry['container_id']])
            
            port_entry = {
                'http': f'http://localhost:{entry["port"]}',
                'https': f'http://localhost:{entry["port"]}',
            }
            
            if self.test_connection(port_entry):
                entry['proxy_config'] = port_entry
                entry['succesful'] = 0
                entry['failed'] = 0
                self.connections[entry['location']] = entry

    def test_connection(self,proxy):
        response = requests.get('https://api.bigdatacloud.net/data/client-ip', proxies=proxy)
        if response.status_code == 200:
            print(response.text)
            return True
        return False
    
test = hydra()



