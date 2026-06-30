/*==============================================================*/
/* 1. INSERIR DADOS NAS TABELAS DE DOMÍNIO                      */
/*==============================================================*/

-- TIPO_UTENTE
INSERT INTO TIPO_UTENTE (ID_TIPO_UTENTE, NOME_TIPO_UTENTE, DESCRICAO_TIPO_UTENTE) VALUES
(1, 'Socioeconomico', 'Utente do programa de intervenção social comunitária'),
(2, 'Idoso', 'Utente do programa de apoio a seniores');

-- ZONA_UTENTE (freguesias/bairros)
INSERT INTO ZONA_UTENTE (ID_ZONA_UTENTE, DESCRICAO_ZONA_UTENTE) VALUES
(1, 'Freguesia do Centro'),
(2, 'Freguesia da Ribeira'),
(3, 'Bairro Social da Encosta'),
(4, 'Urbanização das Flores'),
(5, 'Zona Histórica'),
(6, 'Bairro da Ponte'),
(7, 'Freguesia Nova'),
(8, 'Zona Industrial');

-- GENERO
INSERT INTO GENERO (ID_GENERO, DESCRICAO_GENERO) VALUES
(1, 'Masculino'),
(2, 'Feminino'),
(3, 'Não binário'),
(4, 'Outro');

-- ESTADO_CIVIL
INSERT INTO ESTADO_CIVIL (ID_ESTADO_CIVIL, DESCRICAO_ESTADO_CIVIL) VALUES
(1, 'Solteiro(a)'),
(2, 'Casado(a)'),
(3, 'União de facto'),
(4, 'Divorciado(a)'),
(5, 'Viúvo(a)');

-- GRAU_AUTONOMIA
INSERT INTO GRAU_AUTONOMIA (ID_GRAU_AUTONOMIA, NOME_GRAU_AUTONOMIA) VALUES
(1, 'Autónomo'),
(2, 'Parcialmente dependente'),
(3, 'Dependente');

-- MOBILIDADE
INSERT INTO MOBILIDADE (ID_MOBILIDADE, NOME_MOBILIDADE) VALUES
(1, 'Sem limitações'),
(2, 'Usa bengala'),
(3, 'Usa andarilho'),
(4, 'Cadeira de rodas'),
(5, 'Acamado');

-- NIVEL_ISOLAMENTO
INSERT INTO NIVEL_ISOLAMENTO (ID_NIVEL_ISOLAMENTO, NIVEL_ISOLAMENTO) VALUES
(1, 'Nenhum'),
(2, 'Moderado'),
(3, 'Elevado');

-- RELACAO_FAMILIA
INSERT INTO RELACAO_FAMILIA (ID_RELACAO_FAMILIA, DESCRICAO_RELACAO_FAMILIA) VALUES
(1, 'Boa'),
(2, 'Frágil'),
(3, 'Inexistente');

-- FREQUENCIA_CONTACTO_SOCIAL
INSERT INTO FREQUENCIA_CONTACTO_SOCIAL (ID_FREQUENCIA_CONTACTO_SOCIAL, DESCRICAO_FREQUENCIA_CONTACTO_SOCIAL) VALUES
(1, 'Diário'),
(2, 'Semanal'),
(3, 'Quinzenal'),
(4, 'Mensal'),
(5, 'Raramente'),
(6, 'Nunca');

-- TIPO_HABITACAO
INSERT INTO TIPO_HABITACAO (ID_TIPO_HABITACAO, DESCRICAO_TIPO) VALUES
(1, 'Casa própria'),
(2, 'Casa arrendada'),
(3, 'Quarto arrendado'),
(4, 'Habitação social'),
(5, 'Situação de sem-abrigo'),
(6, 'Instituição');

-- BARREIRAS_ARQUITETONICAS
INSERT INTO BARREIRAS_ARQUITETONICAS (ID_BARREIRA_ARQUITETONICA, DESCRICAO_BARREIRA_ARQUITETONICA) VALUES
(1, 'Escadas sem corrimão'),
(2, 'Casa de banho não adaptada'),
(3, 'Degraus à entrada'),
(4, 'Portas estreitas'),
(5, 'Falta de elevador'),
(6, 'Iluminação insuficiente'),
(7, 'Tapetes soltos/perigosos');

