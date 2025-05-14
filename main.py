import os
import subprocess
import time
from datetime import datetime
from win32com.client import Dispatch
from concurrent.futures import ThreadPoolExecutor, as_completed
import pythoncom
import schedule 
import logging

# Obtém o diretório onde o script atual está localizado
base_dir = os.path.dirname(os.path.abspath(__file__))

# Define os diretórios relativos
prod_dir = os.path.join(base_dir, "PROD")
cmv_dir = os.path.join(base_dir, "CMV")
cd_dir = os.path.join(base_dir, "CD")
zen_dir = os.path.join(base_dir, "ZEN")
bahia_dir = os.path.join(base_dir, "FISCAL", "BAHIA")

# Configura o logger
log_file = os.path.join(base_dir, "execution_log.txt")
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Lista de scripts diários, mensais e semanais

scripts_daily = [ # Roda todos os dias 
    os.path.join(cd_dir, "UpdateAcompNacional.py"),
    os.path.join(zen_dir, "ScrapTicketAtribuicao_D-1.py"),
    os.path.join(zen_dir, "ScrapCriadosResolvidos_D-1.py"),
    os.path.join(cmv_dir, "AutomacaoCMV.py"),
    os.path.join(prod_dir, "imap_and_pop_connection.py"),
    os.path.join(zen_dir, "tickets.py"),
    os.path.join(zen_dir, "activities.py"),
]

scripts_monthly = [ # Roda no primeiro dia do mês
    
]

scripts_weekly = [ # Roda uma vez por semana, toda segunda feira
    os.path.join(zen_dir, "ScrapTicketAtribuicao_S-1.py"),
    os.path.join(zen_dir, "ScrapCriadosResolvidos_S-1.py")
]

scripts_weekdays = [ # Roda de seg a sexta
    os.path.join(bahia_dir, "ScrapAutomacao.py")
]

# Função para enviar e-mails em caso de erro
def send_error_email(script_name, error_message):
    try:
        pythoncom.CoInitialize()  # Inicializa a COM
        outlook = Dispatch("Outlook.Application")
        mail = outlook.CreateItem(0)  # 0 é o código para e-mails
        #mail.To = "mateus.restier@bagaggio.com.br"
        mail.To = "mateus.restier@bagaggio.com.br; elton.marinho@bagaggio.com.br"
        mail.Subject = f"AUTOMÁTICO: ERRO AO EXECUTAR SCRIPT \"{script_name}\""
        mail.Body = (
            f"Olá,\n\n"
            f"Ocorreu um erro ao executar o script: {script_name}\n\n"
            f"Detalhes do erro:\n\n"
            f"{error_message}\n\n"
            f"Por favor, verifique.\n\n"
            f"Atenciosamente,\n"
            f"Automação"
        )
        mail.Send()
        print(f"E-mail enviado para notificar o erro no script: {script_name}")
    except Exception as e:
        print(f"Falha ao enviar e-mail de erro: {e}")
    finally:
        pythoncom.CoUninitialize()  # Desinicializa a COM
    logging.error(f"Erro ao executar {script_name}: {error_message}")


# Função para enviar e-mails de relatório de sucesso
def send_success_email(successful_scripts, total_time):
    try:
        pythoncom.CoInitialize()  # Inicializa a COM
        outlook = Dispatch("Outlook.Application")
        mail = outlook.CreateItem(0)  # 0 é o código para e-mails
        #mail.To = "mateus.restier@bagaggio.com.br"
        mail.To = "mateus.restier@bagaggio.com.br; elton.marinho@bagaggio.com.br"
        mail.Subject = "AUTOMÁTICO: RELATÓRIO DE EXECUÇÃO DE SCRIPTS"
        mail.Body = (
            f"Olá,\n\n"
            f"Os seguintes scripts foram executados com sucesso:\n\n"
            f"{chr(10).join([f'{script} - {time:.2f} segundos' for script, time in successful_scripts])}\n\n"
            f"Tempo total de execução: {total_time:.2f} segundos\n\n"
            f"Atenciosamente,\n"
            f"Automação"
        )
        # Anexa o arquivo de log
        attachment = mail.Attachments.Add(log_file)
        attachment.PropertyAccessor.SetProperty("http://schemas.microsoft.com/mapi/proptag/0x3712001F", "execution_log.txt")
        mail.Send()
        print("E-mail enviado com o relatório de sucesso.")
    except Exception as e:
        print(f"Falha ao enviar e-mail de sucesso: {e}")
    finally:
        pythoncom.CoUninitialize()  # Desinicializa a COM
        # Limpa o arquivo de log após o envio do e-mail
        logging.shutdown()
        open(log_file, 'w').close()


