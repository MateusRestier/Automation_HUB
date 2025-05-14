import subprocess
import os

# Obter o diretório atual do script
diretorio_atual = os.path.dirname(os.path.abspath(__file__))

# Caminho completo para a pasta "ArquivosDiarios"
caminho_pasta_diarios = os.path.join(diretorio_atual, 'ArquivosDiarios')

# Verificar se a pasta "ArquivosDiarios" existe, se não, criar a pasta
if not os.path.exists(caminho_pasta_diarios):
    try:
        os.mkdir(caminho_pasta_diarios)
        print(f'Pasta "ArquivosDiarios" criada em: {caminho_pasta_diarios}')
    except Exception as e:
        print(f'Ocorreu um erro ao criar a pasta: {e}')

# Caminho completo para o arquivo .vbs
caminho_arquivo_vbs = os.path.join(diretorio_atual, 'ExecutarMacroCMV.vbs')

# Executar o arquivo .vbs com o Windows Script Host (wscript.exe)
try:
    subprocess.run(['wscript.exe', caminho_arquivo_vbs], check=True)
    print("Script VBS executado com sucesso!")
except subprocess.CalledProcessError as e:
    print(f"Ocorreu um erro ao executar o script VBS: {e}")

# Excluir arquivos na pasta "ArquivosDiarios"
try:
    for arquivo in os.listdir(caminho_pasta_diarios):
        caminho_arquivo = os.path.join(caminho_pasta_diarios, arquivo)
        if os.path.isfile(caminho_arquivo):
            try:
                os.remove(caminho_arquivo)
                print(f"Arquivo {caminho_arquivo} excluído com sucesso!")
            except PermissionError:
                print(f"Permissão negada ao tentar excluir o arquivo {caminho_arquivo}. O arquivo pode estar em uso.")
                try:
                    # Tentar finalizar o processo que está usando o arquivo
                    result = subprocess.run(['taskkill', '/F', '/IM', 'EXCEL.EXE'], capture_output=True, text=True)
                    #if "ERRO: o processo \"EXCEL.EXE\" não foi encontrado." in result.stderr:
                        #print("O processo EXCEL.EXE não estava em execução.")
                    #else:
                        #print(f"Tarefa do Excel finalizada para liberar o arquivo {caminho_arquivo}.")
                    os.remove(caminho_arquivo)
                    print(f"Arquivo {caminho_arquivo} excluído com sucesso após finalizar a tarefa.")
                except Exception as e:
                    print(f"Ocorreu um erro ao tentar excluir o arquivo {caminho_arquivo} após finalizar a tarefa: {e}")
except Exception as e:
    print(f"Ocorreu um erro ao excluir arquivos na pasta 'ArquivosDiarios': {e}")