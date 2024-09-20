import time
from flask import Flask, render_template, Response, jsonify
from flask_cors import CORS
import requests
import psycopg2
from psycopg2 import sql
from datetime import datetime
from utils import load_yolo_model, generate_frames, get_tracking_info

app = Flask(__name__)
CORS(app)  # Adiciona CORS ao seu app    Flask

# Configurações
MODEL_PATH = 'pt/8n_colab_p3_openvino_model'
CAMERA_URL = 'http://10.1.60.155:4000/video_feed'

# Carregar o modelo YOLOv10
model = load_yolo_model(MODEL_PATH) 

# Configuração do banco de dados PostgreSQL
DATABASE = {
  'dbname': 'WSFM',
  'user': 'postgres',
  'password': 'wsfm',
  'host': '10.1.30.105',  
  'port': '5432'
}

def conectar_postgres():
  """Estabelece a conexão com o banco de dados PostgreSQL."""
  try:
      conn = psycopg2.connect(
          dbname=DATABASE['dbname'],
          user=DATABASE['user'],
          password=DATABASE['password'],
          host=DATABASE['host'],
          port=DATABASE['port'],
          options="-c client_encoding=utf8"
      )
      return conn
  except Exception as e:
      print(f"Erro ao conectar ao PostgreSQL: {e}")
      return None

def inserir_no_postgres(dados):
   """Insere os dados no PostgreSQL se forem diferentes."""
   conn = conectar_postgres()
   if conn is None:
       return

   try:
       cursor = conn.cursor()

       # Validação do campo 'data'
       if 'data' not in dados or dados['data'] is None:
           print("Campo 'data' não encontrado ou é None.")
           return
       
       # Validação do campo 'hora'
       if 'hora' not in dados or dados['hora'] is None:
           print("Campo 'hora' não encontrado ou é None.")
           return

       # Converter a data para o formato YYYY-MM-DD se não for None
       data_convertida = datetime.strptime(dados['data'], "%d/%m/%Y").date() if dados['data'] else None
       
       # Preparar os dados para inserção
       dados_inserir = {
           'QtdMotor': dados['QtdMotor'],
           'data': data_convertida,
           'hora': dados['hora'],
           'tempo_decorrido': dados['tempo_decorrido'],
           'tempo_planejado': dados['tempo_planejado']
       }

       # Se a data ou hora forem None, não insira
       if dados_inserir['data'] is None or dados_inserir['hora'] is None:
           print("Dados não inseridos devido a campos 'data' ou 'hora' ausentes.")
           return

       colunas = ', '.join(dados_inserir.keys())
       valores = ', '.join([f"%s" for _ in dados_inserir.values()])

       # Verifica se os dados já existem no banco de dados
       select_query = sql.SQL(
           "SELECT EXISTS (SELECT 1 FROM {} WHERE QtdMotor = %s AND data = %s AND hora = %s)"
       ).format(sql.Identifier('wsfm'))

       cursor.execute(select_query, (dados_inserir['QtdMotor'], dados_inserir['data'], dados_inserir['hora']))
       existe = cursor.fetchone()[0]

       if not existe:
           insert_query = sql.SQL(
               "INSERT INTO {} ({}) VALUES ({})"
           ).format(sql.Identifier('wsfm'), sql.SQL(colunas), sql.SQL(valores))

           cursor.execute(insert_query, (
               dados_inserir['QtdMotor'],
               dados_inserir['data'],
               dados_inserir['hora'],
               dados_inserir['tempo_decorrido'],
               dados_inserir['tempo_planejado']
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

def consumir_json():
  """Função que consome os dados JSON da API."""
  url = "http://10.1.30.105:5000/tracking_info"  # Altere para o URL correto
  try:
      response = requests.get(url)
      if response.status_code == 200:
          return response.json()
      else:
          print(f"Erro na resposta da API. Status Code: {response.status_code}")
          return None
  except requests.exceptions.RequestException as e:
      print(f"Erro ao fazer a requisição: {e}")
      return None

def main():
   """Função principal para iniciar o servidor Flask e consumir JSON."""
   ultimo_json = None

   while True:
       novo_json = consumir_json()

       # Verificar se o novo JSON é diferente do anterior
       if novo_json is not None:
           print("Novo JSON recebido:", novo_json)  # Adiciona esta linha para depuração
           
           if novo_json != ultimo_json:
               inserir_no_postgres(novo_json)
               ultimo_json = novo_json  # Atualiza o último JSON inserido

       # Aguarda 1 segundo antes de verificar novamente
       time.sleep(1)

if __name__ == '__main__':
  # Rodar o Flask em um thread separado
  from threading import Thread
  Thread(target=main).start()  # Inicia a função main em um thread separado
  app.run(host='0.0.0.0', port=5000, threaded=True)