-- SINAIS_FRAGILIDADE
INSERT INTO SINAIS_FRAGILIDADE (ID_SINAL_FRAGILIDADE, DESCRICAO_FRAGILIDADE) VALUES
(1, 'Fadiga frequente'),
(2, 'Confusão/desorientação'),
(3, 'Perda de peso'),
(4, 'Falta de apetite'),
(5, 'Dificuldade em levantar-se'),
(6, 'Tonturas frequentes'),
(7, 'Esquecimentos frequentes');

-- DOENCAS_CRONICAS
INSERT INTO DOENCAS_CRONICAS (ID_DOENCA_CRONICA, DESCRICAO_DOENCA_CRONICA) VALUES
(1, 'Hipertensão arterial'),
(2, 'Diabetes mellitus'),
(3, 'Doença cardíaca'),
(4, 'Doença pulmonar obstrutiva crónica'),
(5, 'Artrite/osteoartrose'),
(6, 'Alzheimer/demência'),
(7, 'Parkinson'),
(8, 'Osteoporose'),
(9, 'Depressão'),
(10, 'Doença renal crónica');

-- TIPO_CONTACTO
INSERT INTO TIPO_CONTACTO (ID_TIPO_CONTACTO, NOME_TIPO_CONTACTO) VALUES
(1, 'Visita domiciliária'),
(2, 'Chamada telefónica'),
(3, 'Atividade em grupo'),
(4, 'Atendimento no balcão'),
(5, 'Videochamada'),
(6, 'Contacto com familiar');

-- FREQUENCIA_CONTACTO
INSERT INTO FREQUENCIA_CONTACTO (ID_FREQUENCIA_CONTACTO, DESCRICAO_FREQUENCIA_CONTACTO) VALUES
(1, 'Único'),
(2, 'Semanal'),
(3, 'Quinzenal'),
(4, 'Mensal'),
(5, 'Trimestral');

-- SITUACAO_LABORAL
INSERT INTO SITUACAO_LABORAL (ID_SITUACAO_LABORAL, DESCRICAO_SITUACAO_LABORAL) VALUES
(1, 'Empregado(a)'),
(2, 'Desempregado(a)'),
(3, 'Reformado(a)'),
(4, 'Pensão por invalidez'),
(5, 'Estudante'),
(6, 'Trabalhador informal'),
(7, 'Doméstica');

-- TIPO_RENDIMENTO
INSERT INTO TIPO_RENDIMENTO (ID_TIPO_RENDIMENTO, NOME_TIPO_RENDIMENTO) VALUES
(1, 'Trabalho'),
(2, 'Pensão'),
(3, 'RSI'),
(4, 'Subsídio de desemprego'),
(5, 'Subsídio de invalidez'),
(6, 'Apoio social'),
(7, 'Sem rendimento');

-- NACIONALIDADE
INSERT INTO NACIONALIDADE (ID_NACIONALIDADE, DESCRICAO_NACIONALIDADE) VALUES
(1, 'Portuguesa'),
(2, 'Brasileira'),
(3, 'Cabo-verdiana'),
(4, 'Ucraniana'),
(5, 'Angolana'),
(6, 'Guineense'),
(7, 'Outra');

-- TIPOLOGIA_AGREGADO_FAMILIAR
INSERT INTO TIPOLOGIA_AGREGADO_FAMILIAR (ID_TIPOLOGIA, DESCRICAO_TIPOLOGIA) VALUES
(1, 'Unipessoal'),
(2, 'Casal sem filhos'),
(3, 'Casal com filhos'),
(4, 'Monoparental'),
(5, 'Alargado'),
(6, 'Pessoas s/ relação familiar');

-- SITUACAO_HABITACIONAL
INSERT INTO SITUACAO_HABITACIONAL (ID_SITUACAO_HABITACIONAL, DESCRICAO_SITUACAO_HABITACIONAL) VALUES
(1, 'Estável'),
(2, 'Instável'),
(3, 'Sem-abrigo'),
(4, 'Habitação precária');

