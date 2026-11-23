import os
import psycopg2
import matplotlib.pyplot as plt
from tabulate import tabulate
import ia

BANCO = {
    "host": "localhost",
    "port": 5432,
    "dbname": "cte",
    "user": "postgres",
    "password": "postgres",
}


def conectar():
    return psycopg2.connect(**BANCO)


def executar_arquivo(conexao, arquivo):
    """Executa um arquivo .sql da pasta sql/"""
    texto = open("sql/" + arquivo, encoding="utf-8").read()
    cursor = conexao.cursor()
    cursor.execute(texto)
    conexao.commit()


def mostrar(cursor):
    """Mostra o resultado de um SELECT em forma de tabela."""
    colunas = [c[0] for c in cursor.description]
    linhas = cursor.fetchall()
    if len(linhas) == 0:
        print("\nNenhum registro encontrado.")
    else:
        print(tabulate(linhas, headers=colunas, tablefmt="psql"))
    return linhas


def criar_tabelas(conexao):
    try:
        executar_arquivo(conexao, "criar_tabelas.sql")
        executar_arquivo(conexao, "carga.sql")
        print("\nTabelas criadas e dados carregados!")
    except psycopg2.Error as erro:
        conexao.rollback()
        print("\nErro:", erro)
        print("Se as tabelas já existem, elimine antes (opção 2).")


def eliminar_tabelas(conexao):
    if input("Eliminar TODAS as tabelas? (s/n): ") == "s":
        executar_arquivo(conexao, "excluir_tabelas.sql")
        print("\nTabelas eliminadas!")



TABELAS = {
    "uf":                (["sigla_uf"], ["sigla_uf", "nome"]),
    "municipio":         (["id_municipio"], ["nome", "sigla_uf"]),
    "cliente":           (["id_cliente"], ["cpf_cnpj", "nome", "id_municipio"]),
    "unidade_emissora":  (["id_unidade"], ["cnpj", "nome", "id_municipio"]),
    "tabela_frete":      (["id_tabela"], ["descricao", "data_inicio", "data_fim"]),
    "componente_frete":  (["id_componente"], ["nome"]),
    "item_tabela_frete": (["id_tabela", "id_componente"], ["id_tabela", "id_componente", "valor"]),
    "cte":               (["id_cte"], ["numero", "data_emissao", "valor_total", "id_unidade", "id_tabela",
                                       "id_remetente", "id_destinatario", "id_tomador"]),
    "composicao_frete":  (["id_cte", "id_componente"], ["id_cte", "id_componente", "valor"]),
    "nota_fiscal":       (["id_nf"], ["chave_acesso", "valor", "id_cte"]),
}


def ler_chave(tabela):
    """Pede ao usuário a chave primária e monta o WHERE."""
    chave = TABELAS[tabela][0]
    valores = [input("Informe " + col + ": ") for col in chave]
    where = " AND ".join(col + " = %s" for col in chave)
    return where, valores


def listar(conexao, tabela):
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM " + tabela + " ORDER BY 1")
    mostrar(cursor)


def consultar(conexao, tabela):
    where, valores = ler_chave(tabela)
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM " + tabela + " WHERE " + where, valores)
    mostrar(cursor)


def inserir(conexao, tabela):
    campos = TABELAS[tabela][1]
    valores = [input(campo + ": ") for campo in campos]
    sql = ("INSERT INTO " + tabela + " (" + ", ".join(campos) + ") VALUES ("
           + ", ".join(["%s"] * len(campos)) + ")")
    cursor = conexao.cursor()
    cursor.execute(sql, valores)
    conexao.commit()
    print("\nRegistro inserido!")


def alterar(conexao, tabela):
    where, chave = ler_chave(tabela)
    chave_pk, campos = TABELAS[tabela]
    campos = [c for c in campos if c not in chave_pk]    # a chave primária não é alterada
    print("Digite os novos valores:")
    valores = [input(campo + ": ") for campo in campos]
    sql = "UPDATE " + tabela + " SET " + ", ".join(c + " = %s" for c in campos) + " WHERE " + where
    cursor = conexao.cursor()
    cursor.execute(sql, valores + chave)
    conexao.commit()
    print("\nRegistro alterado!" if cursor.rowcount else "\nRegistro não encontrado.")


