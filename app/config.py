# config.py
import os
import logging
from dotenv import load_dotenv
from pathlib import Path

"""
Este módulo centraliza todas as configurações do projeto de forma dinâmica e portátil.
"""

# --- Carregamento de Variáveis de Ambiente ---
def localizar_env(diretorio_raiz="PRIVATE_BAG.ENV"):
    path = Path(__file__).resolve()
    for parent in path.parents:
        possible = parent / diretorio_raiz / ".env"
        if possible.exists():
            return possible
    raise FileNotFoundError(f"Arquivo .env não encontrado na pasta '{diretorio_raiz}'.")

env_path = localizar_env()
load_dotenv(dotenv_path=env_path)


# --- Definição Dinâmica de Caminhos ---
AUTOMATIONS_BASE_DIR = Path(__file__).resolve().parents[2]

def get_script_path(repo_name, *path_parts):
    """
    Monta o caminho completo para um script, permitindo subdiretórios.
    """
    return os.path.join(AUTOMATIONS_BASE_DIR, repo_name, *path_parts)


# --- Definição de Caminhos para Bloqueio em Feriados ---
PATHS_BLOCKED_ON_HOLIDAYS = [
    os.path.join("MAT_Fiscal_Automation_Suite", "GUIAS", "BAHIA"),
    os.path.join("MAT_Fiscal_Automation_Suite", "GUIAS", "ALAGOAS"),
]

block_on_holidays_dirs = [os.path.join(AUTOMATIONS_BASE_DIR, path) for path in PATHS_BLOCKED_ON_HOLIDAYS]

# --- Configuração do Logger ---
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log_file = os.path.join(base_dir, "execution_log.txt")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)