-- TIPO_INTERVENCAO
INSERT INTO TIPO_INTERVENCAO (ID_TIPO_INTERVENCAO, NOME_TIPO_INTERVENCAO) VALUES
(1, 'Atendimento'),
(2, 'Encaminhamento'),
(3, 'Acompanhamento'),
(4, 'Apoio material'),
(5, 'Ação comunitária'),
(6, 'Visita domiciliária');

-- ENTIDADE
INSERT INTO ENTIDADE (ID_ENTIDADE, NOME_ENTIDADE) VALUES
(1, 'Junta de Freguesia'),
(2, 'IPSS - Centro Social'),
(3, 'SNS - Centro de Saúde'),
(4, 'Segurança Social'),
(5, 'Banco Alimentar'),
(6, 'Câmara Municipal'),
(7, 'Cruz Vermelha'),
(8, 'GNR - Núcleo de Apoio'),
(9, 'Farmácia Solidária');

-- PROGRAMA
INSERT INTO PROGRAMA (ID_PROGRAMA, PROGRAMA) VALUES
(1, 'ABEM - Acesso ao medicamento'),
(2, 'Apoio alimentar'),
(3, 'Prevenção de quedas'),
(4, 'Vacinação sénior'),
(5, 'Apoio psicológico'),
(6, 'Ajudas técnicas'),
(7, 'Banco de equipamentos'),
(8, 'Acompanhamento social');

-- TIPO_RESPOSTA
INSERT INTO TIPO_RESPOSTA (ID_TIPO_RESPOSTA, DESCRICAO_TIPO_RESPOSTA) VALUES
(1, 'Aceite'),
(2, 'Recusada'),
(3, 'Em espera'),
(4, 'Lista de espera'),
(5, 'Não se aplica');

-- PROBLEMATICAS_IDENTIFICADAS
INSERT INTO PROBLEMATICAS_IDENTIFICADAS (ID_PROBLEMATICA, NOME_PROBLEMATICA) VALUES
(1, 'Isolamento social'),
(2, 'Carência alimentar'),
(3, 'Endividamento'),
(4, 'Violência doméstica'),
(5, 'Saúde mental'),
(6, 'Dependência (álcool/drogas)'),
(7, 'Situação de sem-abrigo'),
(8, 'Problemas de acesso a serviços');

/*==============================================================*/
/* 2. INSERIR ADMINISTRADORES                                   */
/*==============================================================*/

INSERT INTO ADMINISTRADORES (ID_ADMINISTRADOR, NOME_ADMINISTRADOR, EMAIL_ADMINISTRADOR, PASSWORD_ADMINISTRADOR, CARGO_ADMINISTRADOR) VALUES
(1, 'Ana Silva', 'anasilva@gmail.com', '1234', 'Assistente Social');

/*==============================================================*/
/* 3. INSERIR UTENTES (geral)                                   */
/*==============================================================*/