def excluir(conexao, tabela):
    where, chave = ler_chave(tabela)
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM " + tabela + " WHERE " + where, chave)
    conexao.commit()
    print("\nRegistro excluído!" if cursor.rowcount else "\nRegistro não encontrado.")


def menu_tabelas(conexao):
    nomes = list(TABELAS)
    while True:
        print("\n--- Escolha a tabela ---")
        for i in range(len(nomes)):
            print(i + 1, "-", nomes[i])
        print("0 - Voltar")
        opcao = input("Opção: ")
        if opcao == "0":
            break
        if not opcao.isdigit() or int(opcao) < 1 or int(opcao) > len(nomes):
            print("Opção inválida.")
            continue
        tabela = nomes[int(opcao) - 1]

        while True:
            print("\n--- Tabela", tabela, "---")
            print("1 - Listar\n2 - Consultar\n3 - Inserir\n4 - Alterar\n5 - Excluir\n0 - Voltar")
            acao = input("Opção: ")
            if acao == "0":
                break
            try:
                if acao == "1":
                    listar(conexao, tabela)
                elif acao == "2":
                    consultar(conexao, tabela)
                elif acao == "3":
                    inserir(conexao, tabela)
                elif acao == "4":
                    alterar(conexao, tabela)
                elif acao == "5":
                    excluir(conexao, tabela)
                else:
                    print("Opção inválida.")
            except psycopg2.errors.ForeignKeyViolation:
                # tratamento das dependências entre as tabelas
                conexao.rollback()
                print("\nErro de chave estrangeira: o registro depende de outra tabela.")
                print("- Ao excluir: apague antes os registros que usam este.")
                print("- Ao inserir/alterar: use um código que exista na outra tabela.")
            except psycopg2.Error as erro:
                conexao.rollback()
                print("\nErro do banco:", erro)




CONSULTA_1 = """
SELECT mo.sigla_uf || ' -> ' || md.sigla_uf AS fluxo,
       COUNT(*)           AS qtd_ctes,
       SUM(c.valor_total) AS valor_frete
FROM cte c
JOIN cliente   r  ON r.id_cliente    = c.id_remetente
JOIN municipio mo ON mo.id_municipio = r.id_municipio
JOIN cliente   d  ON d.id_cliente    = c.id_destinatario
JOIN municipio md ON md.id_municipio = d.id_municipio
WHERE c.data_emissao BETWEEN %s AND %s
GROUP BY mo.sigla_uf, md.sigla_uf
ORDER BY valor_frete DESC
"""

CONSULTA_2 = """
SELECT t.nome                      AS cliente_tomador,
       m.nome || '/' || m.sigla_uf AS cidade,
       COUNT(*)                    AS qtd_ctes,
       SUM(c.valor_total)          AS total_pago
FROM cte c
JOIN cliente   t ON t.id_cliente   = c.id_tomador
JOIN municipio m ON m.id_municipio = t.id_municipio
WHERE c.data_emissao BETWEEN %s AND %s
GROUP BY t.nome, m.nome, m.sigla_uf
ORDER BY total_pago DESC
"""

CONSULTA_3 = """
SELECT TO_CHAR(c.data_emissao, 'YYYY-MM') AS mes,
       cf.nome      AS componente,
       SUM(f.valor) AS valor
FROM composicao_frete f
JOIN cte              c  ON c.id_cte         = f.id_cte
JOIN componente_frete cf ON cf.id_componente = f.id_componente
WHERE c.data_emissao BETWEEN %s AND %s
GROUP BY mes, cf.nome
ORDER BY mes, cf.nome
"""


def ler_periodo():
    print("Informe o período (Enter = ano de 2026)")
    inicio = input("Data inicial (AAAA-MM-DD): ") or "2026-01-01"
    fim = input("Data final (AAAA-MM-DD): ") or "2026-12-31"
    return inicio, fim


