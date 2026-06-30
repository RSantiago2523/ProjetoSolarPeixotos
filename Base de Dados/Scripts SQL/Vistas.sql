CREATE OR REPLACE VIEW vw_intervencoes_mes_ano AS
SELECT 
    EXTRACT(YEAR FROM data_intervencao) AS ano,
    EXTRACT(MONTH FROM data_intervencao) AS mes,
    COUNT(*) AS total
FROM intervencao
GROUP BY ano, mes
ORDER BY ano, mes;


CREATE OR REPLACE VIEW vw_contactos_mes_ano AS
SELECT 
    EXTRACT(YEAR FROM data_contacto) AS ano,
    EXTRACT(MONTH FROM data_contacto) AS mes,
    COUNT(*) AS total_contactos
FROM contacto
GROUP BY ano, mes
ORDER BY ano, mes;


CREATE OR REPLACE VIEW vw_problematicas_ocorridas AS
SELECT 
    p.nome_problematica AS Problematica,
    COUNT(*) AS total_casos_ativos
FROM ter t
JOIN problematicas_identificadas p ON p.id_problematica = t.id_problematica
WHERE t.data_fim IS NULL   -- apenas as que ainda não foram resolvidas
GROUP BY p.nome_problematica
ORDER BY total_ocorrencias DESC;


CREATE OR REPLACE VIEW vw_idosos_isolados AS 
SELECT
    u.id_utente,
    u.nome_utente,
    EXTRACT(YEAR FROM AGE(CURRENT_DATE, u.data_nascimento)) AS idade,
    ni.nivel_isolamento AS nivel_isolamento,
    ui.vive_sozinho
FROM UTENTES_IDOSOS ui
JOIN UTENTES u ON u.id_utente = ui.id_utente
JOIN NIVEL_ISOLAMENTO ni ON ni.id_nivel_isolamento = ui.id_nivel_isolamento
WHERE ui.vive_sozinho = true AND ni.nivel_isolamento = 'Elevado';


CREATE OR REPLACE VIEW vw_numero_idosos_isolados AS
SELECT COUNT(*)  AS Total_Idosos_Isolados
FROM utentes_idosos ui
JOIN nivel_isolamento ni ON ni.id_nivel_isolamento = ui.id_nivel_isolamento
WHERE ui.vive_sozinho = true AND ni.nivel_isolamento = 'Elevado';


CREATE OR REPLACE VIEW vw_totais_gerais AS
SELECT
  (SELECT COUNT(*) FROM utentes_idosos) AS total_idosos,
  (SELECT COUNT(*) FROM utentes_socio_economicas) AS total_socioeconomicos,
  (SELECT COUNT(*) FROM intervencao) AS total_intervencoes,
  (SELECT COUNT(*) FROM contacto) AS total_contactos;


CREATE OR REPLACE VIEW vw_idades_socioeconomicos AS
SELECT 
    CASE 
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, data_nascimento)) BETWEEN 0 AND 17 THEN '0-17'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, data_nascimento)) BETWEEN 18 AND 24 THEN '18-24'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, data_nascimento)) BETWEEN 25 AND 34 THEN '25-34'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, data_nascimento)) BETWEEN 35 AND 44 THEN '35-44'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, data_nascimento)) BETWEEN 45 AND 54 THEN '45-54'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, data_nascimento)) BETWEEN 55 AND 64 THEN '55-64'
        ELSE '65+'
    END AS faixa_etaria,
    COUNT(*) AS total
FROM utentes
WHERE id_tipo_utente = 1
GROUP BY faixa_etaria
ORDER BY MIN(EXTRACT(YEAR FROM AGE(CURRENT_DATE, data_nascimento)));


CREATE OR REPLACE VIEW vw_idades_idosos AS
SELECT 
    CASE 
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, data_nascimento)) BETWEEN 65 AND 74 THEN '65-74'
        WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, data_nascimento)) BETWEEN 75 AND 84 THEN '75-84'
        ELSE '85+'
    END AS faixa_etaria,
    COUNT(*) AS total
FROM utentes u
JOIN utentes_idosos ui ON u.id_utente = ui.id_utente
GROUP BY faixa_etaria
ORDER BY MIN(EXTRACT(YEAR FROM AGE(CURRENT_DATE, data_nascimento)));


CREATE OR REPLACE VIEW vw_genero_socioeconomicos AS
SELECT 
    g.descricao_genero AS genero,
    COUNT(*) AS total
