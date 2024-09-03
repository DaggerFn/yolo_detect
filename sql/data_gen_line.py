import pymongo
import requests

# Conexão ao MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["meu_banco"]
colecao = db["produtos"]

# Consumindo o JSON da web
url = 'http://10.1.30.105:5000/tracking_info'
response = requests.get(url)
json_data = response.json()

# Verificando se o JSON contém vários produtos
if isinstance(json_data, list):
    colecao.insert_many(json_data)
else:
    colecao.insert_one(json_data)

# Confirmando a inserção
for produto in colecao.find():
    print(produto)
