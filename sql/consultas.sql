-- Consulta 1: quantidade de CT-es e valor de frete
-- por UF de origem (remetente) e UF de destino (destinatário)
SELECT mo.sigla_uf || ' -> ' || md.sigla_uf AS fluxo,
       COUNT(*)                            AS qtd_ctes,
       SUM(c.valor_total)                  AS valor_frete
FROM cte c
JOIN cliente   r  ON r.id_cliente   = c.id_remetente
JOIN municipio mo ON mo.id_municipio = r.id_municipio
JOIN cliente   d  ON d.id_cliente   = c.id_destinatario
JOIN municipio md ON md.id_municipio = d.id_municipio
WHERE c.data_emissao BETWEEN '2026-01-01' AND '2026-12-31'
GROUP BY mo.sigla_uf, md.sigla_uf
ORDER BY valor_frete DESC;

-- Consulta 2: Total de frete pago por cliente pagador (tomador)
SELECT t.nome                        AS cliente_tomador,
       m.nome || '/' || m.sigla_uf   AS cidade,
       COUNT(*)                      AS qtd_ctes,
       SUM(c.valor_total)            AS total_pago
FROM cte c
JOIN cliente   t ON t.id_cliente   = c.id_tomador
JOIN municipio m ON m.id_municipio = t.id_municipio
WHERE c.data_emissao BETWEEN '2026-01-01' AND '2026-12-31'
GROUP BY t.nome, m.nome, m.sigla_uf
ORDER BY total_pago DESC;

-- Consulta 3: Faturamento mensal por componente do frete
SELECT TO_CHAR(c.data_emissao, 'YYYY-MM') AS mes,
       cf.nome                            AS componente,
       SUM(f.valor)                       AS valor
FROM composicao_frete f
JOIN cte              c  ON c.id_cte         = f.id_cte
JOIN componente_frete cf ON cf.id_componente = f.id_componente
WHERE c.data_emissao BETWEEN '2026-01-01' AND '2026-12-31'
GROUP BY mes, cf.nome
ORDER BY mes, cf.nome;
