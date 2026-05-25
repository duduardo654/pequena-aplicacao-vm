from flask import Flask, render_template, request, redirect, url_for, session, send_file
import psycopg
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
import io

app = Flask(__name__)
app.secret_key = 'abc123'

EMAIL_REMETENTE = 'eduardo.secco@universo.univates.br'
EMAIL_SENHA_APP = 'ndcu llrc zupc loyn'
EMAIL_DESTINATARIO = 'eduardo.secco@universo.univates.br'


def get_connection():
    return psycopg.connect(
        host='localhost',
        port=5432,
        dbname='db_manager_conf',
        user='postgres',
        password='postgres123'
    )


def enviar_email(assunto, corpo):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_REMETENTE
        msg['To'] = EMAIL_DESTINATARIO
        msg['Subject'] = assunto
        msg.attach(MIMEText(corpo, 'plain'))
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_REMETENTE, EMAIL_SENHA_APP)
            smtp.send_message(msg)
    except Exception as e:
        print(f'Erro ao enviar email: {e}')


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        login_input = request.form['login']
        senha = request.form['senha']
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM usuario WHERE login = %s AND senha = %s AND situacao = 'a'",
            (login_input, senha)
        )
        usuario = cur.fetchone()
        cur.close()
        conn.close()
        if usuario:
            session['usuario'] = login_input
            return redirect(url_for('listar_receitas'))
        erro = 'Login ou senha invalidos.'
    return render_template('login.html', erro=erro)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/receitas')
def listar_receitas():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')
    tipo = request.args.get('tipo', '')

    query = "SELECT id, nome, descricao, data_registro, custo, tipo_receita FROM receita WHERE 1=1"
    params = []

    if data_inicio:
        query += " AND data_registro >= %s"
        params.append(data_inicio)
    if data_fim:
        query += " AND data_registro <= %s"
        params.append(data_fim)
    if tipo in ('s', 'd'):
        query += " AND tipo_receita = %s"
        params.append(tipo)

    query += " ORDER BY id"

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    receitas = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('receitas.html', receitas=receitas,
                           data_inicio=data_inicio, data_fim=data_fim, tipo=tipo)


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
            "INSERT INTO receita (nome, descricao, data_registro, custo, tipo_receita)"
            " VALUES (%s, %s, %s, %s, %s)",
            (nome, descricao, data_registro, custo, tipo_receita)
        )
        conn.commit()
        cur.close()
        conn.close()
        tipo_label = 'Doce' if tipo_receita == 'd' else 'Salgado'
        enviar_email(
            f'Nova receita cadastrada: {nome}',
            f'Nome: {nome}\nTipo: {tipo_label}\nCusto: R$ {custo}\n'
            f'Data: {data_registro}\nDescricao: {descricao}'
        )
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
            "UPDATE receita SET nome=%s, descricao=%s, data_registro=%s,"
            " custo=%s, tipo_receita=%s WHERE id=%s",
            (nome, descricao, data_registro, custo, tipo_receita, id)
        )
        conn.commit()
        cur.close()
        conn.close()
        tipo_label = 'Doce' if tipo_receita == 'd' else 'Salgado'
        enviar_email(
            f'Receita atualizada: {nome}',
            f'Nome: {nome}\nTipo: {tipo_label}\nCusto: R$ {custo}\n'
            f'Data: {data_registro}\nDescricao: {descricao}'
        )
        return redirect(url_for('listar_receitas'))
    cur.execute(
        "SELECT id, nome, descricao, data_registro, custo, tipo_receita FROM receita WHERE id = %s",
        (id,)
    )
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


@app.route('/receitas/exportar/<int:id>')
def exportar_receita_pdf(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, nome, descricao, data_registro, custo, tipo_receita FROM receita WHERE id = %s",
        (id,)
    )
    r = cur.fetchone()
    cur.close()
    conn.close()

    if not r:
        return 'Receita nao encontrada', 404

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    titulo = ParagraphStyle('titulo', parent=styles['Title'], fontSize=18, spaceAfter=20)

    tipo_label = 'Doce' if r[5] == 'd' else 'Salgado'

    story = []
    story.append(Paragraph(f'Receita: {r[1]}', titulo))
    story.append(Spacer(1, 0.3*cm))

    dados = [
        ['Campo', 'Valor'],
        ['Nome', r[1]],
        ['Descricao', r[2] or ''],
        ['Data de Registro', str(r[3])],
        ['Custo', f'R$ {r[4]:.2f}'],
        ['Tipo', tipo_label],
    ]
    t = Table(dados, colWidths=[5*cm, 11*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f9f9f9'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
    ]))
    story.append(t)
    doc.build(story)

    buffer.seek(0)
    return send_file(buffer, as_attachment=True,
                     download_name=f'receita_{id}.pdf',
                     mimetype='application/pdf')


if __name__ == '__main__':
    app.run(debug=True)