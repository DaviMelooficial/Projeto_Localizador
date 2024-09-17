from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

# Variáveis globais
conn = sqlite3.connect("carros.db", check_same_thread=False)
Localizador = Flask(__name__)
cursor = conn.cursor()

# Função para criar o banco de dados
def create_db():
    conn.execute('''
        CREATE TABLE IF NOT EXISTS carros (
            placa TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            latitude FLOAT,
            longitude FLOAT,
            contrato INTEGER NOT NULL,
            devedor TEXT NOT NULL
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS historico_localizacao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            placa TEXT,
            latitude FLOAT,
            longitude FLOAT,
            timestamp TEXT,
            FOREIGN KEY (placa) REFERENCES carros (placa)
        )
    ''')

# Função para inserir carros
def inserir_carro():
    conn.execute('''
        INSERT INTO carros (placa, timestamp, latitude, longitude, contrato, devedor) 
        VALUES (
            "KXRS001", 
            "13-08-2024", 
            -1.205, 
            -1.205, 
            681255, 
            "Rafael Teixeira"
        )
    ''')
    conn.commit()

# Rota para o index
@Localizador.route('/')
def read_index():
    return render_template('index.html')

# Rota de pesquisa via form
@Localizador.route('/pesquisa', methods=['POST'])
def pesquisa():
    placa = request.form['placa'].upper()

    # Busca o carro pelo campo 'placa'
    cursor.execute('SELECT * FROM carros WHERE placa = ?', (placa,))
    carro = cursor.fetchone()

    # Se o carro for encontrado, carrega o histórico
    if carro:
        cursor.execute('SELECT * FROM historico_localizacao WHERE placa = ?', (placa,))
        historico = cursor.fetchall()
        return render_template('atualizar.html', carro=carro, historico=historico)
    
    # Se o carro não for encontrado, retorna uma mensagem de erro
    else:
        return render_template('index.html', error="Placa não encontrada!")

# Função para atualizar a localização
@Localizador.route('/atualizar_localizacao', methods=['POST'])
def atualiza_localizacao():
    placa = request.form['placa'].upper()
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Verifica se a latitude e longitude estão presentes
    if not latitude or not longitude:
        return render_template('atualizar.html', error="Coordenadas não recebidas!", carro=(placa,))

    # Atualiza a tabela `historico_localizacao` com o novo registro 
    cursor.execute('''
        INSERT INTO historico_localizacao (placa, latitude, longitude, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (placa, latitude, longitude, timestamp))
    conn.commit()

    # Atualiza também a tabela principal de carros
    cursor.execute('''
        UPDATE carros 
        SET latitude = ?, longitude = ?, timestamp = ?
        WHERE placa = ?
    ''', (latitude, longitude, timestamp, placa))
    conn.commit()

    # Redireciona de volta para a página inicial após atualizar
    return redirect(url_for('read_index'))

# Criar o banco de dados
create_db()

# inserir carro de exemplo
# inserir_carro()

# Iniciar o servidor Flask
if __name__ == '__main__':
    Localizador.run(debug=True)
