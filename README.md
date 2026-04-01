## Sobre a Aplicação
Repositório: https://github.com/duduardo654/pequena-aplicacao-vm.git

Aplicação web desenvolvida em Python com Flask para registro de receitas (doces e salgadas), com autenticação de usuário e CRUD.

**Tecnologias utilizadas:**
- Python 3 + Flask
- PostgreSQL
- psycopg (driver Python para PostgreSQL)
- Bootstrap 5

---

## Modelagem do Banco de Dados

### Tabela `receita`

| Coluna | Tipo | Descrição |
|---|---|---|
| id | SERIAL PRIMARY KEY | Identificador único |
| nome | VARCHAR(255) NOT NULL | Nome da receita |
| descricao | TEXT | Descrição detalhada |
| data_registro | DATE NOT NULL DEFAULT CURRENT_DATE | Data de cadastro |
| custo | NUMERIC(10,2) | Custo de produção |
| tipo_receita | CHAR(1) CHECK ('s','d') | 's' = Salgado, 'd' = Doce |

### Tabela `usuario`

| Coluna | Tipo | Descrição |
|---|---|---|
| id | SERIAL PRIMARY KEY | Identificador único |
| nome | VARCHAR(255) NOT NULL | Nome do usuário |
| login | VARCHAR(100) NOT NULL UNIQUE | Login de acesso |
| senha | VARCHAR(255) NOT NULL | Senha de acesso |
| situacao | CHAR(1) DEFAULT 'a' CHECK ('a','i') | 'a' = Ativo, 'i' = Inativo |


## Interfaces Desenvolvidas

A aplicação possui três telas:

- **Login** — autenticação do usuário com login e senha
- **Listagem de Receitas** — tabela com todas as receitas cadastradas e botões de editar e deletar
- **Formulário de Receita** — tela de cadastro e edição de receitas

---

## Publicação na VM

### Acesso à VM

O acesso é feito via SSH:

```bash
ssh univates@177.44.248.14
```

### Instalação das Ferramentas

**1. Atualizar o sistema:**
```bash
sudo apt update && sudo apt upgrade -y
```

**2. Instalar Python 3 e pip:**
```bash
sudo apt install python3 python3-pip -y
```

**3. Instalar PostgreSQL:**
```bash
sudo apt install postgresql postgresql-contrib -y
```

**4. Verificar se o PostgreSQL está rodando:**
```bash
sudo systemctl status postgresql
```

**5. Instalar Flask e o driver do PostgreSQL:**
```bash
pip install flask psycopg --break-system-packages
```

### Implantação da Aplicação

**Criar a estrutura de pastas na VM:**
```bash
mkdir ~/projeto_receitas
mkdir ~/projeto_receitas/templates
```

**Transferir os arquivos via SCP (executar no terminal local):**
```bash
scp app.py univates@177.44.248.14:~/projeto_receitas/
scp templates/login.html univates@177.44.248.14:~/projeto_receitas/templates/
scp templates/receitas.html univates@177.44.248.14:~/projeto_receitas/templates/
scp templates/form_receita.html univates@177.44.248.14:~/projeto_receitas/templates/
```

**Iniciar a aplicação na VM:**
```bash
cd ~/projeto_receitas
python3 -m flask run --host=0.0.0.0 --port=5000
```

### URL de Acesso

```
http://177.44.248.14:5000
```

**Credenciais:**
- Usuário: `admin`
- Senha: `admin123`

---

## Tempos Gastos

| Etapa | Tempo |
|---|---|
| Desenvolvimento da aplicação | 1h 30min |
| Criação do ambiente na VM | 30min |
| Publicação da aplicação | 10min |
| **Total** | **2h 10min** |
