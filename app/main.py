import time
import schedule
from datetime import datetime

# Importa as funções e listas dos outros módulos
from executor import execute_scripts_concurrently
from utils import send_success_email
from tasks import (
    scripts_daily, scripts_daily_4, scripts_itau, scripts_monthly,
    scripts_weekly, scripts_weekdays, scripts_monday_thursday, scripts_mon_wed_fri
)

"""
Ponto de entrada do orquestrador.
Este módulo é responsável por configurar e executar os agendamentos.
"""

def run_main_schedule():
    """Executa os scripts diários e os que correspondem ao dia atual."""
    print("Iniciando verificação de agendamento principal (04:00)...")
    today = datetime.today()
    weekday = today.weekday()

    schedule_map = [
        (True, scripts_daily),
        (today.day == 1, scripts_monthly),
        (weekday == 0, scripts_weekly),
        (weekday < 5, scripts_weekdays),
        (weekday in [0, 3], scripts_monday_thursday),
        (weekday in [0, 2, 4], scripts_mon_wed_fri),
    ]

    all_successful_scripts = []
    total_execution_time = 0

    for condition, script_list in schedule_map:
        if condition and script_list:
            successful, total_time = execute_scripts_concurrently(script_list)
            all_successful_scripts.extend(successful)
            total_execution_time += total_time
    
    if all_successful_scripts:
        send_success_email(all_successful_scripts, total_execution_time)
    print("Verificação de agendamento principal concluída.")


def run_specific_schedule(scripts_to_run):
    """Função genérica para rodar uma lista específica de scripts."""
    print(f"Executando agendamento específico...")
    successful, total_time = execute_scripts_concurrently(scripts_to_run)
    if successful:
        send_success_email(successful, total_time)
    print("Agendamento específico concluído.")


def setup_schedules():
    """Configura todos os agendamentos."""
    schedule.every().day.at("04:00").do(run_main_schedule)
    
    # Agendamentos para scripts_daily_4
    schedule.every().day.at("06:00").do(run_specific_schedule, scripts_daily_4)
    schedule.every().day.at("12:00").do(run_specific_schedule, scripts_daily_4)
    schedule.every().day.at("15:00").do(run_specific_schedule, scripts_daily_4)
    schedule.every().day.at("17:00").do(run_specific_schedule, scripts_daily_4)

    # Agendamento para scripts_itau
    schedule.every().day.at("11:00").do(run_specific_schedule, scripts_itau)
    
    print("Agendamentos configurados. O orquestrador está em execução.")


def run_all_tasks_immediately():
    """Executa todos os grupos de tarefas de uma vez, para fins de teste."""
    
    run_main_schedule() # Roda os scripts diários, mensais, semanais, etc.
    
    run_specific_schedule(scripts_daily_4) # Roda os scripts que executam 4x ao dia
    
    run_specific_schedule(scripts_itau) # Roda os scripts do Itaú


def main():
    run_immediately = False  # Mude para True para testar sem esperar o agendamento

    if run_immediately:
        run_all_tasks_immediately()
    else:
        setup_schedules()
        while True:
            schedule.run_pending()
            time.sleep(1)


if __name__ == "__main__":
    main()