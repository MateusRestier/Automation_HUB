# Orquestrador de Automações (Automation HUB)

Este repositório contém o código do **Automation HUB**, um orquestrador de scripts Python projetado para agendar, executar e monitorar automações que residem em seus próprios repositórios.

O objetivo principal deste projeto é centralizar a lógica de agendamento e execução, permitindo que cada automação seja desenvolvida e mantida de forma independente, promovendo uma arquitetura modular e portátil.

---

## ✨ Funcionalidades Principais

- **Agendamento Flexível:** Configure tarefas para rodar em horários específicos, diariamente, semanalmente, mensalmente ou em dias da semana predefinidos.
- **Execução Paralela e Sequencial:** Otimiza o tempo de execução rodando scripts independentes em paralelo, enquanto garante que tarefas sensíveis (como web scraping) rodem em sequência para evitar conflitos.
- **Bloqueio em Feriados:** Evita a execução de automações em feriados, com a flexibilidade de bloquear um repositório inteiro ou apenas subpastas específicas.
- **Notificações Automáticas:** Envia relatórios de sucesso e notificações de erro por e-mail via Outlook.
- **Logging Centralizado:** Registra o output de todas as execuções, sucessos e falhas em um arquivo de log.
- **Arquitetura Portátil:** Projetado para rodar em qualquer máquina sem a necessidade de alterar caminhos no código, graças à sua estrutura de descoberta dinâmica de diretórios.

---

## 🏗️ Estrutura do Projeto

O orquestrador é dividido em módulos com responsabilidades claras:

- `main.py`: **Ponto de Entrada.** Inicia e gerencia o loop de agendamento.
- `tasks.py`: **A Lista de Tarefas.** Defina *quais* scripts devem rodar e em *qual* agendamento.
- `executor.py`: **O Motor.** Executa os scripts, gerenciando concorrência, logs e erros.
- `config.py`: **O Cérebro.** Centraliza configurações, descobre caminhos dos repositórios e gerencia bloqueio em feriados.
- `utils.py`: **Caixa de Ferramentas.** Funções de apoio, como envio de e-mails e consulta de feriados.

---

## ⚙️ Pré-requisitos

Antes de começar, garanta que você tenha os seguintes softwares instalados:

- Python 3.8+
- PIP (gerenciador de pacotes do Python)
- Microsoft Outlook (instalado e configurado na máquina que rodará o orquestrador)
- Acesso de rede ao servidor de banco de dados SQL Server onde a tabela de feriados está localizada.

---

## 🚀 Instalação e Setup

### 1. Estrutura de Diretórios

Clone o `MAT_Automation_HUB` e todos os outros repositórios de automação necessários dentro de uma única pasta "mãe". A estrutura deve ser a seguinte:

```text
Meus_Projetos/
├── MAT_Automation_HUB/      (Este repositório)
├── MAT_Automacao_Linx/
├── MAT_Fiscal_Automation_Suite/
├── MAT_ZendeskScrap/
├── ... (outros repositórios de automação)
├── PRIVATE_BAG.ENV/
└── .env
```

---

### 2. Adicionando uma Nova Automação

1. **Clone o Repositório:** Certifique-se de que o repositório da nova automação esteja na pasta "mãe".
2. **Edite `tasks.py`:** Abra o arquivo `tasks.py` no `MAT_Automation_HUB`.
3. **Adicione o Script:** Use a função `get_script_path()` para adicionar o caminho do seu script à lista de agendamento desejada.

**Exemplo:** Para adicionar um novo script diário chamado `RelatorioVendas.py` que está no repositório `MAT_Vendas_ETL`, adicione a seguinte linha na lista `scripts_daily`:

```python
scripts_daily = [
    # ... outros scripts
    get_script_path("MAT_Vendas_ETL", "RelatorioVendas.py")
]
```

---

### 3. Lógica de Feriados

Para impedir que um script seja executado em um feriado, adicione o caminho do repositório ou da subpasta à lista `PATHS_BLOCKED_ON_HOLIDAYS` no arquivo `config.py`.

**Para bloquear um repositório inteiro:**

```python
PATHS_BLOCKED_ON_HOLIDAYS = [
    "MAT_Fiscal_Automation_Suite"
]
```

**Para bloquear apenas uma subpasta:**

```python
import os
PATHS_BLOCKED_ON_HOLIDAYS = [
    os.path.join("MAT_Fiscal_Automation_Suite", "GUIAS", "BAHIA")
]
```

---

## 📬 Contato

Dúvidas, sugestões ou problemas? Abra uma issue ou entre em contato com o mantenedor do projeto.