# Comparativo de Desempenho ETL: PHP vs. Java vs. Python

## Objetivo

Este repositório contém os scripts e dados para a "Proposta de Trabalho" que realiza uma análise comparativa de desempenho entre PHP, Java e Python, com foco em operações síncronas e assíncronas.

O Objetivo é avaliar e comparar o Throughput (Requisições por Segundo) e a Latência de aplicações desenvolvidas em PHP, Node.js e Python, contrastando suas implementações tradicionais (Síncronas/Single-Thread) com suas implementações modernas de alta performance (Assíncronas/Multi-Workers).

## Requerimentos
PHP 8.3
    -> Executar scripts php.
Swoole 
    -> Extensão para tornar php assincrono.
Composer
    -> Instalar dependencias do PHP.
NodeJs 
    -> Servidor JavaScript.
NPM
    -> Instalar dependencias node.
Python 
    -> Executar Python.
Glances 
    -> pip install glances 
    -> Monitorar as atividades.
    -> Para salvar relatorios automaticamente, 
        execute :  glances --export csv --export-csv-file ./relatorio.csv
Tmux 
    -> Para gerenciar e visualizar o terminal em janelas divididas de acesso ssh.
Worker
    -> Para simular cargas de trabalhos com diferentes threads.

## Executando o projeto


### Subindo os sevidores
Após clonar o projeto em uma janela do tmux navegue até o diretório de cada linguagem e exevute o script assincrono ou sincrono para cada uma das linguagens a partir dos seguintes comandos.

PHP -> Será ser executado na porta 8081
    Sincrono :  php -S localhost:8081 phpsync.php
    Assincrono : php phpasync.php

JS -> Será executado na porta 8082
    Sincrono : node jssync.js
    Assincrono :node jsasync.js
    
PYTHON -> Será executado na porta 8083
    Sincrono : python3 pythonsync.py
    Assincrono : uvicorn pythonasync:app --host 127.0.0.1 --port 8083 --workers 32

### Executando os Workers
PHP 
 -> wrk -t32 -c100 -d10s http://127.0.0.1:8081
JS
 -> wrk -t32 -c100 -d10s http://127.0.0.1:8083
PYTHON
 -> wrk -t32 -c100 -d10s http://127.0.0.1:8083