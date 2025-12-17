# 3. Python (FastAPI + Uvicorn)

# pip install fastapi uvicorn aiofiles

# No Python, você não muda o código do arquivo server_async.py. Quem gerencia os workers é o Uvicorn (o programa que roda o servidor).
# Em vez de rodar com python server_async.py, você deve usar o comando direto do uvicorn no terminal, passando a flag --workers.

# Comando para rodar (No terminal):

# Bash

    # uvicorn async:app --host 127.0.0.1 --port 8083 --workers 4

# async: É o nome do seu arquivo (sem o .py).

# app: É o nome da variável FastAPI() dentro do script.

# --workers 4: Cria 4 processos simultâneos.

import json
import aiofiles
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    # 'async with' garante que a leitura do arquivo não trave o servidor
    async with aiofiles.open('posts.json', mode='r') as f:
        content = await f.read()
    
    data = json.loads(content)
    
    # Processamento
    items = []
    for item in data:
        items.append({
            'id': item['id'],
            'title': item['title'].upper()
        })
        
    return items

if __name__ == "__main__":
    # Workers = 1 para ser justo na comparação de thread única com Node, 
    # mas em produção você usaria mais.
    uvicorn.run(app, host="127.0.0.1", port=8083, log_level="warning")