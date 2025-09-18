from config import get_script_path

"""
Este módulo define as listas de scripts que devem ser executados
em diferentes agendamentos, usando a estrutura de múltiplos repositórios.
"""

scripts_daily = [ # Roda todos os dias 
    get_script_path("MAT_Logistics_Tracking_ETL", "UpdateAcompNacional.py"),
    get_script_path("MAT_ZendeskScrap", "ScrapTicketAtribuicao_D-1.py"),
    get_script_path("MAT_ZendeskScrap", "ScrapCriadosResolvidos_D-1.py"),
    get_script_path("MAT_Fiscal_Automation_Suite", "PROD", "FiscalProdAnalyzer.py"),
    get_script_path("MAT_ZendeskScrap", "tickets.py"),
    get_script_path("MAT_ZendeskScrap", "activities.py"),
    get_script_path("MAT_Automacao_Linx", "Scraplinx.py"),
]

scripts_daily_4 = [ # scripts executados 4x ao dia
    get_script_path("MAT_AutomacaoFeriasRH", "processar_email_ferias.py")
]

scripts_itau = [ # scripts_itau executados todos os dias às 11h
    get_script_path("MAT_REDE_Financial_ETL", "VendasRede-Diario.py"),
    get_script_path("MAT_REDE_Financial_ETL", "PagamentosConsolidados-Diario.py"),
    get_script_path("MAT_REDE_Financial_ETL", "RecebiveisSemanal-Diario.py"),
    get_script_path("MAT_REDE_Financial_ETL", "RecebiveisMensal.py")
]

scripts_monthly = [ # Roda no primeiro dia do mês
    get_script_path("MAT_REDE_Financial_ETL", "VendasRede-MesAnterior.py")
]

scripts_weekly = [ # Roda uma vez por semana, toda segunda feira
    get_script_path("MAT_ZendeskScrap", "ScrapTicketAtribuicao_S-1.py"),
    get_script_path("MAT_ZendeskScrap", "ScrapCriadosResolvidos_S-1.py")
]

scripts_weekdays = [ # Roda de seg a sexta
    get_script_path("MAT_Fiscal_Automation_Suite", "GUIAS", "BAHIA", "ScrapAutomacaoBahia.py"),
]

scripts_monday_thursday = [ # Executa apenas nas terças e quintas

]

scripts_mon_wed_fri = [ # Executa apenas nas segundas, quartas e sextas
    get_script_path("MAT_Fiscal_Automation_Suite", "GUIAS", "ALAGOAS", "ScrapAutomacaoAlagoas.py")
]