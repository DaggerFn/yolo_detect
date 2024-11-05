from flask import send_file
import psycopg2
import pandas as pd
import io

def export_to_excel():
    try:
        conn = psycopg2.connect(
            dbname='wsfm',
            user='postgres',
            password='wsfm',
            host='10.1.30.30',
            port='5432'
        )
        print("Conexão bem-sucedida!")
    except Exception as e:
        print(f"Erro na conexão ao banco de dados: {e}")
        return "Erro na conexão ao banco de dados", 500

    try:
        query = "SELECT * FROM wsfm"
        df = pd.read_sql_query(query, conn)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="Dados")
        output.seek(0)
    except Exception as e:
        print(f"Erro ao executar a consulta ou gerar o Excel: {e}")
        return "Erro ao gerar o arquivo Excel", 500
    finally:
        conn.close()

    return send_file(output,
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                     download_name="dados.xlsx",
                     as_attachment=True)

