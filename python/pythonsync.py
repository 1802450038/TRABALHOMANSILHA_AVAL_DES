# pythonsync.py
# Framework: Flask (Padrão WSGI Síncrono)
# Instalar: pip install flask

from flask import Flask, jsonify
import json
import os

app = Flask(__name__)

# Rota padrão síncrona
@app.route('/')
def root():
    try:
        # 1. Leitura Síncrona/Bloqueante
        # O processo Python trava aqui até o arquivo ser lido do disco
        # Não usamos 'async with', apenas o 'with' padrão
        with open('posts.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 2. Processamento
        items = []
        for item in data:
            items.append({
                'id': item['id'],
                'title': item['title'].upper()
            })
            
        return jsonify(items)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    # Rodando com o servidor de desenvolvimento do Flask (Single Threaded por padrão na maioria dos contextos de teste simples)
    print("Servidor Python (Flask) Síncrono rodando na porta 8083...")
    app.run(host="127.0.0.1", port=8083, debug=False)


    # Comando para rodar (No terminal):
    # python3 pythonsync.py