import os
import subprocess
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from utils import send_error_email, is_today_holiday
from config import block_on_holidays_dirs

"""
Este módulo contém o 'motor' do orquestrador, responsável por
executar os scripts, seja em paralelo ou sequencialmente.
"""

def execute_script(script):
    start_time = time.time()
    try:
        logging.info(f"Executando: {script}")
        result = subprocess.run(
            ["python", script], 
            check=True, 
            capture_output=True, 
            text=True, 
            encoding='utf-8', 
            errors='replace',
            env={**os.environ, "PYTHONIOENCODING": "utf-8"}
        )
        logging.info(result.stdout)
        if result.stderr:
            logging.error(result.stderr)
        
        logging.info(f"Concluído: {script}")
        return script, True, time.time() - start_time
    except subprocess.CalledProcessError as e:
        error_message = f"Erro (CalledProcessError) em {script}:\nOutput: {e.output}\nError: {e.stderr}"
        logging.error(error_message)
        send_error_email(os.path.basename(script), error_message)
        return script, False, time.time() - start_time
    except Exception as e:
        error_message = f"Erro inesperado em {script}:\n{str(e)}"
        logging.error(error_message)
        send_error_email(os.path.basename(script), error_message)
        return script, False, time.time() - start_time

def execute_scripts_concurrently(scripts, max_workers=3):
    if not scripts:
        return [], 0

    if is_today_holiday():
        scripts = [
            s for s in scripts
            if not any(os.path.commonpath([s, blocked_dir]) == blocked_dir for blocked_dir in block_on_holidays_dirs)
        ]
        logging.info(f"Hoje é feriado. Scripts de diretórios bloqueados não serão executados.")

    sequential_scripts = [s for s in scripts if 'scrap' in os.path.basename(s).lower()]
    parallel_scripts = [s for s in scripts if s not in sequential_scripts]

    successful_scripts = []
    start_time = time.time()

    if parallel_scripts:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(execute_script, script) for script in parallel_scripts}
            for future in as_completed(futures):
                script, success, exec_time = future.result()
                if success:
                    successful_scripts.append((script, exec_time))

    for script in sequential_scripts:
        _script, success, exec_time = execute_script(script)
        if success:
            successful_scripts.append((script, exec_time))

    total_time = time.time() - start_time
    return successful_scripts, total_time