-- UTENTES (tabela base)
INSERT INTO UTENTES (ID_UTENTE, ID_TIPO_UTENTE, ID_GENERO, ID_ZONA_UTENTE, NOME_UTENTE, DATA_NASCIMENTO, DATA_CRIACAO) VALUES
-- Utentes socioeconómicos (tipo 1)
(1, 1, 2, 1, 'Maria do Carmo Lopes', '2010-05-01', '2022-01-01'),
(2, 1, 1, 3, 'António José Ribeiro', '2003-01-07', '2022-05-20'),
(3, 1, 2, 2, 'Carla Susana Moreira', '2002-06-12', '2022-09-20'),
(4, 1, 1, 3, 'Joaquim Manuel Pinto', '1990-04-01', '2022-12-01'),
(5, 1, 2, 4, 'Teresa Isabel Gomes', '1999-01-20', '2023-01-02'),
(6, 1, 1, 6, 'Fernando Jorge Nunes', '1998-02-01', '2023-01-20'),
(7, 1, 2, 5, 'Luísa Maria Fernandes', '1995-04-23', '2024-02-20'),
(8, 1, 1, 7, 'Ricardo Miguel Costa', '1988-12-22', '2024-03-15'),
-- Utentes idosos (tipo 2)
(9, 2, 2, 1, 'Laura Beatriz Silva', '1945-12-01', '2024-03-16'),
(10, 2, 1, 2, 'Manuel Joaquim Santos', '1932-12-01', '2024-04-01'),
(11, 2, 2, 3, 'Alice da Conceição Pereira', '1952-08-08', '2024-04-05'),
(12, 2, 1, 4, 'José Augusto Ferreira', '1938-07-06', '2024-04-20'),
(13, 2, 2, 1, 'Amélia Rosa Martins', '1923-07-21', '2024-05-01'),
(14, 2, 1, 5, 'António Manuel Oliveira', '2005-11-05', '2024-05-03'),
(15, 2, 2, 6, 'Isabel Maria Rodrigues', '2004-09-14', '2024-05-10'),
(16, 2, 1, 7, 'Joaquim José Alves', '2006-03-02', '2025-05-13'),
(17, 2, 2, 2, 'Rosa Maria Nunes', '2000-01-25', '2026-01-02'),
(18, 2, 1, 3, 'Fernando Augusto Lopes', '2003-09-25', '2026-02-01');

/*==============================================================*/
/* 4. INSERIR UTENTES_SOCIO_ECONOMICAS                          */
/*==============================================================*/

INSERT INTO UTENTES_SOCIO_ECONOMICAS (
    ID_UTENTE, ID_NACIONALIDADE, ID_TIPOLOGIA, 
    ID_SITUACAO_HABITACIONAL, ID_SITUACAO_LABORAL, ID_TIPO_RENDIMENTO,
    RISCO_SOCIAL, OBSERVACOES_UTENTE, CRITERIO_RISCO
) VALUES
(1, 1, 4, 1, 1, 1, FALSE, 'Família monoparental, emprego estável', NULL),
(2, 1, 1, 2, 2, 3, TRUE, 'Desempregado há 8 meses, risco de execução hipotecária', 'Desemprego prolongado, sem poupanças'),
(3, 2, 3, 1, 1, 1, FALSE, 'Imigrante brasileira, trabalho na restauração', NULL),
(4, 1, 1, 2, 2, 3, TRUE, 'Sem rendimentos, RSI em processo', 'Sem-abrigo temporário'),
(5, 1, 4, 1, 1, 1, FALSE, 'Divorciada, dois filhos, trabalho estável', NULL),
(6, 3, 5, 2, 6, 6, TRUE, 'Trabalhador informal, agregado alargado', 'Trabalho precário, rendimentos insuficientes'),
(7, 4, 2, 1, 2, 4, TRUE, 'Refugiada ucraniana, subsídio', 'Deslocada, sem suporte familiar'),
(8, 1, 3, 1, 1, 1, FALSE, 'Jovem casal, ambos empregados', NULL);

/*==============================================================*/
/* 5. INSERIR UTENTES_IDOSOS                                    */
/*==============================================================*/

