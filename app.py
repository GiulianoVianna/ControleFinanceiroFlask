from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import datetime

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('contas.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            descricao TEXT,
            tipo TEXT,
            valor REAL
        )
    ''')

    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = sqlite3.connect('contas.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM transacoes ORDER BY data ASC')
    transacoes = [
        {
            'id': row[0],
            'data': datetime.datetime.strptime(row[1], '%Y-%m-%d').strftime('%d/%m/%Y') if row[1] else '',
            'descricao': row[2],
            'tipo': row[3],
            'valor': row[4]
        } for row in cursor.fetchall()
    ]
    entradas = sum(transacao['valor'] for transacao in transacoes if transacao['tipo'] == 'Crédito')
    saidas = sum(-transacao['valor'] for transacao in transacoes if transacao['tipo'] == 'Débito')
    saldo_atual = entradas - saidas

    conn.close()

    return render_template('index.html', transacoes=transacoes, entradas=entradas, saidas=saidas, saldo_atual=saldo_atual)


@app.route('/cadastrar_transacao', methods=['POST'])
def cadastrar_transacao():
    data = request.form['data']
    descricao = request.form['descricao']
    tipo = request.form['tipo']
    valor = float(request.form['valor'])

    if tipo == 'Débito':
        valor = -valor

    conn = sqlite3.connect('contas.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO transacoes (data, descricao, tipo, valor) VALUES (?, ?, ?, ?)', (data, descricao, tipo, valor))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

@app.route('/excluir/<int:transacao_id>', methods=['DELETE'])
def excluir_transacao(transacao_id):
    conn = sqlite3.connect('contas.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM transacoes WHERE id = ?', (transacao_id,))
    conn.commit()
    conn.close()

    return '', 204



@app.route('/filtrar/<data_filtro>')
def filtrar(data_filtro):
    data_filtro = datetime.datetime.strptime(data_filtro, '%Y-%m-%d')
    conn = sqlite3.connect('contas.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM transacoes WHERE data = ?', (data_filtro.strftime('%Y-%m-%d'),))
    transacoes = [
        {
            'id': row[0],
            'data': datetime.datetime.strptime(row[1], '%Y-%m-%d').strftime('%d/%m/%Y') if row[1] else '',
            'descricao': row[2],
            'tipo': row[3],
            'valor': row[4]
        } for row in cursor.fetchall()
    ]

    entradas = sum(transacao['valor'] for transacao in transacoes if transacao['tipo'] == 'Crédito')
    saidas = sum(-transacao['valor'] for transacao in transacoes if transacao['tipo'] == 'Débito')
    saldo_atual = entradas - saidas

    conn.close()

    return render_template('index.html', transacoes=transacoes, entradas=entradas, saidas=saidas, saldo_atual=saldo_atual)



if __name__ == '__main__':
    app.run(debug=True, port=5000)