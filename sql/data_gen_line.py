import requests
import psycopg2
from psycopg2 import sql
import time

# Configurações de conexão
DATABASE = {
    'dbname': 'WSFM',
    'user': 'postgres',
    'password': 'wsfm',
    'host': 'localhost',
    'port': '5432'
}

# Função para consumir dados JSON
def consumir_json(url):
    """Função que consome os dados JSON da API"""
    try:
        response = requests.get(url)
        # Verificar se a resposta é válida
        if response.status_code == 200:
            return response.json()  # Tentativa de decodificar o JSON
        else:
            print(f"Erro na resposta da API. Status Code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erro ao fazer a requisição: {e}")
        return None
    except ValueError as e:
        print(f"Erro ao decodificar o JSON: {e}")
        return None

# Função para conectar ao PostgreSQL
def conectar_postgres():
    """Estabelece a conexão com o banco de dados PostgreSQL"""
    try:
        conn = psycopg2.connect(**DATABASE)
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao PostgreSQL: {e}")
        return None

# Função para inserir dados no PostgreSQL
def inserir_no_postgres(dados):
    """Função que insere os dados no PostgreSQL se forem diferentes"""
    conn = conectar_postgres()
    if conn is None:
        return
    
    try:
        cursor = conn.cursor()
        
        # Adapte a tabela e as colunas conforme sua estrutura
        tabela = 'wsfm'
        colunas = ', '.join(dados.keys())
        valores = ', '.join([f"%s" for _ in dados.values()])
        
        # Verifica se o JSON já existe no banco de dados
        select_query = sql.SQL(
            "SELECT EXISTS (SELECT 1 FROM {} WHERE QtdMotor = %s AND data = %s AND hora = %s)"
        ).format(sql.Identifier(tabela))
        
        cursor.execute(select_query, (dados.get('QtdMotor'), dados.get('data'), dados.get('hora')))
        existe = cursor.fetchone()[0]
        
        if not existe:
            insert_query = sql.SQL(
                "INSERT INTO {} ({}) VALUES ({})"
            ).format(sql.Identifier(tabela), sql.SQL(colunas), sql.SQL(valores))
            
            cursor.execute(insert_query, (
                dados.get('QtdMotor'),
                dados.get('data'),
                dados.get('hora'),
                dados.get('tempo_decorrido'),
                dados.get('tempo_planejado')
            ))
            conn.commit()
            print("Novos dados inseridos no PostgreSQL")
        else:
            print("Dados já existem no banco de dados, não inseridos.")
    
    except Exception as e:
        print(f"Erro ao inserir no PostgreSQL: {e}")
    
    finally:
        cursor.close()
        conn.close()

# URL da API
url = 'http://10.1.30.105:5000/tracking_info'

# Loop contínuo para verificar e processar dados JSON
while True:
    dados_json = consumir_json(url)
    if dados_json:
        inserir_no_postgres(dados_json)
    # Espera de 10 segundos entre as verificações (ajuste conforme necessário)
    time.sleep(10)
