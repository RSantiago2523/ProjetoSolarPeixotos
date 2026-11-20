/* ============================================================
   1. TABELA UTENTES
   ============================================================ */

CREATE INDEX IF NOT EXISTS idx_utentes_tipo_utente
ON UTENTES (ID_TIPO_UTENTE);

CREATE INDEX IF NOT EXISTS idx_utentes_tipo_genero
ON UTENTES (ID_TIPO_UTENTE, ID_GENERO);

CREATE INDEX IF NOT EXISTS idx_utentes_tipo_nascimento
ON UTENTES (ID_TIPO_UTENTE, DATA_NASCIMENTO);

CREATE INDEX IF NOT EXISTS idx_utentes_zona
ON UTENTES (ID_ZONA_UTENTE);


/* ============================================================
   2. TABELA UTENTES_IDOSOS
   ============================================================ */

CREATE INDEX IF NOT EXISTS idx_ui_estado_civil
ON UTENTES_IDOSOS (ID_ESTADO_CIVIL);

CREATE INDEX IF NOT EXISTS idx_ui_grau_autonomia
ON UTENTES_IDOSOS (ID_GRAU_AUTONOMIA);

CREATE INDEX IF NOT EXISTS idx_ui_mobilidade
ON UTENTES_IDOSOS (ID_MOBILIDADE);

CREATE INDEX IF NOT EXISTS idx_ui_nivel_isolamento
ON UTENTES_IDOSOS (ID_NIVEL_ISOLAMENTO);

CREATE INDEX IF NOT EXISTS idx_ui_relacao_familia
ON UTENTES_IDOSOS (ID_RELACAO_FAMILIA);

CREATE INDEX IF NOT EXISTS idx_ui_freq_contacto_social
ON UTENTES_IDOSOS (ID_FREQUENCIA_CONTACTO_SOCIAL);

CREATE INDEX IF NOT EXISTS idx_ui_tipo_habitacao
ON UTENTES_IDOSOS (ID_TIPO_HABITACAO);

CREATE INDEX IF NOT EXISTS idx_ui_vive_sozinho
ON UTENTES_IDOSOS (VIVE_SOZINHO)
WHERE VIVE_SOZINHO IS TRUE;

CREATE INDEX IF NOT EXISTS idx_ui_isolamento_sozinho
ON UTENTES_IDOSOS (ID_NIVEL_ISOLAMENTO, ID_UTENTE)
WHERE VIVE_SOZINHO IS TRUE;


/* ============================================================
   3. TABELAS DE ATIVIDADES E BARREIRAS
   ============================================================ */

CREATE INDEX IF NOT EXISTS idx_atividades_utente
ON ATIVIDADES_DIARIA (ID_UTENTE);

CREATE INDEX IF NOT EXISTS idx_barreiras_idosos_barreira
ON BARREIRAS_IDOSOS (ID_BARREIRA_ARQUITETONICA);


/* ============================================================
   4. TABELA CONTACTO
   ============================================================ */

CREATE INDEX IF NOT EXISTS idx_contacto_utente_data
ON CONTACTO (ID_UTENTE, DATA_CONTACTO DESC);

CREATE INDEX IF NOT EXISTS idx_contacto_data
ON CONTACTO (DATA_CONTACTO DESC);

CREATE INDEX IF NOT EXISTS idx_contacto_administrador
ON CONTACTO (ID_ADMINISTRADOR);

CREATE INDEX IF NOT EXISTS idx_contacto_tipo
ON CONTACTO (ID_TIPO_CONTACTO);

CREATE INDEX IF NOT EXISTS idx_contacto_frequencia
ON CONTACTO (ID_FREQUENCIA_CONTACTO);


/* ============================================================
   5. TABELA UTENTES_SOCIO_ECONOMICAS
   ============================================================ */

CREATE INDEX IF NOT EXISTS idx_usec_nacionalidade
ON UTENTES_SOCIO_ECONOMICAS (ID_NACIONALIDADE);

CREATE INDEX IF NOT EXISTS idx_usec_tipologia
ON UTENTES_SOCIO_ECONOMICAS (ID_TIPOLOGIA);

CREATE INDEX IF NOT EXISTS idx_usec_situacao_habitacional
ON UTENTES_SOCIO_ECONOMICAS (ID_SITUACAO_HABITACIONAL);

CREATE INDEX IF NOT EXISTS idx_usec_situacao_laboral
ON UTENTES_SOCIO_ECONOMICAS (ID_SITUACAO_LABORAL);

CREATE INDEX IF NOT EXISTS idx_usec_tipo_rendimento
ON UTENTES_SOCIO_ECONOMICAS (ID_TIPO_RENDIMENTO);

CREATE INDEX IF NOT EXISTS idx_usec_risco_social
ON UTENTES_SOCIO_ECONOMICAS (RISCO_SOCIAL);


/* ============================================================
   6. TABELAS DESPESAS E RENDIMENTOS
   ============================================================ */

CREATE INDEX IF NOT EXISTS idx_despesas_utente
ON DESPESAS_FIXAS (ID_UTENTE);

CREATE INDEX IF NOT EXISTS idx_despesas_tipo
ON DESPESAS_FIXAS (ID_TIPO_DESPESA);