FROM utentes u
JOIN genero g ON u.id_genero = g.id_genero
WHERE u.id_tipo_utente = 1
GROUP BY g.descricao_genero;


CREATE OR REPLACE VIEW vw_genero_idosos AS
SELECT 
    g.descricao_genero AS genero,
    COUNT(*) AS total
FROM utentes u
JOIN utentes_idosos ui ON u.id_utente = ui.id_utente
JOIN genero g ON u.id_genero = g.id_genero
GROUP BY g.descricao_genero;


CREATE OR REPLACE VIEW vw_nivel_isolamento_idosos AS
SELECT 
    ni.nivel_isolamento,
    COUNT(*) AS total
FROM utentes_idosos ui
JOIN nivel_isolamento ni ON ui.id_nivel_isolamento = ni.id_nivel_isolamento
GROUP BY ni.nivel_isolamento;


CREATE OR REPLACE VIEW vw_autonomia_idosos AS
SELECT 
    ga.nome_grau_autonomia AS grau_autonomia,
    COUNT(*) AS total
FROM utentes_idosos ui
JOIN grau_autonomia ga ON ui.id_grau_autonomia = ga.id_grau_autonomia
GROUP BY ga.nome_grau_autonomia;


CREATE OR REPLACE VIEW vw_tipos_intervencao_utilizados AS
SELECT 
    ti.nome_tipo_intervencao AS tipo,
    COUNT(*) AS total
FROM intervencao i
JOIN tipo_intervencao ti ON i.id_tipo_intervencao = ti.id_tipo_intervencao
GROUP BY ti.nome_tipo_intervencao
ORDER BY total DESC;


CREATE OR REPLACE VIEW vw_programas_utilizados AS
SELECT 
    p.programa AS programa,
    COUNT(*) AS total
FROM intervencao i
JOIN programa p ON i.id_programa = p.id_programa
GROUP BY p.programa
ORDER BY total DESC;


CREATE OR REPLACE VIEW vw_risco_social AS
SELECT 
    CASE
        WHEN risco_social IS TRUE  THEN 'Em risco'
        WHEN risco_social IS FALSE THEN 'Estável'
        ELSE 'Não preenchido'
    END AS situacao
    COUNT(*) AS total
FROM utentes_socio_economicas
GROUP BY risco_social;


CREATE OR REPLACE VIEW vw_respostas_mais_utilizadas AS
SELECT 
    tr.DESCRICAO_TIPO_RESPOSTA AS tipo_resposta,
    COUNT(e.ID_ENCAMINHAMENTO) AS total_ocorrencias
FROM ENCAMINHAMENTOS_REDE e
JOIN TIPO_RESPOSTA tr ON e.ID_TIPO_RESPOSTA = tr.ID_TIPO_RESPOSTA
WHERE e.ID_TIPO_RESPOSTA IS NOT NULL
GROUP BY tr.DESCRICAO_TIPO_RESPOSTA
ORDER BY total_ocorrencias DESC;


CREATE OR REPLACE VIEW vw_idosos_sem_contacto_4semanas AS
SELECT u.nome_utente, MAX(c.data_contacto) as ultimo_contacto
FROM utentes_idosos ui
JOIN utentes u ON ui.id_utente = u.id_utente
LEFT JOIN contacto c ON c.id_utente = ui.id_utente
GROUP BY u.id_utente
HAVING MAX(c.data_contacto) < NOW() - INTERVAL '4 weeks' OR MAX(c.data_contacto) IS NULL;


CREATE OR REPLACE VIEW vw_quedas_repetidas AS
SELECT 
    u.ID_UTENTE,
    u.NOME_UTENTE,
    EXTRACT(YEAR FROM AGE(CURRENT_DATE, u.DATA_NASCIMENTO)) AS idade,
    z.DESCRICAO_ZONA_UTENTE AS zona,
    COUNT(q.ID_QUEDA) AS total_quedas,
    MAX(q.DATA_QUEDA) AS ultima_queda
FROM UTENTES u
JOIN UTENTES_IDOSOS ui ON u.ID_UTENTE = ui.ID_UTENTE
JOIN ZONA_UTENTE z ON u.ID_ZONA_UTENTE = z.ID_ZONA_UTENTE
LEFT JOIN QUEDAS_IDOSO q ON u.ID_UTENTE = q.ID_UTENTE
WHERE q.DATA_QUEDA >= CURRENT_DATE - INTERVAL '6 months'   -- últimos 6 meses
GROUP BY u.ID_UTENTE, u.NOME_UTENTE, z.DESCRICAO_ZONA_UTENTE
HAVING COUNT(q.ID_QUEDA) >= 2
ORDER BY total_quedas DESC, ultima_queda DESC;


