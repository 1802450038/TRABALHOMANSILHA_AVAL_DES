# Comparativo de Desempenho ETL: PHP vs. Java vs. Python

## Objetivo

[cite_start]Este repositório contém os scripts e dados para a "Proposta de Trabalho"  que realiza uma análise comparativa de desempenho entre PHP, Java e Python. O foco é avaliar o comportamento dessas linguagens em modos síncrono e assíncrono sob uma carga de trabalho ETL intensiva em I/O.

## Metodologia (Workload)

[cite_start]O *workload* principal, descrito na [Proposta de Trabalho (3).pdf](Proposta%20de%20Trabalho%20(3).pdf), consiste em um script de ETL que executa as seguintes etapas para mais de 100.000 registros:

1.  **Extração**: Lê um registro do arquivo `202210_PEP.csv`.
2.  **Transformação**: Para cada registro:
    * Conecta-se a um banco de dados MySQL.
    * Executa um `SELECT` na tabela `cargos` (povoada por `FUN.csv`) para obter o `id` correspondente à `Descrição_Função`.
    * Executa um `SELECT` na tabela `cidades` (povoada por `ORG.csv`) para obter o `id` correspondente ao `Nome_Órgão`.
3.  **Carga**: Insere o `CPF`, `Nome_PEP`, `cargo_id` e `cidade_id` na tabela `pessoas`.

Este processo é implementado em:
* **PHP**: Síncrono (PDO) e Assíncrono (Swoole).
* **Java**: Síncrono (JDBC) e Assíncrono (R2DBC).
* **Python**: Síncrono (mysql-connector) e Assíncrono (aiomysql).

## Análise (Caracterização do Workload)

Os scripts na pasta `/analise` são usados para analisar os dados de desempenho (tempo, CPU, memória) coletados e salvos em `resultados_workload.csv`. [cite_start]Esta análise utiliza técnicas (como Média, Clustering e PCA) discutidas na aula de "Caracterização de Workloads".

## Estrutura

* `/dados_lookup`: Contém os CSVs (`FUN.csv`, `ORG.csv`) usados para povoar o banco de dados.
* `/dados_entrada`: Contém o arquivo `202210_PEP.csv` a ser processado.
* `/scripts_etl`: Contém os scripts de *workload* (PHP, Java, Python).
* `/scripts_analise`: Contém os scripts para *caracterização* dos resultados (PCA, Média, etc.).
* `setup_database.py`: Script auxiliar para criar e popular o banco de dados.
* `resultados_workload.csv`: Arquivo-exemplo contendo os resultados das métricas de desempenho (a ser preenchido).