def executar_consulta(conexao, sql):
    cursor = conexao.cursor()
    cursor.execute(sql, ler_periodo())
    return mostrar(cursor)


def mostrar_grafico(titulo, arquivo):
    plt.title(titulo)
    plt.tight_layout()
    os.makedirs("graficos", exist_ok=True)
    plt.savefig("graficos/" + arquivo)
    plt.show()
    plt.close()


def consulta_1(conexao):
    linhas = executar_consulta(conexao, CONSULTA_1)
    if linhas:
        fluxos = [l[0] for l in linhas]
        valores = [float(l[2]) for l in linhas]
        plt.figure(figsize=(9, 5))
        plt.barh(fluxos[::-1], valores[::-1], color="steelblue")
        plt.xlabel("Valor do frete (R$)")
        mostrar_grafico("Valor de frete por fluxo UF origem -> UF destino", "consulta1_fluxo_uf.png")


def consulta_2(conexao):
    linhas = executar_consulta(conexao, CONSULTA_2)
    if linhas:
        clientes = [l[0] for l in linhas]
        valores = [float(l[3]) for l in linhas]
        plt.figure(figsize=(9, 6))
        plt.barh(clientes[::-1], valores[::-1], color="seagreen")
        plt.xlabel("Total pago (R$)")
        mostrar_grafico("Total de frete pago por cliente tomador", "consulta2_tomador.png")


def consulta_3(conexao):
    linhas = executar_consulta(conexao, CONSULTA_3)
    if linhas:
        meses = sorted(set(l[0] for l in linhas))
        componentes = sorted(set(l[1] for l in linhas))
        plt.figure(figsize=(10, 6))
        base = [0] * len(meses)                  
        for comp in componentes:
            alturas = []
            for mes in meses:
                valor = 0
                for l in linhas:
                    if l[0] == mes and l[1] == comp:
                        valor = float(l[2])
                alturas.append(valor)
            plt.bar(meses, alturas, bottom=base, label=comp)
            base = [base[i] + alturas[i] for i in range(len(meses))]
        plt.ylabel("Valor (R$)")
        plt.xticks(rotation=45)
        plt.legend()
        mostrar_grafico("Faturamento mensal por componente do frete", "consulta3_mensal_componente.png")


def menu_consultas(conexao):
    while True:
        print("\n--- Consultas gerenciais ---")
        print("1 - Fluxo geográfico (UF origem -> UF destino)")
        print("2 - Total pago por cliente tomador")
        print("3 - Faturamento mensal por componente do frete")
        print("0 - Voltar")
        opcao = input("Opção: ")
        try:
            if opcao == "1":
                consulta_1(conexao)
            elif opcao == "2":
                consulta_2(conexao)
            elif opcao == "3":
                consulta_3(conexao)
            elif opcao == "0":
                break
            else:
                print("Opção inválida.")
        except psycopg2.Error as erro:
            conexao.rollback()
            print("\nErro do banco:", erro)



def main():
    try:
        conexao = conectar()
    except psycopg2.Error as erro:
        print("Não foi possível conectar ao banco:", erro)
        return

    while True:
        print("\n===== SISTEMA DE CT-e =====")
        print("1 - Criar tabelas e carregar dados")
        print("2 - Eliminar todas as tabelas")
        print("3 - Manutenção das tabelas")
        print("4 - Consultas gerenciais")
        print("5 - Assistente com IA (Gemini)")
        print("0 - Sair")
        opcao = input("Opção: ")
        if opcao == "1":
            criar_tabelas(conexao)
        elif opcao == "2":
            eliminar_tabelas(conexao)
        elif opcao == "3":
            menu_tabelas(conexao)
        elif opcao == "4":
            menu_consultas(conexao)
        elif opcao == "5":
            ia.menu_ia(conexao)
        elif opcao == "0":
            break
        else:
            print("Opção inválida.")
    conexao.close()


if __name__ == "__main__":
    main()
