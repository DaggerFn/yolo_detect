import psycopg2
from psycopg2 import sql
from datetime import datetime

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