INSERT INTO UTENTES_IDOSOS (
    ID_UTENTE, ID_ESTADO_CIVIL, ID_GRAU_AUTONOMIA, ID_MOBILIDADE,
    ID_NIVEL_ISOLAMENTO, ID_RELACAO_FAMILIA, ID_FREQUENCIA_CONTACTO_SOCIAL,
    ID_TIPO_HABITACAO, VIVE_SOZINHO, CONTACTO_EMERGENCIA,
    FAMILIAR_REFERENCIA, MEDICACAO_DIARIA, DIFICULDADE_ACESSO_SAUDE,
    ACOMPANHAMENTO_REG, PARTICIPA_ATIVIDADES_FR, TRISTESA_DEPRESSAO,
    LUTO_RECENTE, AQUECIMENTO_ADEQ_INV, SEGURANCA, NECESSIDADE_ADPTACOES
) VALUES
-- ID 9 - Laura
(9, 5, 2, 2, 2, 2, 4, 1, TRUE, 912345678, 'Sobrinha - Ana', TRUE, FALSE, TRUE, FALSE, TRUE, TRUE, TRUE, 'Casa segura mas com escadas', 'Corrimão nas escadas'),
-- ID 10 - Manuel
(10, 5, 3, 4, 2, 3, 5, 2, TRUE, 923456789, 'Nenhum', TRUE, TRUE, FALSE, FALSE, FALSE, TRUE, FALSE, 'Casa antiga com más condições', 'WC adaptado e rampa'),
-- ID 11 - Alice
(11, 2, 1, 1, 1, 1, 2, 1, FALSE, 934567890, 'Filho - Pedro', FALSE, FALSE, TRUE, TRUE, FALSE, FALSE, TRUE, 'Casa segura', NULL),
-- ID 12 - José
(12, 5, 3, 4, 3, 3, 6, 2, TRUE, NULL, 'Nenhum', TRUE, TRUE, FALSE, FALSE, TRUE, TRUE, FALSE, 'Casa degradada, sem aquecimento', 'Múltiplas adaptações necessárias'),
-- ID 13 - Amélia
(13, 5, 1, 1, 2, 2, 3, 1, TRUE, 945678901, 'Filha - Carla', TRUE, FALSE, TRUE, TRUE, FALSE, TRUE, TRUE, 'Casa com tapetes perigosos', 'Remover tapetes'),
-- ID 14 - António
(14, 2, 2, 2, 2, 1, 2, 1, FALSE, 956789012, 'Esposa', TRUE, FALSE, TRUE, FALSE, FALSE, FALSE, TRUE, 'Casa adaptada', NULL),
-- ID 15 - Isabel
(15, 1, 1, 1, 1, 1, 2, 1, FALSE, 967890123, 'Irmã', FALSE, FALSE, TRUE, TRUE, FALSE, FALSE, TRUE, 'Casa segura', NULL),
-- ID 16 - Joaquim
(16, 5, 3, 4, 3, 3, 6, 2, TRUE, NULL, 'Nenhum', TRUE, TRUE, FALSE, FALSE, TRUE, FALSE, FALSE, 'Casa muito degradada', 'Realojamento urgente'),
-- ID 17 - Rosa
(17, 5, 2, 2, 2, 2, 3, 1, TRUE, 978901234, 'Filho - Miguel', TRUE, FALSE, TRUE, TRUE, TRUE, FALSE, TRUE, 'Casa com escadas', 'Apoio na medicação'),
-- ID 18 - Fernando
(18, 2, 2, 2, 2, 1, 3, 1, FALSE, 989012345, 'Filha - Joana', TRUE, FALSE, TRUE, FALSE, FALSE, FALSE, TRUE, 'Casa adaptada', NULL);

/*==============================================================*/
/* 6. INSERIR DADOS NAS TABELAS DE RELACIONAMENTO (N:N)         */
/*==============================================================*/

-- BARREIRAS_IDOSOS
INSERT INTO BARREIRAS_IDOSOS (ID_UTENTE, ID_BARREIRA_ARQUITETONICA) VALUES
(9, 1), (9, 2),
(10, 1), (10, 2), (10, 5),
(12, 1), (12, 2), (12, 5), (12, 6),
(13, 7),
(16, 1), (16, 2), (16, 5), (16, 6),
(17, 1);

-- DOENCAS_IDOSOS
INSERT INTO DOENCAS_IDOSOS (ID_UTENTE, ID_DOENCA_CRONICA) VALUES
(9, 1), (9, 5),
(10, 1), (10, 2), (10, 3), (10, 8),
(11, 5), (11, 9),
(12, 2), (12, 3), (12, 8), (12, 10),
(13, 1), (13, 5),
(14, 1), (14, 7),
(15, 9),
(16, 2), (16, 3), (16, 6),
(17, 1), (17, 5),
(18, 1), (18, 2);

-- FRAGILIDADE_IDOSO
INSERT INTO FRAGILIDADE_IDOSO (ID_UTENTE, ID_SINAL_FRAGILIDADE) VALUES
(9, 1), (9, 5),
(10, 1), (10, 2), (10, 3), (10, 7),
(12, 2), (12, 3), (12, 7),
(13, 4),
(16, 2), (16, 3), (16, 7),
(17, 1), (17, 5);