CREATE OR REPLACE VIEW vw_falta_rede_suporte AS
SELECT 
    u.ID_UTENTE,
    u.NOME_UTENTE,
    EXTRACT(YEAR FROM AGE(CURRENT_DATE, u.DATA_NASCIMENTO)) AS idade,
    z.DESCRICAO_ZONA_UTENTE AS zona,
    ui.VIVE_SOZINHO,
    ui.CONTACTO_EMERGENCIA,
    ui.FAMILIAR_REFERENCIA
FROM UTENTES u
JOIN UTENTES_IDOSOS ui ON u.ID_UTENTE = ui.ID_UTENTE
JOIN ZONA_UTENTE z ON u.ID_ZONA_UTENTE = z.ID_ZONA_UTENTE
WHERE ui.VIVE_SOZINHO = true
  AND (ui.CONTACTO_EMERGENCIA IS NULL OR ui.CONTACTO_EMERGENCIA = '')
  AND (ui.FAMILIAR_REFERENCIA IS NULL OR ui.FAMILIAR_REFERENCIA = '');


CREATE OR REPLACE VIEW vw_zona_utentes AS
SELECT z.descricao_zona_utente, COUNT(u.id_utente) as total,
       COUNT(CASE WHEN usec.risco_social THEN 1 END) as risco
FROM utentes u
LEFT JOIN zona_utente z ON u.id_zona_utente = z.id_zona_utente
LEFT JOIN utentes_socio_economicas usec ON u.id_utente = usec.id_utente
GROUP BY z.id_zona_utente;


CREATE OR REPLACE VIEW vw_reincidencias AS
SELECT 
    t1.id_utente,
    t1.id_problematica,
    t1.data_inicio AS primeira_ocorrencia,
    t1.data_fim AS fim_primeira,
    t2.data_inicio AS reincidencia_inicio,
    t2.data_fim AS fim_reincidencia
FROM ter t1
JOIN ter t2 ON t1.id_utente = t2.id_utente 
           AND t1.id_problematica = t2.id_problematica
           AND t1.data_inicio < t2.data_inicio
           AND t1.data_fim IS NOT NULL 
           AND t1.data_fim < t2.data_inicio
ORDER BY t1.id_utente, t1.id_problematica, t1.data_inicio;


CREATE OR REPLACE VIEW vw_taxa_reincidencia_por_problematica AS
WITH 
casos_unicos AS (
    SELECT id_problematica, COUNT(DISTINCT id_utente) AS total_utentes
    FROM ter
    GROUP BY id_problematica
),
reincidentes AS (
    SELECT t1.id_problematica, COUNT(DISTINCT t1.id_utente) AS utentes_reincidentes
    FROM ter t1
    JOIN ter t2 ON t1.id_utente = t2.id_utente 
                AND t1.id_problematica = t2.id_problematica
                AND t1.data_inicio < t2.data_inicio
                AND (t1.data_fim IS NOT NULL AND t1.data_fim < t2.data_inicio)
    GROUP BY t1.id_problematica
)
SELECT 
    p.nome_problematica,
    COALESCE(c.total_utentes, 0) AS total_utentes,
    COALESCE(r.utentes_reincidentes, 0) AS utentes_reincidentes,
    ROUND(100.0 * COALESCE(r.utentes_reincidentes, 0) / NULLIF(c.total_utentes, 0), 2) AS taxa_reincidencia_percentual
FROM problematicas_identificadas p
LEFT JOIN casos_unicos c ON p.id_problematica = c.id_problematica
LEFT JOIN reincidentes r ON p.id_problematica = r.id_problematica
WHERE c.total_utentes > 0
ORDER BY taxa_reincidencia_percentual DESC;


CREATE OR REPLACE VIEW vw_taxa_reincidencia AS
WITH 
total_utentes_problema AS (
    SELECT DISTINCT id_utente, id_problematica FROM ter
),
reincidentes AS (
    SELECT DISTINCT id_utente, id_problematica FROM vw_reincidencias
)
SELECT 
    (SELECT COUNT(*) FROM reincidentes) AS casos_com_reincidencia,
    (SELECT COUNT(*) FROM total_utentes_problema) AS total_casos_unicos,
    ROUND(100.0 * (SELECT COUNT(*) FROM reincidentes) / 
          NULLIF((SELECT COUNT(*) FROM total_utentes_problema), 0), 2) AS taxa_percentual;


