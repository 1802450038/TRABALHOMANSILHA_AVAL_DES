import pandas as pd
import mysql.connector
import sys

# --- Configurações do Banco de Dados ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'seu_password_aqui'
}
DB_NAME = 'trabalho_pep'
# -------------------------------------

def create_database():
    """Cria o banco de dados e as tabelas principais."""
    try:
        # Conecta sem banco selecionado para criar o DB
        db = mysql.connector.connect(**DB_CONFIG)
        cursor = db.cursor()
        
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} DEFAULT CHARACTER SET utf8mb4")
        print(f"Banco de dados '{DB_NAME}' garantido.")
        cursor.execute(f"USE {DB_NAME}")

        # --- Criar Tabela Cidades (de ORG.csv) ---
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cidades (
            id INT AUTO_INCREMENT PRIMARY KEY,
            org_nome VARCHAR(255) NOT NULL,
            UNIQUE KEY (org_nome)
        ) ENGINE=InnoDB;
        """)
        print("Tabela 'cidades' criada.")

        # --- Criar Tabela Cargos (de FUN.csv) ---
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cargos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            func_sigla VARCHAR(50),
            func_desc VARCHAR(255),
            func_nivel VARCHAR(50),
            UNIQUE KEY (func_desc)
        ) ENGINE=InnoDB;
        """)
        print("Tabela 'cargos' criada.")
        
        # --- Criar Tabela Pessoas (Onde os dados serão inseridos) ---
        #
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pessoas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            cpf VARCHAR(20) NOT NULL,
            nome_pep VARCHAR(255) NOT NULL,
            cidade_id INT,
            cargo_id INT,
            FOREIGN KEY (cidade_id) REFERENCES cidades(id),
            FOREIGN KEY (cargo_id) REFERENCES cargos(id),
            INDEX (cpf)
        ) ENGINE=InnoDB;
        """)
        print("Tabela 'pessoas' criada.")
        
        cursor.close()
        db.close()
    except mysql.connector.Error as err:
        print(f"Erro no setup do DB: {err}")
        sys.exit(1)

def populate_lookup_tables():
    """Popula as tabelas 'cidades' e 'cargos' com os CSVs de lookup."""
    try:
        DB_CONFIG['database'] = DB_NAME
        db = mysql.connector.connect(**DB_CONFIG)
        cursor = db.cursor()

        # --- Popular Cidades (ORG.csv) ---
        # Tenta ler com 'latin1' que é comum para arquivos CSV do Brasil
        try:
            df_org = pd.read_csv('dados_lookup/ORG.csv', encoding='latin1')
        except UnicodeDecodeError:
            df_org = pd.read_csv('dados_lookup/ORG.csv', encoding='utf-8')
        
        # Limpa dados (remove duplicados antes de inserir)
        df_org = df_org.dropna().drop_duplicates(subset=['org_nome'])
        
        sql = "INSERT IGNORE INTO cidades (org_nome) VALUES (%s)"
        values = [(row['org_nome'],) for index, row in df_org.iterrows()]
        
        cursor.executemany(sql, values)
        db.commit()
        print(f"{cursor.rowcount} cidades inseridas (ignorando duplicadas).")

        # --- Popular Cargos (FUN.csv) ---
        try:
            df_fun = pd.read_csv('dados_lookup/FUN.csv', encoding='latin1')
        except UnicodeDecodeError:
            df_fun = pd.read_csv('dados_lookup/FUN.csv', encoding='utf-8')
            
        # Limpa dados
        df_fun = df_fun.where(pd.notnull(df_fun), None) # Substitui NaN por None
        df_fun = df_fun.drop_duplicates(subset=['func_desc'])

        sql = "INSERT IGNORE INTO cargos (func_sigla, func_desc, func_nivel) VALUES (%s, %s, %s)"
        values = [
            (row['func_sigla'], row['func_desc'], row['func_nivel']) 
            for index, row in df_fun.iterrows()
        ]
        
        cursor.executemany(sql, values)
        db.commit()
        print(f"{cursor.rowcount} cargos inseridos (ignorando duplicadas).")

        cursor.close()
        db.close()

    except FileNotFoundError as err:
        print(f"Erro: Arquivo não encontrado. {err}")
        print("Certifique-se que 'ORG.csv' e 'FUN.csv' estão na pasta 'dados_lookup/'.")
    except mysql.connector.Error as err:
        print(f"Erro ao popular o DB: {err}")
    except Exception as e:
        print(f"Erro inesperado ao ler CSVs: {e}")

if __name__ == "__main__":
    create_database()
    populate_lookup_tables()
    print("\nSetup do banco de dados concluído.")