-- ==============================================================
-- Dados de teste para a tabela TER (com datas)
-- ==============================================================

-- Utente 1: Isolamento social (ID 4) e Dependência (ID 5) – ambos ativos
INSERT INTO TER (ID_UTENTE, ID_PROBLEMATICA, DATA_INICIO, DATA_FIM) VALUES
(1, 4, '2024-01-15', NULL),
(1, 5, '2024-01-15', NULL);

-- Utente 2: Carência alimentar (2) e Endividamento (3) – ambos ativos
INSERT INTO TER (ID_UTENTE, ID_PROBLEMATICA, DATA_INICIO, DATA_FIM) VALUES
(2, 2, '2023-03-10', NULL),
(2, 3, '2023-03-10', NULL);

-- Utente 3: Endividamento (3) e Saúde mental (6) – endividamento resolvido, saúde mental ativa
INSERT INTO TER (ID_UTENTE, ID_PROBLEMATICA, DATA_INICIO, DATA_FIM) VALUES
(3, 3, '2023-11-01', '2024-06-30'),
(3, 6, '2024-02-10', NULL);

-- Utente 4: Isolamento social (1), Carência alimentar (2), Endividamento (3), Violência doméstica (7) – todos ativos
INSERT INTO TER (ID_UTENTE, ID_PROBLEMATICA, DATA_INICIO, DATA_FIM) VALUES
(4, 1, '2022-09-01', NULL),
(4, 2, '2022-09-01', NULL),
(4, 3, '2022-09-01', NULL),
(4, 7, '2023-05-20', NULL);

-- Utente 5: Saúde mental (6) e Problemas de acesso a serviços (8) – ambos resolvidos
INSERT INTO TER (ID_UTENTE, ID_PROBLEMATICA, DATA_INICIO, DATA_FIM) VALUES
(5, 6, '2023-08-15', NULL),
(5, 8, '2023-08-15', NULL);

-- Utente 6: Isolamento social (1), Carência alimentar (2), Endividamento (3), Problemas de acesso (8)
-- Endividamento reincidente: primeiro resolvido, depois ativo novamente
INSERT INTO TER (ID_UTENTE, ID_PROBLEMATICA, DATA_INICIO, DATA_FIM) VALUES
(6, 1, '2023-01-10', NULL),
(6, 2, '2023-01-10', NULL),
(6, 3, '2023-01-10', '2024-03-15'),   -- primeira ocorrência resolvida
(6, 3, '2024-08-01', NULL),            -- reincidência (ainda ativa)
(6, 8, '2024-02-20', NULL);

-- Utente 7: Isolamento social (1) e Problemas de acesso (8) – ambos resolvidos
INSERT INTO TER (ID_UTENTE, ID_PROBLEMATICA, DATA_INICIO, DATA_FIM) VALUES
(7, 1, '2023-12-01', NULL),
(7, 8, '2023-12-01', NULL);

-- Utente 8: Isolamento social (1) – ativo
INSERT INTO TER (ID_UTENTE, ID_PROBLEMATICA, DATA_INICIO, DATA_FIM) VALUES
(8, 1, '2024-05-01', NULL);

/*==============================================================*/
/* 7. INSERIR MEMBROS DO AGREGADO FAMILIAR                      */
/*==============================================================*/

INSERT INTO MEMBROS_AGREGADO_FAMILIAR (ID_MEMBRO, ID_UTENTE, NOME_MEMBRO, ANO_NASCIMENTO, GRAU_PARENTESCO) VALUES
(1, 1, 'Carlos Lopes', 2015, 'Filho'),
(2, 1, 'Sofia Lopes', 2018, 'Filha'),
(3, 3, 'Pedro Moreira', 2019, 'Filho'),
(4, 3, 'João Moreira', 1988, 'Cônjuge'),
(5, 5, 'Mariana Gomes', 2010, 'Filha'),
(6, 5, 'Rafael Gomes', 2015, 'Filho'),
(7, 6, 'Helena Nunes', 1980, 'Irmã'),
(8, 6, 'Miguel Nunes', 2005, 'Sobrinho'),
(9, 6, 'Ana Nunes', 2008, 'Sobrinha');

