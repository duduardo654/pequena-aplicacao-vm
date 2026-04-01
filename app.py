from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
import psycopg

app = Flask(__name__)
app.secret_key = 'chave_secreta'

def get_connection():
    return psycopg.connect(
        host='localhost',
        port=5432,
        dbname='db_manager_conf',
        user='postgres',
        password='postgres123'
    )

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        login = request.form['login']
        senha = request.form['senha']
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM usuario WHERE login = %s AND senha = %s AND situacao = 'a'", (login, senha))
        usuario = cur.fetchone()
        cur.close()
        conn.close()
        if usuario:
            session['usuario'] = login
            return redirect(url_for('listar_receitas'))
        else:
            erro = 'Login ou senha inválidos.'
    return render_template('login.html', erro=erro)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/receitas')
def listar_receitas():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, descricao, data_registro, custo, tipo_receita FROM receita ORDER BY id")
    receitas = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('receitas.html', receitas=receitas)

@app.route('/receitas/nova', methods=['GET', 'POST'])
def nova_receita():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        data_registro = request.form['data_registro']
        custo = request.form['custo']
        tipo_receita = request.form['tipo_receita']
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO receita (nome, descricao, data_registro, custo, tipo_receita) VALUES (%s, %s, %s, %s, %s)",
            (nome, descricao, data_registro, custo, tipo_receita)
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('listar_receitas'))
    return render_template('form_receita.html', receita=None)

@app.route('/receitas/editar/<int:id>', methods=['GET', 'POST'])
def editar_receita(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    conn = get_connection()
    cur = conn.cursor()
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        data_registro = request.form['data_registro']
        custo = request.form['custo']
        tipo_receita = request.form['tipo_receita']
        cur.execute(
            "UPDATE receita SET nome=%s, descricao=%s, data_registro=%s, custo=%s, tipo_receita=%s WHERE id=%s",
            (nome, descricao, data_registro, custo, tipo_receita, id)
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('listar_receitas'))
    cur.execute("SELECT id, nome, descricao, data_registro, custo, tipo_receita FROM receita WHERE id = %s", (id,))
    receita = cur.fetchone()
    cur.close()
    conn.close()
    return render_template('form_receita.html', receita=receita)

@app.route('/receitas/deletar/<int:id>', methods=['POST'])
def deletar_receita(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM receita WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('listar_receitas'))

if __name__ == '__main__':
    app.run(debug=True)