def execute_script(script, check_excel_outlook=False):
    """Executa um script individualmente."""

    start_time = time.time()
    try:
        print(f"Executando: {script}")
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
        print(result.stdout)
        logging.info(result.stdout)
        if result.stderr:
            print(result.stderr)
            logging.error(result.stderr)
            send_error_email(script, result.stderr)
            return False, time.time() - start_time
        print(f"Concluído: {script}")
        logging.info(f"Concluído: {script}")
        return True, time.time() - start_time
    except subprocess.CalledProcessError as e:
        error_message = (
            f"Erro ao executar {script}:\n"
            f"Return code: {e.returncode}\n"
            f"Output: {e.output}\n"
            f"Error: {e.stderr}\n"
        )
        print(error_message)
        logging.error(error_message)
        send_error_email(script, error_message)
    except FileNotFoundError as e:
        error_message = f"Arquivo não encontrado: {script}\nErro: {str(e)}"
        print(error_message)
        logging.error(error_message)
        send_error_email(script, error_message)
    except Exception as e:
        error_message = f"Erro inesperado ao executar {script}:\n{str(e)}"
        print(error_message)
        logging.error(error_message)
        send_error_email(script, error_message)
    return False, time.time() - start_time

def execute_scripts_concurrently(scripts, check_excel_outlook=False, max_workers=3):
    """Executa múltiplos scripts. Scripts com 'Scrap' no nome são executados em série."""

    # Separa scripts com 'Scrap' no nome (case-insensitive)
    sequential_scripts = [s for s in scripts if 'scrap' in os.path.basename(s).lower()]
    parallel_scripts = [s for s in scripts if s not in sequential_scripts]

    successful_scripts = []
    start_time = time.time()

    # Executa scripts em paralelo (os que não são "Scrap")
    if parallel_scripts:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(execute_script, script, check_excel_outlook): script for script in parallel_scripts}
            for future in as_completed(futures):
                script = futures[future]
                try:
                    success, exec_time = future.result()
                    if success:
                        successful_scripts.append((script, exec_time))
                except Exception as e:
                    print(f"Erro ao executar o script {script}: {e}")
                    logging.error(f"Erro ao executar o script {script}: {e}")

    # Executa scripts sequencialmente (os que são "Scrap")
    for script in sequential_scripts:
        success, exec_time = execute_script(script, check_excel_outlook)
        if success:
            successful_scripts.append((script, exec_time))

    total_time = time.time() - start_time
    logging.info("Todos os scripts foram executados.")
    send_success_email(successful_scripts, total_time)


# Função para executar os scripts com base na data atual
def run_scripts():
    today = datetime.today()
    is_first_of_month = today.day == 1
    is_monday = today.weekday() == 0
    is_weekday = today.weekday() < 5  # Segunda (0) até sexta (4)

    # Executa scripts diários
    execute_scripts_concurrently(scripts_daily, check_excel_outlook=True)

    # Executa scripts semanais apenas às segundas-feiras
    if is_monday:
        execute_scripts_concurrently(scripts_weekly)

    # Executa scripts mensais apenas no dia 1º do mês
    if is_first_of_month:
        execute_scripts_concurrently(scripts_monthly)

    # Executa scripts de segunda a sexta
    if is_weekday:
        execute_scripts_concurrently(scripts_weekdays)

    print("Todos os scripts foram executados com sucesso.")


# Agenda a execução diária às 06:00
schedule.every().day.at("06:01").do(run_scripts)

# Mantém o script em execução para verificar os agendamentos
while True:
    schedule.run_pending()
    time.sleep(1)


'''if __name__ == "__main__":
    run_scripts()'''