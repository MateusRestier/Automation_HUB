import os
import pyodbc
import pythoncom
import logging
from datetime import datetime
from win32com.client import Dispatch
from config import log_file # Importa o log_file do config.py

"""
Este módulo contém funções de utilidade usadas em todo o projeto.
"""

def get_sql_connection():
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={os.getenv('DB_SERVER_EXCEL')},{os.getenv('DB_PORT_EXCEL')};"
        f"DATABASE={os.getenv('DB_DATABASE_EXCEL')};"
        f"UID={os.getenv('DB_USER_EXCEL')};"
        f"PWD={os.getenv('DB_PASSWORD_EXCEL')};"
    )
    return pyodbc.connect(conn_str)

def is_today_holiday():
    today_str = datetime.today().strftime('%Y-%m-%d')
    try:
        conn = get_sql_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(1) FROM dbo.feriados_rj WHERE CONVERT(DATE, data) = ?", today_str)
        result = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return result > 0
    except Exception as e:
        logging.error(f"Falha ao verificar feriado no banco de dados: {e}")
        return False # Assume que não é feriado se houver falha na consulta

def send_error_email(script_name, error_message):
    try:
        pythoncom.CoInitialize()
        outlook = Dispatch("Outlook.Application")
        mail = outlook.CreateItem(0)
        mail.To = "mateus.restier@bagaggio.com.br"
        mail.Subject = f"AUTOMÁTICO: ERRO AO EXECUTAR SCRIPT \"{script_name}\""
        mail.Body = (
            f"Olá,\n\nOcorreu um erro ao executar o script: {script_name}\n\n"
            f"Detalhes do erro:\n\n{error_message}\n\n"
            f"Por favor, verifique.\n\nAtenciosamente,\nAutomação"
        )
        mail.Send()
        print(f"E-mail enviado para notificar o erro no script: {script_name}")
    except Exception as e:
        print(f"Falha ao enviar e-mail de erro: {e}")
    finally:
        pythoncom.CoUninitialize()
    logging.error(f"Erro ao executar {script_name}: {error_message}")

def send_success_email(successful_scripts, total_time):
    try:
        pythoncom.CoInitialize()
        outlook = Dispatch("Outlook.Application")
        mail = outlook.CreateItem(0)
        mail.To = "mateus.restier@bagaggio.com.br"
        mail.Subject = "AUTOMÁTICO: RELATÓRIO DE EXECUÇÃO DE SCRIPTS"
        
        scripts_body = "\n".join([f'{os.path.basename(script)} - {time:.2f} segundos' for script, time in successful_scripts])
        
        mail.Body = (
            f"Olá,\n\nOs seguintes scripts foram executados com sucesso:\n\n"
            f"{scripts_body}\n\n"
            f"Tempo total de execução: {total_time:.2f} segundos\n\n"
            f"Atenciosamente,\nAutomação"
        )
        mail.Attachments.Add(log_file)
        mail.Send()
        print("E-mail enviado com o relatório de sucesso.")
    except Exception as e:
        print(f"Falha ao enviar e-mail de sucesso: {e}")
    finally:
        pythoncom.CoUninitialize()
        logging.shutdown()
        # Limpa o arquivo de log para a próxima execução
        if os.path.exists(log_file):
            open(log_file, 'w').close()