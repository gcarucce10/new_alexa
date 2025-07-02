import json
import sys
import os
import subprocess

actions_data_path = os.path.join("Actions","actions_data.json")

with open(actions_data_path, 'r', encoding='utf-8') as f:
            jsonData: dict = json.load(f)



class Connector:

    def __init__(self, comands: list[str], jsonData: dict = None, where_exec: str = "server", parallel: bool = False) -> None:

        self.action = comands[0]

        jsonList = jsonData.get("actions", {})

        for action in jsonList:
            if action.get("name") == self.action:
                self.server_exec = action.get("execution").get("server")
                self.client_exec = action.get("execution").get("client")
                self.fileType = action.get("fileType", "python-script")
                self.fileExtension = action.get("file_extension", "")
                self.wait = action.get("parallel", False)
                break

        self.where_exec = where_exec       

        print(f"Tipo de arquivo: {self.fileType}")
        self.params: list[str]  = comands[1:]

        self.command: str = self.build_command()

        if parallel:
            self.wait = parallel

    def build_command(self) -> list[str]:
        """
        Constrói o comando a ser executado com base nos parâmetros fornecidos.
        """

        absolute_dir: str = os.path.dirname(os.path.abspath(__file__))
        path_tofile = os.path.join(absolute_dir, self.action)

        filename = f"{self.action}{self.fileExtension}"

        if self.fileType == "python-script":
            command = [sys.executable] 
        else:   
            # Para outros tipos de arquivo, apenas junta os parâmetros
            if os.name == 'linux' or os.name == 'darwin':
                path_tofile = os.path.join(".", path_tofile)

            command = []
            
        path_tofile = os.path.join(path_tofile, filename)
        command.append(path_tofile)
        command.extend(self.params)

        print(f"Caminho do programa a ser executado é : {path_tofile}")

        return command
        
    def can_execute(self) -> bool:
        """
        Verifica se o comando pode ser executado com base no tipo de execução (servidor ou cliente).
        """
        if self.where_exec == "server" and not self.server_exec:
            print(f"Ação '{self.action}' não pode ser executada no servidor.")
            return False
        elif self.where_exec == "client" and not self.client_exec:
            print(f"Ação '{self.action}' não pode ser executada no cliente.")
            return False
        return True    

    def run_program(self):

        if (not self.can_execute()):
            print(f"Não é possível executar a ação '{self.action}' no ambiente atual.")
            return False
            
        print(f"Tentando executar: {' '.join(self.command)}") # Para depuração

        try:
            # capture_output=True para pegar stdout e stderr
            # text=True para decodificar a saída como string
            # check=False (por enquanto) para que não levante erro e possamos inspecionar

            # Se a ação deve ocorrer em paralelo, usamos Popen, senão usamos run
            if self.wait:
                self.resultado = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            else:
                self.resultado = subprocess.run(self.command, capture_output=True, text=True, check=False)

            print(f"Código de Saída: {self.resultado.returncode}")

            if self.resultado.stdout:
                print("Saída Padrão (stdout):")
                print(self.resultado.stdout)

            if self.resultado.stderr:
                print("Saída de Erro (stderr):")
                print(self.resultado.stderr) # Erros do list-manager.py aparecerão aqui

            return True

        except FileNotFoundError:
            print(f"Erro: O executável não foi encontrado.")
            print("Verifique se o caminho foi especificado corretamente.")
            return False
        except Exception as e:
            print(f"Ocorreu uma exceção inesperada: {e}")
            return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python actions_connector.py '<comando e parametros>' ")
        sys.exit(1)
    
    commands = sys.argv[1:]

    connector = Connector(commands, jsonData)
    connector.run_program()
