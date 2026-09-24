# Controle de Orçamentos · Novemp

Aplicativo desktop para registrar e acompanhar orçamentos técnicos do dia a dia: data, vendedor responsável, número da PFN, cliente, obra, status e observações.

Criado para organizar o fluxo de orçamentos recebidos de múltiplos vendedores, evitando planilhas soltas e informações perdidas.

## ✨ Funcionalidades

- Cadastro de orçamentos com data, vendedor, nº PFN, cliente, obra, descrição e status
- Campo de cliente com autocomplete (sugere clientes já cadastrados antes)
- Filtros por vendedor e por status
- Edição e exclusão de registros direto na tabela
- Interface escura, minimalista
- Dados salvos automaticamente em banco local (SQLite) — sem depender de internet ou planilha compartilhada

## 🛠️ Tecnologias

- **Python 3**
- **PyQt5** — interface gráfica
- **SQLite** — persistência local dos dados

## 🚀 Como rodar

Pré-requisitos: Python 3 instalado.

```bash
pip install PyQt5
python controle_orcamentos.py
```

O programa cria automaticamente um arquivo `orcamentos.db` na mesma pasta na primeira execução — é onde os dados ficam salvos.

## 📌 Status do projeto

Em uso interno e evolução contínua, conforme novas necessidades do dia a dia surgem.

## 👤 Autor

Vinicius Luque Parente — Engenharia aplicada a painéis elétricos e barramentos blindados, cursando Análise e Desenvolvimento de Sistemas.
