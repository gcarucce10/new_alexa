import json
import os
import subprocess
import sys


class ResourceController:

    def __init__(self):
        try:
            # Usa caminho relativo ao arquivo atual para localizar o JSON de config
            base_dir = os.path.dirname(__file__)
            config_path = os.path.join(base_dir, 'resource_config.json')
            # alternativa: config_path = os.path.join(base_dir, 'server_config.json')
            with open(config_path, 'r', encoding='utf-8') as config_file:
                self.config: dict = json.load(config_file)
        except FileNotFoundError:
            print(f"Error: Configuration file not found at {config_path}.")
            self.config = None
        except json.JSONDecodeError:
            print("Error: Configuration file is not a valid JSON.")
            self.config = None
        except Exception as e:
            print(f"Unexpected error: {e}")
            self.config = None
        finally:
            self.available_resources = [{}]
            resources = self.config.get("resources", []) if self.config else []
            for resource in resources:
                name = resource.get("name", "")
                self.available_resources.append({"name": name, "process": None})


    def save_config(self):
        """
        Saves the current configuration to the resource_config.json file.
        """
        try:
            base_dir = os.path.dirname(__file__)
            config_path = os.path.join(base_dir, 'resource_config.json')
            with open(config_path, 'w', encoding='utf-8') as config_file:
                json.dump(self.config, config_file, indent=4)
            print(f"Configuration saved to {config_path}.")
        except Exception as e:
            print(f"Error saving configuration: {e}")
    

    def get_resource_names(self) -> list[str]:
        """
        Returns a list of available resource names.
        """
        resource_names = []
        for resource in self.available_resources:
            name = resource.get("name", "")
            if name:
                resource_names.append(name)
        return resource_names
    

    def parse_request(self, request: dict):
        """
        Parse the resource request and return the configuration dictionary.
        Checks if the requested resource is available.
        """
        try:
            # Verifica se há recursos para carregar
            resource = request.get("resource", {})

            if resource:
                name = resource.get("name", "")
                config = resource.get("config", {})

                for resource in self.available_resources:
                    if name == resource.get("name", ""):
                        return config
                    
            raise ValueError("Recurso não disponível ou inválido.")
        except Exception as e:
            print(f"Erro ao carregar recursos: {e}")
            return None
        

    def send_request(self, request: dict):
        """
        Dumps the resource configuration from the request to a temporary JSON file.
        This JSON file will be use by the resource then will be deleted after use.
        """

        config = self.parse_request(request)

        # dump config para ficheiro json temporário
        if config is not None:
            resource_name = request.get("resource", {}).get("name", "")
            absolute_dir: str = os.path.dirname(os.path.abspath(__file__))
            path_tofile = os.path.join(absolute_dir, resource_name)
            temp_config_path = os.path.join(path_tofile,f"{resource_name}_temp_config.json")
            try:
                with open(temp_config_path, 'w', encoding='utf-8') as temp_config_file:
                    json.dump(config, temp_config_file)
                
                print(f"Configuração temporária escrita em {temp_config_path}")

            except Exception as e:
                print(f"Erro ao escrever configuração temporária: {e}")

   

    def init_resource(self, resource_name: str):
        """
        Initialize the specified resource by starting its process.
        """

        # Building command to call the resource
        absolute_dir: str = os.path.dirname(os.path.abspath(__file__))
        path_tofile = os.path.join(absolute_dir, resource_name)

        for resource in self.config.get("resources", []):
            if resource_name == resource.get("name", ""):
                file_extension = resource.get("file-extension", None)
                file_port = resource.get("port", "5000")
                break
        filename:str = ""
        if file_extension :
            filename = f"{resource_name}." + file_extension

        path_tofile = os.path.join(path_tofile, filename)

        if os.name == 'linux' or os.name == 'darwin':
            command = [os.path.join(".", path_tofile)]
        else:
            command = [path_tofile]

        if file_extension == "py":
            command = [sys.executable, "-u", path_tofile]

        command.append(file_port)

        # Search for the resource and start the process
        for resource in self.available_resources:
            if resource_name == resource.get("name", ""): 
                self.available_resources[self.available_resources.index(resource)]["process"] = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                print(f"Recurso '{resource_name}' iniciado com PID {self.available_resources[self.available_resources.index(resource)]['process'].pid}")


    def init_all_resources(self):
        """
        Initialize all available resources.
        """
        for resource in self.available_resources:
            resource_name = resource.get("name", "")
            if resource_name:
                self.init_resource(resource_name)
        

    def stop_resource(self, resource_name: str):
        """
        Stops the specified resource by terminating its process.
        """
        for resource in self.available_resources:
            if resource_name == resource.get("name", ""):
                process: subprocess.Popen = resource.get("process", None)
                if process:
                    process.terminate()
                    process.wait()
                    print(f"Recurso '{resource_name}' com PID {process.pid} foi terminado.")
                else:
                    print(f"Nenhum processo ativo encontrado para o recurso '{resource_name}'.")


    def stop_all_resources(self):
        """
        Stops all running resources.
        """
        for resource in self.available_resources:
            resource_name = resource.get("name", "")
            if resource_name:
                self.stop_resource(resource_name)


    def add_resource(self, resource_name: str):
        """
        Adds a new resource to the available resources list and save in json.
        """
        self.available_resources.append({"name": resource_name, "process": None})
        self.save_config()


    def remove_resource(self, resource_name: str):
        """
        Removes a resource from the available resources list and save in json.
        """
        for resource in self.available_resources:
            if resource_name == resource.get("name", ""):
                self.available_resources.remove(resource)
                self.save_config()
                print(f"Recurso '{resource_name}' removido da lista de recursos disponíveis.")
                return
        print(f"Recurso '{resource_name}' não encontrado na lista de recursos disponíveis.")


""
if __name__ == "__main__":

    import time

    controller = ResourceController()
    controller.init_all_resources()
    time.sleep(2)
    controller.stop_all_resources()
    
    request = {
        "resource": {
            "name": "audio_player",
            "config": {
                "url": "example.com/audio.mp3"
            }
        }
    }

    controller.send_request(request)
