# Módulo de IA ( - usa a API do Google Gemini
# 1) O usuário faz uma pergunta em português, o Gemini gera o SQL,
#    o programa executa no banco e o Gemini explica o resultado.
# 2) O Gemini faz uma análise gerencial com base nas consultas do item 6.

import requests
from tabulate import tabulate

GEMINI_API_KEY = "chave aqui"
MODELO = "gemini-4-hydrogen"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODELO}:generateContent"

# Estrutura do banco, enviada ao Gemini para ele saber montar o SQL
ESQUEMA = """
uf(sigla_uf, nome)
municipio(id_municipio, nome, sigla_uf)
cliente(id_cliente, cpf_cnpj, nome, id_municipio)
unidade_emissora(id_unidade, cnpj, nome, id_municipio)
tabela_frete(id_tabela, descricao, data_inicio, data_fim)
componente_frete(id_componente, nome)
item_tabela_frete(id_tabela, id_componente, valor)
cte(id_cte, numero, data_emissao, valor_total, id_unidade, id_tabela,
    id_remetente, id_destinatario, id_tomador)   -- remetente, destinatario e tomador sao clientes
composicao_frete(id_cte, id_componente, valor)
nota_fiscal(id_nf, chave_acesso, valor, id_cte)
O tomador e o cliente que paga o frete.
"""


def perguntar_gemini(texto):
    """Manda um texto para o Gemini e devolve a resposta."""
    if GEMINI_API_KEY == "":
        print("Coloque a sua chave do Gemini no arquivo ia.py")
        return ""
    dados = {"contents": [{"parts": [{"text": texto}]}]}
    resposta = requests.post(URL, headers={"x-goog-api-key": GEMINI_API_KEY}, json=dados)
    resposta.raise_for_status()
    return resposta.json()["candidates"][0]["content"]["parts"][0]["text"]


def pergunta_livre(conexao):
    pergunta = input("\nFaça sua pergunta sobre os dados:\n> ")

    # 1. A IA gera o SQL
    sql = perguntar_gemini("Banco PostgreSQL com as tabelas:\n" + ESQUEMA +
                           "\nEscreva somente um SELECT que responda a pergunta, sem explicação."
                           "\nPergunta: " + pergunta)
    sql = sql.replace("```sql", "").replace("```", "").strip().rstrip(";")
    print("\nSQL gerado pela IA:\n" + sql)

    # 2. Por segurança, só aceita SELECT
    if not sql.upper().startswith("SELECT"):
        print("Consulta bloqueada: só é permitido SELECT.")
        return

    # 3. Executa no banco em modo somente leitura
    cursor = conexao.cursor()
    cursor.execute("SET TRANSACTION READ ONLY")
    cursor.execute(sql)
    colunas = [c[0] for c in cursor.description]
    linhas = cursor.fetchall()
    conexao.rollback()
    resultado = tabulate(linhas, headers=colunas, tablefmt="psql")
    print(resultado)

    # 4. A IA explica o resultado
    resposta = perguntar_gemini("Pergunta: " + pergunta + "\nResultado:\n" + resultado +
                                "\nResponda a pergunta em português, em poucas frases.")
    print("\nResposta da IA:\n" + resposta)


def analise_gerencial(conexao):
    import app                   
    periodo = app.ler_periodo()
    cursor = conexao.cursor()
    dados = ""
    for sql in (app.CONSULTA_1, app.CONSULTA_2, app.CONSULTA_3):
        cursor.execute(sql, periodo)
        colunas = [c[0] for c in cursor.description]
        dados += tabulate(cursor.fetchall(), headers=colunas) + "\n\n"

    print("\nGerando análise com IA...\n")
    print(perguntar_gemini("Você é analista de uma transportadora. Com base nos dados abaixo, "
                           "escreva em português 3 pontos principais e 2 sugestões para a empresa.\n\n" + dados))


def menu_ia(conexao):
    while True:
        print("\n--- Assistente com IA (Gemini) ---")
        print("1. Fazer uma pergunta sobre os dados")
        print("2. Gerar análise gerencial")
        print("0. Voltar")
        opcao = input("Opção: ")
        try:
            if opcao == "1":
                pergunta_livre(conexao)
            elif opcao == "2":
                analise_gerencial(conexao)
            elif opcao == "0":
                break
            else:
                print("Opção inválida.")
        except Exception as erro:
            conexao.rollback()
            print("Erro:", erro)
