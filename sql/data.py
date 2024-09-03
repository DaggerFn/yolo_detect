import pymongo
import requests
import time

# Conectar ao MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["meu_banco"]
collection = db["motores"]

# URL da API onde o JSON é fornecido
url = "http://10.1.30.105:5000/tracking_info"  # Substitua pelo URL correto

# Variável para armazenar a última versão do JSON
ultimo_json = None

def consumir_json():
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

def inserir_no_mongo(dados):
    """Função que insere os dados no MongoDB se forem diferentes"""
    try:
        # Verifica se o JSON já existe no banco de dados
        if not collection.find_one(dados):
            collection.insert_one(dados)
            print("Novos dados inseridos no MongoDB")
        else:
            print("Dados já existem no banco de dados, não inseridos.")
    except Exception as e:
        print(f"Erro ao inserir no MongoDB: {e}")

while True:
    novo_json = consumir_json()

    # Verificar se o novo JSON é diferente do anterior
    if novo_json is not None and novo_json != ultimo_json:
        inserir_no_mongo(novo_json)
        ultimo_json = novo_json  # Atualiza o último JSON inserido

    # Aguarda 1 segundo antes de verificar novamente
    time.sleep(1)
