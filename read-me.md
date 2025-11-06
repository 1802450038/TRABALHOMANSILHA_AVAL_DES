# Comparativo de Desempenho ETL: PHP vs. Java vs. Python

## Objetivo

Este repositório contém os scripts e dados para a "Proposta de Trabalho" que realiza uma análise comparativa de desempenho entre PHP, Java e Python, com foco em operações síncronas e assíncronas.

O objetivo é executar um *workload* de ETL idêntico em cada linguagem, medir o desempenho (tempo, memória, CPU) e, em seguida, analisar os resultados coletados.

## Fluxo de Trabalho

O processo é dividido em duas fases:

**Fase 1: Execução do Workload (Coleta de Dados)**
1.  Use o script `setup_database.py` para criar o banco de dados e popular as tabelas de *lookup* (`cargos`, `cidades`) com os dados de `FUN.csv` e `ORG.csv`.
2.  Execute os scripts de ETL encontrados na pasta `/scripts_etl` (ex: `etl_python.py`, `etl_php.php`).
3.  **Cada script de ETL é responsável por:**
    * Executar a tarefa de ETL (ler `202210_PEP.csv`, consultar o DB, inserir em `pessoas`).
    * Medir o próprio tempo de execução e o pico de uso de memória.
    * Anexar uma nova linha com esses resultados ao arquivo `resultados_workload.csv`.

**Fase 2: Análise dos Resultados (Caracterização do Workload)**
1.  Após executar *todos* os testes (diferentes linguagens, modos, arquiteturas), o arquivo `resultados_workload.csv` estará completo.
2.  Execute o script de análise em Python (`scripts_analise/analise_workload.py`).
3.  Este script lerá o `resultados_workload.csv` e aplicará as técnicas de caracterização (Média, K-Means Clustering, PCA) para analisar os dados e gerar *insights*.

## Estrutura do Repositório

* `/dados_lookup`: Contém `FUN.csv` e `ORG.csv` para popular o DB.
* `/dados_entrada`: Contém o arquivo `202210_PEP.csv` a ser processado.
* `/scripts_etl`: (Fase 1) Scripts de *workload* (PHP, Java, Python) que executam a tarefa e salvam seus resultados.
* `/saida_esperada`: Contém o arquivo `RESALL.csv` resultado esperado.
* `/scripts_analise`: (Fase 2) Script Python que analisa os resultados coletados.
* `setup_database.py`: (Pré-requisito) Script para preparar o ambiente do banco de dados.
* `resultados_workload.csv`: (Arquivo de Saída) O arquivo mestre onde *todos* os scripts de ETL anexam seus resultados.
* `requirements.txt`: Dependências Python (para *ambas* as fases).