CREATE INDEX IF NOT EXISTS idx_escalao_utente
ON ESCALAO_RENDIMENTOS (ID_UTENTE);

CREATE INDEX IF NOT EXISTS idx_membros_utente
ON MEMBROS_AGREGADO_FAMILIAR (ID_UTENTE);


/* ============================================================
   7. TABELAS DE DOENÇAS E FRAGILIDADES
   ============================================================ */

CREATE INDEX IF NOT EXISTS idx_doencas_idosos_doenca
ON DOENCAS_IDOSOS (ID_DOENCA_CRONICA);

CREATE INDEX IF NOT EXISTS idx_fragilidade_idoso_sinal
ON FRAGILIDADE_IDOSO (ID_SINAL_FRAGILIDADE);


/* ============================================================
   8. TABELA INTERVENCAO
   ============================================================ */

CREATE INDEX IF NOT EXISTS idx_intervencao_administrador
ON INTERVENCAO (ID_ADMINISTRADOR);

CREATE INDEX IF NOT EXISTS idx_intervencao_tipo
ON INTERVENCAO (ID_TIPO_INTERVENCAO);

CREATE INDEX IF NOT EXISTS idx_intervencao_entidade
ON INTERVENCAO (ID_ENTIDADE);

CREATE INDEX IF NOT EXISTS idx_intervencao_programa
ON INTERVENCAO (ID_PROGRAMA);

CREATE INDEX IF NOT EXISTS idx_intervencao_data
ON INTERVENCAO (DATA_INTERVENCAO DESC);


/* ============================================================
   9. TABELA ENCAMINHAMENTOS_REDE
   ============================================================ */

CREATE INDEX IF NOT EXISTS idx_encaminhamento_intervencao
ON ENCAMINHAMENTOS_REDE (ID_INTERVENCAO);

CREATE INDEX IF NOT EXISTS idx_encaminhamento_entidade
ON ENCAMINHAMENTOS_REDE (ID_ENTIDADE);

CREATE INDEX IF NOT EXISTS idx_encaminhamento_tipo_resposta
ON ENCAMINHAMENTOS_REDE (ID_TIPO_RESPOSTA);

CREATE INDEX IF NOT EXISTS idx_encaminhamento_pendentes
ON ENCAMINHAMENTOS_REDE (ID_INTERVENCAO)
WHERE ENCAMINHAMENTO_FEITO IS FALSE;


/* ============================================================
   10. TABELA PARTICIPAR
   ============================================================ */

CREATE INDEX IF NOT EXISTS idx_participar_intervencao
ON PARTICIPAR (ID_INTERVENCAO);


/* ============================================================
   11. TABELA TER - PROBLEMÁTICAS
   ============================================================ */

CREATE INDEX IF NOT EXISTS idx_ter_utente
ON TER (ID_UTENTE);

CREATE INDEX IF NOT EXISTS idx_ter_problematica
ON TER (ID_PROBLEMATICA);

CREATE INDEX IF NOT EXISTS idx_ter_intervencao
ON TER (ID_INTERVENCAO);

CREATE INDEX IF NOT EXISTS idx_ter_utente_problema_inicio
ON TER (ID_UTENTE, ID_PROBLEMATICA, DATA_INICIO);

CREATE INDEX IF NOT EXISTS idx_ter_data_inicio
ON TER (DATA_INICIO);

CREATE INDEX IF NOT EXISTS idx_ter_casos_ativos
ON TER (ID_PROBLEMATICA, ID_UTENTE, DATA_INICIO)
WHERE DATA_FIM IS NULL;


/* ============================================================
   12. TABELA QUEDAS_IDOSO
   ============================================================ */

CREATE INDEX IF NOT EXISTS idx_quedas_utente
ON QUEDAS_IDOSO (ID_UTENTE);

CREATE INDEX IF NOT EXISTS idx_quedas_data
ON QUEDAS_IDOSO (DATA_QUEDA DESC);

CREATE INDEX IF NOT EXISTS idx_quedas_utente_data
ON QUEDAS_IDOSO (ID_UTENTE, DATA_QUEDA DESC);

CREATE INDEX IF NOT EXISTS idx_historico_socio_utente_data
ON public.historico_utente_socioeconomico (id_utente, data_historico DESC)


/* ============================================================
   14. ÍNDICES DAS TABELAS DE REFERÊNCIA
   ============================================================ */

CREATE INDEX IF NOT EXISTS idx_nivel_isolamento_nome
ON NIVEL_ISOLAMENTO (NIVEL_ISOLAMENTO);

CREATE INDEX IF NOT EXISTS idx_grau_autonomia_nome
ON GRAU_AUTONOMIA (NOME_GRAU_AUTONOMIA);

CREATE INDEX IF NOT EXISTS idx_genero_descricao
ON GENERO (DESCRICAO_GENERO);

CREATE INDEX IF NOT EXISTS idx_tipo_intervencao_nome
ON TIPO_INTERVENCAO (NOME_TIPO_INTERVENCAO);

CREATE INDEX IF NOT EXISTS idx_programa_nome
ON PROGRAMA (PROGRAMA);
