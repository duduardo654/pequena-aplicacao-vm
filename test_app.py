import pytest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import app as application


@pytest.fixture
def client():
    application.app.config['TESTING'] = True
    application.app.config['SECRET_KEY'] = 'test_key'
    with application.app.test_client() as client:
        yield client


@pytest.fixture
def client_logado(client):
    with client.session_transaction() as sess:
        sess['usuario'] = 'admin'
    return client


def mock_cursor(rows=None, one=None):
    cur = MagicMock()
    cur.fetchall.return_value = rows or []
    cur.fetchone.return_value = one
    return cur


def mock_conn(cur):
    conn = MagicMock()
    conn.cursor.return_value = cur
    return conn


def test_rota_index_redireciona_para_login(client):
    r = client.get('/')
    assert r.status_code == 302
    assert '/login' in r.headers['Location']


def test_login_get_retorna_200(client):
    with patch('app.render_template', return_value='<html>login</html>'):
        r = client.get('/login')
    assert r.status_code == 200


def test_login_post_credenciais_invalidas(client):
    cur = mock_cursor(one=None)
    conn = mock_conn(cur)
    with patch('app.get_connection', return_value=conn), \
         patch('app.render_template', return_value='<html>invalidos</html>'):
        r = client.post('/login', data={'login': 'errado', 'senha': 'errada'})
    assert r.status_code == 200
    assert 'invalidos' in r.data.decode('utf-8').lower()


def test_login_post_credenciais_validas(client):
    cur = mock_cursor(one=(1, 'Administrador', 'admin', 'admin123', 'a'))
    conn = mock_conn(cur)
    with patch('app.get_connection', return_value=conn):
        r = client.post('/login', data={'login': 'admin', 'senha': 'admin123'})
    assert r.status_code == 302
    assert '/receitas' in r.headers['Location']


def test_logout_limpa_sessao_e_redireciona(client_logado):
    r = client_logado.get('/logout')
    assert r.status_code == 302
    assert '/login' in r.headers['Location']


def test_listar_receitas_sem_login_redireciona(client):
    r = client.get('/receitas')
    assert r.status_code == 302
    assert '/login' in r.headers['Location']


def test_nova_receita_sem_login_redireciona(client):
    r = client.get('/receitas/nova')
    assert r.status_code == 302
    assert '/login' in r.headers['Location']


def test_editar_receita_sem_login_redireciona(client):
    r = client.get('/receitas/editar/1')
    assert r.status_code == 302
    assert '/login' in r.headers['Location']


def test_deletar_receita_sem_login_redireciona(client):
    r = client.post('/receitas/deletar/1')
    assert r.status_code == 302
    assert '/login' in r.headers['Location']


def test_exportar_pdf_sem_login_redireciona(client):
    r = client.get('/receitas/exportar/1')
    assert r.status_code == 302
    assert '/login' in r.headers['Location']


def test_listar_receitas_retorna_200(client_logado):
    cur = mock_cursor(rows=[])
    conn = mock_conn(cur)
    with patch('app.get_connection', return_value=conn), \
         patch('app.render_template', return_value='<html>lista</html>'):
        r = client_logado.get('/receitas')
    assert r.status_code == 200


def test_listar_receitas_com_filtro_tipo(client_logado):
    cur = mock_cursor(rows=[])
    conn = mock_conn(cur)
    with patch('app.get_connection', return_value=conn), \
         patch('app.render_template', return_value='<html>lista</html>'):
        r = client_logado.get('/receitas?tipo=d')
    assert r.status_code == 200
    args = cur.execute.call_args[0]
    assert 'tipo_receita' in args[0]


def test_listar_receitas_com_filtro_data(client_logado):
    cur = mock_cursor(rows=[])
    conn = mock_conn(cur)
    with patch('app.get_connection', return_value=conn), \
         patch('app.render_template', return_value='<html>lista</html>'):
        r = client_logado.get('/receitas?data_inicio=2026-01-01&data_fim=2026-12-31')
    assert r.status_code == 200
    args = cur.execute.call_args[0]
    assert 'data_registro' in args[0]


def test_nova_receita_get_retorna_200(client_logado):
    with patch('app.render_template', return_value='<html>form</html>'):
        r = client_logado.get('/receitas/nova')
    assert r.status_code == 200


def test_nova_receita_post_insere_e_redireciona(client_logado):
    cur = mock_cursor()
    conn = mock_conn(cur)
    with patch('app.get_connection', return_value=conn), \
         patch('app.enviar_email') as mock_email:
        r = client_logado.post('/receitas/nova', data={
            'nome': 'Teste', 'descricao': 'Desc',
            'data_registro': '2026-01-01', 'custo': '5.00', 'tipo_receita': 's'
        })
    assert r.status_code == 302
    conn.commit.assert_called_once()
    mock_email.assert_called_once()


def test_editar_receita_get_retorna_200(client_logado):
    cur = mock_cursor(one=(1, 'Coxinha', 'Desc', '2026-01-10', 2.50, 's'))
    conn = mock_conn(cur)
    with patch('app.get_connection', return_value=conn), \
         patch('app.render_template', return_value='<html>form</html>'):
        r = client_logado.get('/receitas/editar/1')
    assert r.status_code == 200


def test_editar_receita_post_atualiza_e_redireciona(client_logado):
    cur = mock_cursor()
    conn = mock_conn(cur)
    with patch('app.get_connection', return_value=conn), \
         patch('app.enviar_email') as mock_email:
        r = client_logado.post('/receitas/editar/1', data={
            'nome': 'Coxinha Edit', 'descricao': 'Desc',
            'data_registro': '2026-01-10', 'custo': '3.00', 'tipo_receita': 's'
        })
    assert r.status_code == 302
    conn.commit.assert_called_once()
    mock_email.assert_called_once()


def test_deletar_receita_remove_e_redireciona(client_logado):
    cur = mock_cursor()
    conn = mock_conn(cur)
    with patch('app.get_connection', return_value=conn):
        r = client_logado.post('/receitas/deletar/1')
    assert r.status_code == 302
    conn.commit.assert_called_once()


def test_exportar_pdf_receita_inexistente_retorna_404(client_logado):
    cur = mock_cursor(one=None)
    conn = mock_conn(cur)
    with patch('app.get_connection', return_value=conn):
        r = client_logado.get('/receitas/exportar/999')
    assert r.status_code == 404


def test_exportar_pdf_retorna_arquivo(client_logado):
    cur = mock_cursor(one=(1, 'Coxinha', 'Desc', '2026-01-10', 2.50, 's'))
    conn = mock_conn(cur)
    with patch('app.get_connection', return_value=conn):
        r = client_logado.get('/receitas/exportar/1')
    assert r.status_code == 200
    assert r.content_type == 'application/pdf'