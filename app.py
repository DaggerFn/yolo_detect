import time
from flask import Flask, render_template, Response, jsonify
from flask_cors import CORS  # Importa a biblioteca CORS
import pymongo
import requests
from utils import load_yolo_model, generate_frames, get_tracking_info

app = Flask(__name__)
CORS(app)  # Adiciona CORS ao seu app Flask

# Configurações
MODEL_PATH = 'best0.pt'
CAMERA_URL = 'http://10.1.60.155:4000/video_feed'

# Carregar o modelo YOLOv10
model = load_yolo_model(MODEL_PATH)

# Conectar ao MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["meu_banco"]
collection = db["motores"]

# URL da API onde o JSON é fornecido
url = "http://10.1.30.105:5000/tracking_info"  # Substitua pelo URL correto

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
       if not collection.find_one(dados):
           collection.insert_one(dados)
           print("Novos dados inseridos no MongoDB")
       else:
           print("Dados já existem no banco de dados, não inseridos.")
   except Exception as e:
       print(f"Erro ao inserir no MongoDB: {e}")

@app.route('/video_feed')
def video_feed():
   """Rota do Flask para transmitir o vídeo processado."""
   return Response(generate_frames(model, CAMERA_URL),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/tracking_info', methods=['GET'])
def tracking_info():
   """Rota do Flask para obter as informações de rastreamento no formato JSON."""
   info = get_tracking_info()
   return jsonify(info)

@app.route('/tracking')
def tracking():
   """Rota do Flask para servir a página de tracking info."""
   return render_template('tracking.html')

def main():
   """Função principal para iniciar o servidor Flask e consumir JSON."""
   ultimo_json = None

   while True:
       novo_json = consumir_json()

       # Verificar se o novo JSON é diferente do anterior
       if novo_json is not None and novo_json != ultimo_json:
           inserir_no_mongo(novo_json)
           ultimo_json = novo_json  # Atualiza o último JSON inserido

       # Aguarda 1 segundo antes de verificar novamente
       time.sleep(1)

if __name__ == '__main__':
   # Rodar o Flask em um thread separado
   from threading import Thread
   Thread(target=main).start()  # Inicia a função main em um thread separado
   app.run(host='0.0.0.0', port=5000, threaded=True)


"""
from flask import Flask, render_template
from flask import Flask, Response, jsonify
from flask_cors import CORS  # Importa a biblioteca CORS
from utils import load_yolo_model, generate_frames, get_tracking_info

app = Flask(__name__)
CORS(app)  # Adiciona CORS ao seu app Flask

# Configurações
MODEL_PATH = 'best0.pt'
CAMERA_URL = 'http://10.1.60.155:4000/video_feed'

# Carregar o modelo YOLOv10
model = load_yolo_model(MODEL_PATH)

@app.route('/video_feed')
def video_feed():
    Rota do Flask para transmitir o vídeo processado.
    return Response(generate_frames(model, CAMERA_URL),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/tracking_info', methods=['GET'])
def tracking_info():
    Rota do Flask para obter as informações de rastreamento no formato JSON.
    info = get_tracking_info()
    return jsonify(info)

@app.route('/tracking')
def tracking():
    Rota do Flask para servir a página de tracking info.
    return render_template('tracking.html')

def main():
    Função principal para iniciar o servidor Flask.
    app.run(host='0.0.0.0', port=5000, threaded=True)

if __name__ == '__main__':
    main()

"""

