CREATE TABLE receita (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    data_registro DATE NOT NULL DEFAULT CURRENT_DATE,
    custo NUMERIC(10,2),
    tipo_receita CHAR(1) CHECK (tipo_receita IN ('s', 'd')) 
);


CREATE TABLE usuario (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    login VARCHAR(100) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    situacao CHAR(1) NOT NULL DEFAULT 'a' CHECK (situacao IN ('a', 'i')) -- a = ativo, i = inativo
);


INSERT INTO receita (nome, descricao, data_registro, custo, tipo_receita) VALUES
('Coxinha de Frango',     'Massa de batata recheada com frango desfiado e catupiry',  '2026-01-10', 2.50,  's'),
('Brigadeiro',            'Doce de chocolate com granulado, clássico brasileiro',      '2026-01-12', 1.20,  'd'),
('Esfiha de Carne',       'Massa aberta recheada com carne moída temperada',           '2026-01-15', 3.00,  's'),
('Beijinho de Coco',      'Doce de leite condensado com coco ralado e cravo',          '2026-01-18', 1.00,  'd'),
('Pastel de Queijo',      'Massa fina e crocante recheada com queijo mussarela',       '2026-01-20', 2.80,  's'),
('Bolo de Cenoura',       'Bolo fofinho de cenoura com cobertura de chocolate',        '2026-01-22', 8.50,  'd'),
('Risole de Presunto',    'Massa cremosa recheada com presunto e queijo empanado',     '2026-01-25', 3.20,  's'),
('Pudim de Leite',        'Pudim clássico de leite condensado com calda de caramelo',  '2026-01-28', 6.00,  'd'),
('Enroladinho de Salsicha','Massa de pão enrolada em salsicha, assada e dourada',      '2026-02-01', 1.80,  's'),
('Quindim',               'Doce de gema de ovo com coco ralado, brilhante e firme',   '2026-02-05', 2.00,  'd');

INSERT INTO usuario (nome, login, senha, situacao) VALUES
('Administrador', 'admin', 'admin123', 'a');


