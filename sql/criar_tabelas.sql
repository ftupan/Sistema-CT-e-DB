CREATE TABLE uf (
    sigla_uf  CHAR(2)      PRIMARY KEY,
    nome      VARCHAR(50)  NOT NULL
);

CREATE TABLE municipio (
    id_municipio  SERIAL       PRIMARY KEY,
    nome          VARCHAR(100) NOT NULL,
    sigla_uf      CHAR(2)      NOT NULL REFERENCES uf (sigla_uf)
);

CREATE TABLE cliente (
    id_cliente    SERIAL       PRIMARY KEY,
    cpf_cnpj      VARCHAR(14)  NOT NULL UNIQUE,
    nome          VARCHAR(150) NOT NULL,
    id_municipio  INTEGER      NOT NULL REFERENCES municipio (id_municipio)
);

CREATE TABLE unidade_emissora (
    id_unidade    SERIAL       PRIMARY KEY,
    cnpj          CHAR(14)     NOT NULL UNIQUE,
    nome          VARCHAR(100) NOT NULL,
    id_municipio  INTEGER      NOT NULL REFERENCES municipio (id_municipio)
);

CREATE TABLE tabela_frete (
    id_tabela    SERIAL       PRIMARY KEY,
    descricao    VARCHAR(100) NOT NULL,
    data_inicio  DATE         NOT NULL,
    data_fim     DATE         NOT NULL,
    CHECK (data_fim >= data_inicio)
);

CREATE TABLE componente_frete (
    id_componente  SERIAL      PRIMARY KEY,
    nome           VARCHAR(50) NOT NULL UNIQUE
);

-- Valor de cada componente dentro de uma tabela de frete (N:M)
CREATE TABLE item_tabela_frete (
    id_tabela      INTEGER       NOT NULL REFERENCES tabela_frete (id_tabela),
    id_componente  INTEGER       NOT NULL REFERENCES componente_frete (id_componente),
    valor          NUMERIC(10,2) NOT NULL CHECK (valor >= 0),
    PRIMARY KEY (id_tabela, id_componente)
);

CREATE TABLE cte (
    id_cte           SERIAL        PRIMARY KEY,
    numero           INTEGER       NOT NULL,
    data_emissao     DATE          NOT NULL,
    valor_total      NUMERIC(12,2) NOT NULL CHECK (valor_total >= 0),
    id_unidade       INTEGER       NOT NULL REFERENCES unidade_emissora (id_unidade),
    id_tabela        INTEGER       NOT NULL REFERENCES tabela_frete (id_tabela),
    id_remetente     INTEGER       NOT NULL REFERENCES cliente (id_cliente),
    id_destinatario  INTEGER       NOT NULL REFERENCES cliente (id_cliente),
    id_tomador       INTEGER       NOT NULL REFERENCES cliente (id_cliente),
    UNIQUE (id_unidade, numero)
);

-- Valor cobrado de cada componente em um CT-e (N:M)
CREATE TABLE composicao_frete (
    id_cte         INTEGER       NOT NULL REFERENCES cte (id_cte) ON DELETE CASCADE,
    id_componente  INTEGER       NOT NULL REFERENCES componente_frete (id_componente),
    valor          NUMERIC(10,2) NOT NULL CHECK (valor >= 0),
    PRIMARY KEY (id_cte, id_componente)
);

CREATE TABLE nota_fiscal (
    id_nf         SERIAL        PRIMARY KEY,
    chave_acesso  CHAR(44)      NOT NULL UNIQUE,
    valor         NUMERIC(12,2) NOT NULL CHECK (valor >= 0),
    id_cte        INTEGER       NOT NULL REFERENCES cte (id_cte) ON DELETE CASCADE
);