/*==============================================================*/
/* 8. INSERIR DESPESAS_FIXAS                                     */
/*==============================================================*/

INSERT INTO TIPO_DESPESA VALUES
(1, 'Renda'),
(2, 'Medicamentos'),
(3, 'Alimentação'),
(4, 'Habitacao');

INSERT INTO DESPESAS_FIXAS (ID_DESPESA, ID_UTENTE, ID_TIPO_DESPESA, VALOR_DESPESA) VALUES
(1, 1, 1, 450.00),
(2, 1, 2, 35.00),
(3, 2, 4, 320.00),
(4, 2, 3, 50.00),
(5, 3, 1, 550.00),
(6, 4, 4, 200.00),
(7, 5, 1, 600.00),
(8, 5, 2, 25.00),
(9, 6, 1, 400.00),
(10, 6, 1, 120.00),
(11, 7, 1, 450.00);

/*==============================================================*/
/* 9. INSERIR INTERVENCOES                                       */
/*==============================================================*/

INSERT INTO INTERVENCAO (ID_INTERVENCAO, ID_ADMINISTRADOR, ID_TIPO_INTERVENCAO, ID_ENTIDADE, ID_PROGRAMA, DATA_INTERVENCAO, OBSERVACOES_INTERVENCAO) VALUES
(1, 1, 1, 1, 8, '2026-01-10 10:30:00', 'Primeiro atendimento, levantamento de necessidades'),  -- Programa 8 = Acompanhamento social
(2, 1, 4, 5, 2, '2026-01-15 14:00:00', 'Entrega de cabaz alimentar'),  -- Programa 2 = Apoio alimentar
(3, 1, 2, 4, 8, '2026-01-20 09:15:00', 'Encaminhamento para Segurança Social'),  -- Programa 8
(4, 1, 3, 1, 8, '2026-01-22 11:30:00', 'Acompanhamento mensal'),  -- Programa 8
(5, 1, 5, 1, 5, '2026-01-25 15:00:00', 'Sessão de grupo - apoio psicológico'),  -- Programa 5 = Apoio psicológico
(6, 1, 4, 5, 2, '2026-02-01 10:00:00', 'Segunda entrega de cabaz'),  -- Programa 2
(7, 1, 2, 3, 4, '2026-02-03 09:30:00', 'Encaminhamento para vacinação'),  -- Programa 4 = Vacinação sénior
(8, 1, 3, 1, 8, '2026-02-05 14:30:00', 'Acompanhamento domiciliário'),  -- Programa 8
(9, 1, 6, 1, 8, '2026-02-08 11:00:00', 'Visita domiciliária - avaliação'),  -- Programa 8
(10, 1, 1, 1, 8, '2026-02-10 10:00:00', 'Atendimento presencial');  -- Programa 8

/*==============================================================*/
/* 10. INSERIR PARTICIPAR (utentes nas intervenções)            */
/*==============================================================*/

INSERT INTO PARTICIPAR (ID_UTENTE, ID_INTERVENCAO) VALUES
(1, 1), (1, 4),
(2, 1), (2, 2), (2, 3), (2, 4),
(3, 1), (3, 5),
(4, 1), (4, 2), (4, 3), (4, 6),
(5, 1), (5, 4),
(6, 1), (6, 2), (6, 3), (6, 6), (6, 8),
(7, 1), (7, 3), (7, 4), (7, 7);

/*==============================================================*/
/* 11. INSERIR ENCAMINHAMENTOS_REDE                             */
/*==============================================================*/