CREATE OR REPLACE VIEW vw_visita_prioritaria AS
WITH 
prioridade1 AS (
    -- Isolamento elevado + vive sozinho
    SELECT 
        u.ID_UTENTE,
        u.NOME_UTENTE,
        EXTRACT(YEAR FROM AGE(CURRENT_DATE, u.DATA_NASCIMENTO)) AS idade,
        z.DESCRICAO_ZONA_UTENTE AS zona,
        'Isolamento elevado + vive sozinho' AS motivo,
        1 AS prioridade
    FROM UTENTES u
    JOIN UTENTES_IDOSOS ui ON u.ID_UTENTE = ui.ID_UTENTE
    JOIN NIVEL_ISOLAMENTO ni ON ui.ID_NIVEL_ISOLAMENTO = ni.ID_NIVEL_ISOLAMENTO
    JOIN ZONA_UTENTE z ON u.ID_ZONA_UTENTE = z.ID_ZONA_UTENTE
    WHERE ni.NIVEL_ISOLAMENTO = 'Elevado' AND ui.VIVE_SOZINHO = true
),
prioridade2 AS (
    -- Quedas repetidas (últimos 6 meses)
    SELECT
        ID_UTENTE, NOME_UTENTE, idade, zona,
        'Quedas repetidas' AS motivo, 2 AS prioridade
    FROM vw_quedas_repetidas
),
prioridade3 AS (
    -- Falta de rede de suporte
    SELECT 
        ID_UTENTE,
        NOME_UTENTE,
        idade,
        zona,
        'Falta de rede de suporte' AS motivo,
        3 AS prioridade
    FROM vw_falta_rede_suporte
)
SELECT * FROM prioridade1
UNION ALL
SELECT * FROM prioridade2
UNION ALL
SELECT * FROM prioridade3
ORDER BY prioridade, idade DESC;


CREATE OR REPLACE VIEW vw_evolucao_problematicas AS
WITH meses AS (
    SELECT generate_series(
        date_trunc('month', COALESCE((SELECT MIN(data_inicio) FROM ter), CURRENT_DATE)),
        date_trunc('month', CURRENT_DATE),
        '1 month'::interval
    ) AS mes
)
SELECT 
    to_char(m.mes, 'YYYY-MM') AS ano_mes,
    m.mes,
    COUNT(DISTINCT t.id_ter) FILTER (
        WHERE t.data_inicio >= m.mes 
          AND t.data_inicio < m.mes + interval '1 month'
    ) AS novos_casos,
    COUNT(DISTINCT t.id_ter) FILTER (
        WHERE t.data_inicio < m.mes + interval '1 month'
          AND (t.data_fim IS NULL OR t.data_fim >= m.mes + interval '1 month')
    ) AS ativos_fim_mes
FROM meses m
LEFT JOIN ter t ON true
GROUP BY m.mes
ORDER BY m.mes;

-- ============================================================
-- 1. Agravamento do grau de dependência
-- ============================================================
CREATE OR REPLACE VIEW vw_agravamento_dependencia AS
WITH ultimo_historico AS (
    SELECT DISTINCT ON (hi.id_utente)
        hi.id_utente,
        hi.snapshot_json->'principal'->>'grau_autonomia' AS grau_anterior
    FROM historico_idoso hi
    WHERE hi.data_historico < (SELECT MAX(data_historico) FROM historico_idoso WHERE id_utente = hi.id_utente)
    ORDER BY hi.id_utente, hi.data_historico DESC
),
atuais AS (
    SELECT 
        u.ID_UTENTE,
        u.NOME_UTENTE,
        ga.NOME_GRAU_AUTONOMIA AS grau_atual,
        EXTRACT(YEAR FROM AGE(CURRENT_DATE, u.DATA_NASCIMENTO)) AS idade,
        z.DESCRICAO_ZONA_UTENTE AS zona
    FROM UTENTES u
    JOIN UTENTES_IDOSOS ui ON u.ID_UTENTE = ui.ID_UTENTE
    JOIN GRAU_AUTONOMIA ga ON ui.ID_GRAU_AUTONOMIA = ga.ID_GRAU_AUTONOMIA
    JOIN ZONA_UTENTE z ON u.ID_ZONA_UTENTE = z.ID_ZONA_UTENTE
)
SELECT 
    a.NOME_UTENTE,
    a.idade,
    a.zona,
    a.grau_atual,
    h.grau_anterior
