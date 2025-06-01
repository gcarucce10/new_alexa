import json
import os

def build_prompt() -> None:
    
    path_tofile = os.path.join("server_config.json")

    with open(path_tofile, 'r', encoding='utf-8') as f:
                jsonData: dict = json.load(f)

    arquivos_entrada: list[str] = []

    path_tofile = os.path.join("", "prompts", "begin.txt")
    arquivos_entrada.append(path_tofile)

    for action in jsonData.get("active_actions", []):
        path_tofile = os.path.join("Actions", action, "description.txt")
        arquivos_entrada.append(path_tofile)

    path_tofile = os.path.join("", "prompts", "end.txt")
    arquivos_entrada.append(path_tofile)


    # Define o nome do arquivo de saída
    arquivo_saida= os.path.join("", "prompts", "Current_Prompt.txt")

    # Abre o arquivo de saída no modo de escrita ('w')
    with open(arquivo_saida, 'w', encoding='utf-8') as outfile:
        # Itera sobre cada arquivo de entrada encontrado
        for nome_arquivo in arquivos_entrada:
            # Abre cada arquivo de entrada no modo de leitura ('r')
            with open(nome_arquivo, 'r', encoding='utf-8') as infile:
                # Lê o conteúdo do arquivo de entrada e o escreve no arquivo de saída
                outfile.write(infile.read())
                # Adiciona uma quebra de linha entre os conteúdos dos arquivos (opcional)
                outfile.write('\n') # Remova esta linha se não quiser uma quebra de linha extra

