# Sistema de Gestão e Emissão de CT-e

Trabalho Final de Banco de Dados I (DEC7129), feito por Fábio Augusto Martini Reis e Franciel Tuppan da Rosa.

Aplicação de console em **Python** com banco **PostgreSQL**.

## Arquivos

|Arquivo|Conteúdo|
|-|-|
|`app.py`|Menu principal, conexão, CRUD de todas as tabelas, consultas com gráfico|
|`ia.py`|Assistente com IA generativa (Google Gemini)|
|`sql/criar\\\\\\\_tabelas.sql`|Script DDL (criação das 10 tabelas)|
|`sql/carga.sql`|Carga inicial com valores fixos|
|`sql/excluir\\\\\\\_tabelas.sql`|Eliminação de todas as tabelas|
|`sql/consultas.sql`|As 3 consultas gerenciais do relatório|

## Como executar

1. Instale o PostgreSQL e crie um banco vazio chamado `cte`:

```
   CREATE DATABASE cte;
   ```

2. Instale as bibliotecas Python:

```
   pip install -r bibs.txt
   ```

3. Usuário e sua senha do PostgreSQL no início de `app.py`.
4. Chave da API do Gemini em `GEMINI\\\\\\\_API\\\\\\\_KEY`, no início de `ia.py`.
5. Execute:

```
   python app.py
   ```

6. No menu, escolha primeiro a opção **1** (criar tabelas e carregar dados).

## Menu

```
1. Criar tabelas e carregar dados
2. Eliminar todas as tabelas
3. Manutenção das tabelas (inserir/alterar/excluir/consultar)
4. Consultas gerenciais (tabela + gráfico)
5. Assistente com IA (Gemini)
0. Sair
```

Os gráficos das consultas aparecem na tela e também ficam salvos na pasta `graficos/`.