FROM atuais a
LEFT JOIN ultimo_historico h ON a.ID_UTENTE = h.id_utente
WHERE h.grau_anterior IS NOT NULL
  AND (
        (a.grau_atual = 'Dependente' AND h.grau_anterior IN ('Autónomo', 'Parcialmente dependente'))
        OR (a.grau_atual = 'Parcialmente dependente' AND h.grau_anterior = 'Autónomo')
  );

-- ============================================================
-- 2. Total de idosos que vivem sozinhos
-- ============================================================
CREATE OR REPLACE VIEW vw_vive_sozinho AS
SELECT COUNT(*) AS total_vive_sozinho
FROM UTENTES_IDOSOS
WHERE VIVE_SOZINHO = true;

-- ============================================================
-- 3. Total de idosos com dependência (parcial ou total)
-- ============================================================
CREATE OR REPLACE VIEW vw_dependentes AS
SELECT COUNT(*) AS total_dependentes
FROM UTENTES_IDOSOS ui
JOIN GRAU_AUTONOMIA ga ON ui.ID_GRAU_AUTONOMIA = ga.ID_GRAU_AUTONOMIA
WHERE ga.NOME_GRAU_AUTONOMIA != 'Autónomo';

-- ============================================================
-- 4. Top 10 idosos com mais contactos
-- ============================================================
CREATE OR REPLACE VIEW vw_mais_contactos AS
SELECT 
    u.NOME_UTENTE,
    COUNT(c.ID_CONTACTO) AS num_contactos,
    EXTRACT(YEAR FROM AGE(CURRENT_DATE, u.DATA_NASCIMENTO)) AS idade,
    z.DESCRICAO_ZONA_UTENTE AS zona
FROM CONTACTO c
JOIN UTENTES_IDOSOS ui ON c.ID_UTENTE = ui.ID_UTENTE
JOIN UTENTES u ON ui.ID_UTENTE = u.ID_UTENTE
JOIN ZONA_UTENTE z ON u.ID_ZONA_UTENTE = z.ID_ZONA_UTENTE
GROUP BY u.NOME_UTENTE, u.DATA_NASCIMENTO, z.DESCRICAO_ZONA_UTENTE
ORDER BY num_contactos DESC
LIMIT 10;

-- ============================================================
-- 5. Melhoria após participação (baseado em histórico)
-- ============================================================
CREATE OR REPLACE VIEW vw_melhorias AS
WITH primeiro_snapshot AS (
    SELECT DISTINCT ON (id_utente)
        id_utente,
        snapshot_json->'principal'->>'grau_autonomia' AS grau_inicial,
        snapshot_json->'principal'->>'nivel_isolamento' AS isolamento_inicial
    FROM historico_idoso
    ORDER BY id_utente, data_historico ASC
),
ultimo_snapshot AS (
    SELECT DISTINCT ON (id_utente)
        id_utente,
        snapshot_json->'principal'->>'grau_autonomia' AS grau_final,
        snapshot_json->'principal'->>'nivel_isolamento' AS isolamento_final
    FROM historico_idoso
    ORDER BY id_utente, data_historico DESC
)
SELECT 
    u.NOME_UTENTE,
    p.grau_inicial,
    uf.grau_final,
    p.isolamento_inicial,
    uf.isolamento_final,
    CASE 
        -- Melhoria na autonomia
        WHEN (p.grau_inicial = 'Dependente' AND uf.grau_final IN ('Parcialmente dependente', 'Autónomo'))
          OR (p.grau_inicial = 'Parcialmente dependente' AND uf.grau_final = 'Autónomo')
          -- Melhoria no isolamento
          OR (p.isolamento_inicial = 'Elevado' AND uf.isolamento_final IN ('Moderado', 'Nenhum'))
          OR (p.isolamento_inicial = 'Moderado' AND uf.isolamento_final = 'Nenhum')
        THEN 1 ELSE 0
    END AS melhorou
FROM primeiro_snapshot p
JOIN ultimo_snapshot uf ON p.id_utente = uf.id_utente
JOIN UTENTES u ON p.id_utente = u.ID_UTENTE
WHERE p.id_utente IN (SELECT DISTINCT ID_UTENTE FROM CONTACTO);   -- ← alterado de PARTICIPAR para CONTACTO

#Índices Opcionais
CREATE INDEX idx_hist_idoso_utente_data ON historico_idoso (id_utente, data_historico);
CREATE INDEX idx_hist_idoso_utente_data_desc ON historico_idoso (id_utente, data_historico DESC);