INSERT INTO ENCAMINHAMENTOS_REDE (ID_ENCAMINHAMENTO, ID_INTERVENCAO, ID_ENTIDADE, ID_TIPO_RESPOSTA, DESCRICAO_ENCAMINHAMENTO, ENCAMINHAMENTO_FEITO, DATA_RESPOSTA, TEMPO_RESPOSTA, OBSERVACOES_ENCAMINHAMENTO) VALUES
(1, 3, 5, 1, 'Apoio alimentar', TRUE, '2026-01-25', 5, 'Inserido no programa'),
(2, 7, 3, 1, 'Vacinação gripe', TRUE, '2026-02-10', 7, 'Vacinação agendada'),
(3, 9, 6, 2, 'Adaptação de WC', TRUE, '2026-02-15', 7, 'Pedido recusado - falta de orçamento');

/*==============================================================*/
/* 12. INSERIR CONTACTOS (idosos)                               */
/*==============================================================*/

INSERT INTO CONTACTO (ID_CONTACTO, ID_ADMINISTRADOR, ID_TIPO_CONTACTO, ID_FREQUENCIA_CONTACTO, ID_UTENTE, DATA_CONTACTO, OBSERVACOES_CONTACTO) VALUES
(1, 1, 1, 2, 9, '2026-02-05 11:00:00', 'Idosa bem disposta, medicação em dia'),
(2, 1, 2, 2, 9, '2026-02-12 10:30:00', 'Contacto telefónico, queixa de dores'),
(3, 1, 1, 2, 10, '2026-02-06 14:00:00', 'Idoso acamado, precisa de fraldas'),
(4, 1, 1, 4, 11, '2026-02-07 11:30:00', 'Tudo ok, participou na atividade'),
(5, 1, 1, 2, 12, '2026-02-08 15:00:00', 'Situação degradada, precisa de apoio urgente'),
(6, 1, 1, 3, 13, '2026-02-09 10:00:00', 'Fez queda, mas sem gravidade'),
(7, 1, 2, 2, 14, '2026-02-10 16:30:00', 'Contacto com familiar, estável'),
(8, 1, 1, 2, 15, '2026-02-11 09:30:00', 'Participou no grupo, animada'),
(9, 1, 1, 1, 16, '2026-02-12 14:00:00', 'Situação de emergência, sem alimentos'),
(10, 1, 1, 3, 17, '2026-02-13 11:00:00', 'Acompanhamento regular, ok'),
(11, 1, 2, 3, 18, '2026-02-14 15:30:00', 'Contacto telefónico, estável');

/*==============================================================*/
/* 13. INSERIR QUEDAS_IDOSO                                     */
/*==============================================================*/

INSERT INTO QUEDAS_IDOSO (ID_QUEDA, ID_UTENTE, DATA_QUEDA, OBSERVACOES_QUEDA) VALUES
(1, 9, '2026-01-15', 'Queda na rua, sem fraturas'),
(2, 10, '2025-12-10', 'Queda da cama'),
(3, 13, '2026-02-01', 'Queda em casa, escoriações'),
(4, 13, '2026-02-10', 'Nova queda, mesma semana'),
(5, 16, '2026-01-20', 'Queda no quarto');

-- ESCALAO_RENDIMENTOS
INSERT INTO ESCALAO_RENDIMENTOS (ID_ESCALAO, ID_UTENTE, TIPO_ESCALAO, VALOR_EXATO) VALUES
(1, 1, 'A', 500),
(2, 2, 'B', 1000),
(3, 3, 'C', 1500),
(4, 1, 'D', 2000),
(5, 2, 'E', 3000);

-- ATIVIDADES_DIARIA (AVD)
INSERT INTO ATIVIDADES_DIARIA (ID_ATIVIDADE_DIARIA, ID_UTENTE, DESCRICAO_ATIVIDADE_DIARIA) VALUES
(1, 9, 'Alimentação'),
(2, 10, 'Higiene pessoal'),
(3, 11, 'Vestuário'),
(4, 12, 'Gestão da medicação'),
(5, 13, 'Mobilidade dentro de casa'),
(6, 14, 'Preparação de refeições'),
(7, 15, 'Limpeza doméstica'),
(8, 16, 'Gestão financeira');
/*==============================================================*/
/* FIM DO SCRIPT DE DADOS DE TESTE                              */
/*==============================================================*/