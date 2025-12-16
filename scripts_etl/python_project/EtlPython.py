# Requer: pip install mysql-connector-python aiomysql aiofiles pandas
import pandas as pd
import mysql.connector # Síncrono
import aiomysql # Assíncrono
import asyncio
import time
import resource # Para medir pico de memória (Linux/macOS)
import csv
import os
import sys

# --- Configurações ---
DB_CONFIG = {
    'host': 'localhost', 'user': 'root', 'password': 'C@maro13', 'db': 'trabalho_pep'
}
PEP_FILE_PATH = '../../dados_entrada/202210_PEP.csv'
RESULT_FILE_PATH = '../results/resultados_workload_py.csv'
# ---------------------

# Colunas que vamos ler do PEP.csv
PEP_COLUMNS = ['CPF', 'Nome_PEP', 'Sigla_Função', 'Descrição_Função', 'Nível_Função', 'Nome_Órgão', 'Data_Início_Exercício', 'Data_Fim_Exercício', 'Data_Fim_Carência']
COL_CPF = 'CPF'
COL_NOME = 'Nome_PEP'
COL_CARGO_DESC = 'Descrição_Função' # Para buscar em `cargos`
COL_CIDADE_NOME = 'Nome_Órgão'      # Para buscar em `cidades`


def load_pep_file(limit=None):
    # (Mesma função de carregamento da resposta anterior)
    print(f"Lendo as primeiras {limit} linhas do arquivo PEP...")
    try:
        df = pd.read_csv(PEP_FILE_PATH, encoding='latin1', sep=',', header=None, names=PEP_COLUMNS, skiprows=1, nrows=limit)
    except Exception:
        df = pd.read_csv(PEP_FILE_PATH, encoding='utf-8', sep=',', header=None, names=PEP_COLUMNS, skiprows=1, nrows=limit)
    df = df.where(pd.notnull(df), None)
    print(f"{len(df)} registros lidos.")
    return df

def save_result(language, mode, architecture, load_size, time_s, peak_mem_mb, cpu_percent):
    """Anexa o resultado da execução ao arquivo CSV mestre."""
    file_exists = os.path.isfile(RESULT_FILE_PATH)
    
    with open(RESULT_FILE_PATH, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["linguagem", "modo", "arquitetura", "carga_registros", "tempo_total_s", "pico_memoria_mb", "media_cpu_percent"])
        
        writer.writerow([language, mode, architecture, load_size, f"{time_s:.2f}", f"{peak_mem_mb:.2f}", f"{cpu_percent:.2f}"])
    print(f"Resultado salvo em {RESULT_FILE_PATH}")

# --- MODO SÍNCRONO ---
def run_sync_etl(data_rows):
    db = mysql.connector.connect(**DB_CONFIG)
    cursor = db.cursor(dictionary=True)
    insert_sql = "INSERT INTO pessoas (cpf, nome_pep, cidade_id, cargo_id) VALUES (%s, %s, %s, %s)"
    
    for _, row in data_rows.iterrows():
        # 1. Buscar ID da Cidade
        cursor.execute("SELECT id FROM cidades WHERE org_nome = %s", (row[COL_CIDADE_NOME],))
        cidade_id = (cursor.fetchone() or {}).get('id')
        
        # 2. Buscar ID do Cargo
        cursor.execute("SELECT id FROM cargos WHERE func_desc = %s", (row[COL_CARGO_DESC],))
        cargo_id = (cursor.fetchone() or {}).get('id')
        
        # 3. Inserir na tabela 'pessoas'
        cursor.execute(insert_sql, (row[COL_CPF], row[COL_NOME], cidade_id, cargo_id))
    
    db.commit()
    cursor.close()
    db.close()

# --- MODO ASSÍNCRONO ---
async def process_row_async(pool, row_data):
    cpf, nome, cargo_desc, cidade_nome = row_data
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # 1. Buscar ID da Cidade
            await cursor.execute("SELECT id FROM cidades WHERE org_nome = %s", (cidade_nome,))
            cidade_id = (await cursor.fetchone() or {}).get('id')
            
            # 2. Buscar ID do Cargo
            await cursor.execute("SELECT id FROM cargos WHERE func_desc = %s", (cargo_desc,))
            cargo_id = (await cursor.fetchone() or {}).get('id')
            
            # 3. Inserir na tabela 'pessoas'
            insert_sql = "INSERT INTO pessoas (cpf, nome_pep, cidade_id, cargo_id) VALUES (%s, %s, %s, %s)"
            await cursor.execute(insert_sql, (cpf, nome, cidade_id, cargo_id))
            await conn.commit()

async def run_async_etl(data_rows):
    pool = await aiomysql.create_pool(**DB_CONFIG)
    tasks = []
    for _, row in data_rows.iterrows():
        task_data = (row[COL_CPF], row[COL_NOME], row[COL_CARGO_DESC], row[COL_CIDADE_NOME])
        tasks.append(process_row_async(pool, task_data))
    
    await asyncio.gather(*tasks)
    pool.close()
    await pool.wait_closed()

# --- Execução Principal ---
if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Uso: python etl_python.py [sync|async] [limite_registros] [arquitetura] [cpu_medida]")
        print("Ex: python etl_python.py async 10000 intel 45.5")
        sys.exit(1)

    MODE = sys.argv[1]
    LIMIT = int(sys.argv[2])
    ARCH = sys.argv[3]
    CPU_PERCENT = float(sys.argv[4]) # Medição de CPU é complexa, melhor passar como argumento vindo de uma ferramenta externa como 'time' ou 'htop'

    # 1. Carregar dados
    pep_data = load_pep_file(limit=LIMIT)
    
    # 2. Executar e Medir
    start_time = time.time()
    
    if MODE == 'sync':
        print(f"\n--- Iniciando ETL Síncrono (Python) para {LIMIT} registros ---")
        run_sync_etl(pep_data)
    elif MODE == 'async':
        print(f"\n--- Iniciando ETL Assíncrono (Python) para {LIMIT} registros ---")
        asyncio.run(run_async_etl(pep_data))
    else:
        print(f"Modo '{MODE}' desconhecido. Use 'sync' ou 'async'.")
        sys.exit(1)
        
    end_time = time.time()
    total_time_s = end_time - start_time
    
    # Medir Pico de Memória (em MB)
    # resource.getrusage() retorna em Kilobytes no Linux
    peak_mem_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    peak_mem_mb = peak_mem_kb / 1024.0
    
    print(f"--- Concluído em {total_time_s:.2f} segundos ---")
    print(f"--- Pico de Memória: {peak_mem_mb:.2f} MB ---")

    # 3. Salvar resultados
    save_result("python", MODE, ARCH, LIMIT, total_time_s, peak_mem_mb, CPU_PERCENT)
