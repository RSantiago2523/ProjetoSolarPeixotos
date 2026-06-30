/*==============================================================*/
/* DBMS name:      PostgreSQL 14.x                              */
/* Created on:     24/03/2026 17:27:49                          */
/*==============================================================*/
/*==============================================================*/
/* DROPS ORDENADOS + IF EXISTS                                  */
/*==============================================================*/
DROP TABLE IF EXISTS historico_idoso;
DROP TABLE IF EXISTS HISTORICO_UTENTE_SOCIOECONOMICO;
DROP TABLE IF EXISTS TER;
DROP TABLE IF EXISTS PARTICIPAR;
DROP TABLE IF EXISTS ENCAMINHAMENTOS_REDE;
DROP TABLE IF EXISTS CONTACTO;
DROP TABLE IF EXISTS INTERVENCAO;
DROP TABLE IF EXISTS ATIVIDADES_DIARIA;
DROP TABLE IF EXISTS BARREIRAS_IDOSOS;
DROP TABLE IF EXISTS DOENCAS_IDOSOS;
DROP TABLE IF EXISTS FRAGILIDADE_IDOSO;
DROP TABLE IF EXISTS QUEDAS_IDOSO;
DROP TABLE IF EXISTS DESPESAS_FIXAS;
DROP TABLE IF EXISTS ESCALAO_RENDIMENTOS;
DROP TABLE IF EXISTS MEMBROS_AGREGADO_FAMILIAR;
DROP TABLE IF EXISTS UTENTES_IDOSOS;
DROP TABLE IF EXISTS UTENTES_SOCIO_ECONOMICAS;
DROP TABLE IF EXISTS UTENTES;
DROP TABLE IF EXISTS ADMINISTRADORES;
DROP TABLE IF EXISTS TIPO_CONTACTO;
DROP TABLE IF EXISTS FREQUENCIA_CONTACTO;
DROP TABLE IF EXISTS TIPO_INTERVENCAO;
DROP TABLE IF EXISTS ENTIDADE;
DROP TABLE IF EXISTS PROGRAMA;
DROP TABLE IF EXISTS TIPO_RESPOSTA;

DROP TABLE IF EXISTS BARREIRAS_ARQUITETONICAS;
DROP TABLE IF EXISTS DOENCAS_CRONICAS;
DROP TABLE IF EXISTS SINAIS_FRAGILIDADE;
DROP TABLE IF EXISTS PROBLEMATICAS_IDENTIFICADAS;

DROP TABLE IF EXISTS TIPO_DESPESA;
DROP TABLE IF EXISTS NACIONALIDADE;
DROP TABLE IF EXISTS TIPOLOGIA_AGREGADO_FAMILIAR;
DROP TABLE IF EXISTS SITUACAO_HABITACIONAL;
DROP TABLE IF EXISTS SITUACAO_LABORAL;
DROP TABLE IF EXISTS TIPO_RENDIMENTO;

DROP TABLE IF EXISTS ESTADO_CIVIL;
DROP TABLE IF EXISTS GRAU_AUTONOMIA;
DROP TABLE IF EXISTS MOBILIDADE;
DROP TABLE IF EXISTS NIVEL_ISOLAMENTO;
DROP TABLE IF EXISTS RELACAO_FAMILIA;
DROP TABLE IF EXISTS FREQUENCIA_CONTACTO_SOCIAL;
DROP TABLE IF EXISTS TIPO_HABITACAO;

DROP TABLE IF EXISTS TIPO_UTENTE;
DROP TABLE IF EXISTS GENERO;
DROP TABLE IF EXISTS ZONA_UTENTE;
/*==============================================================*/
/* Table: ADMINISTRADORES                                       */
/*==============================================================*/
create table ADMINISTRADORES (
   ID_ADMINISTRADOR     bigserial              not null,
   NOME_ADMINISTRADOR   varchar(50),
   EMAIL_ADMINISTRADOR  varchar(50),
   PASSWORD_ADMINISTRADOR varchar(50),
   CARGO_ADMINISTRADOR  varchar(50),
   constraint PK_ADMINISTRADORES primary key (ID_ADMINISTRADOR)
);

/*==============================================================*/
/* Table: ESTADO_CIVIL                                          */
/*==============================================================*/
create table ESTADO_CIVIL (
   ID_ESTADO_CIVIL      bigserial              not null,
   DESCRICAO_ESTADO_CIVIL varchar(50),
   constraint PK_ESTADO_CIVIL primary key (ID_ESTADO_CIVIL)
);

/*==============================================================*/
/* Table: GRAU_AUTONOMIA                                        */
/*==============================================================*/
create table GRAU_AUTONOMIA (
   ID_GRAU_AUTONOMIA    bigserial              not null,
   NOME_GRAU_AUTONOMIA  varchar(50),
   constraint PK_GRAU_AUTONOMIA primary key (ID_GRAU_AUTONOMIA)
);

/*==============================================================*/
/* Table: MOBILIDADE                                            */
/*==============================================================*/
create table MOBILIDADE (
   ID_MOBILIDADE        bigserial              not null,
   NOME_MOBILIDADE      varchar(50),
   constraint PK_MOBILIDADE primary key (ID_MOBILIDADE)
);

/*==============================================================*/
/* Table: NIVEL_ISOLAMENTO                                      */
/*==============================================================*/
create table NIVEL_ISOLAMENTO (
   ID_NIVEL_ISOLAMENTO  bigserial              not null,
   NIVEL_ISOLAMENTO     varchar(50),
   constraint PK_NIVEL_ISOLAMENTO primary key (ID_NIVEL_ISOLAMENTO)
);

/*==============================================================*/
/* Table: RELACAO_FAMILIA                                       */
/*==============================================================*/
create table RELACAO_FAMILIA (
   ID_RELACAO_FAMILIA  bigserial              not null,
   DESCRICAO_RELACAO_FAMILIA varchar(50),
   constraint PK_RELACAO_FAMILIA primary key (ID_RELACAO_FAMILIA)
);

/*==============================================================*/
/* Table: FREQUENCIA_CONTACTO_SOCIAL                            */
/*==============================================================*/
create table FREQUENCIA_CONTACTO_SOCIAL (
   ID_FREQUENCIA_CONTACTO_SOCIAL bigserial              not null,
   DESCRICAO_FREQUENCIA_CONTACTO_SOCIAL varchar(50),
   constraint PK_FREQUENCIA_CONTACTO_SOCIAL primary key (ID_FREQUENCIA_CONTACTO_SOCIAL)
);

/*==============================================================*/
/* Table: TIPO_HABITACAO                                        */
/*==============================================================*/
create table TIPO_HABITACAO (
   ID_TIPO_HABITACAO    bigserial              not null,
   DESCRICAO_TIPO       varchar(100),
   constraint PK_TIPO_HABITACAO primary key (ID_TIPO_HABITACAO)
);

/*==============================================================*/
/* Table: TIPO_UTENTE                                           */
/*==============================================================*/
create table TIPO_UTENTE (
   ID_TIPO_UTENTE       bigserial              not null,
   NOME_TIPO_UTENTE     varchar(50),
   DESCRICAO_TIPO_UTENTE text,
   constraint PK_TIPO_UTENTE primary key (ID_TIPO_UTENTE)
);

/*==============================================================*/
/* Table: GENERO                                                */
/*==============================================================*/
create table GENERO (
   ID_GENERO            bigserial              not null,
   DESCRICAO_GENERO     varchar(50),
   constraint PK_GENERO primary key (ID_GENERO)
);

/*==============================================================*/
/* Table: ZONA_UTENTE                                           */
/*==============================================================*/
create table ZONA_UTENTE (
   ID_ZONA_UTENTE       bigserial              not null,
   DESCRICAO_ZONA_UTENTE text,
   constraint PK_ZONA_UTENTE primary key (ID_ZONA_UTENTE)
);

/*==============================================================*/
/* Table: UTENTES                                               */
/*==============================================================*/
create table UTENTES (
   ID_UTENTE            bigserial              not null,
   ID_TIPO_UTENTE       bigint              not null,
   ID_GENERO            bigint              not null,
   ID_ZONA_UTENTE       bigint              not null,
   NOME_UTENTE          varchar(50),
   DATA_NASCIMENTO      date,
   DATA_CRIACAO         date DEFAULT CURRENT_DATE,
   constraint PK_UTENTES primary key (ID_UTENTE),
   constraint FK_UTENTES_UTENTE_TI_TIPO_UTE foreign key (ID_TIPO_UTENTE)
      references TIPO_UTENTE (ID_TIPO_UTENTE)
      on delete restrict on update restrict,
   constraint FK_UTENTES_GENERO_UT_GENERO foreign key (ID_GENERO)
      references GENERO (ID_GENERO)
      on delete restrict on update restrict,
   constraint FK_UTENTES_ZONA_UTEN_ZONA_UTE foreign key (ID_ZONA_UTENTE)
      references ZONA_UTENTE (ID_ZONA_UTENTE)
      on delete restrict on update restrict
);

/*==============================================================*/
/* Table: UTENTES_IDOSOS                                        */
/*==============================================================*/
create table UTENTES_IDOSOS (
   ID_UTENTE            bigint              not null,
   ID_ESTADO_CIVIL      bigint              not null,
   ID_GRAU_AUTONOMIA    bigint              not null,
   ID_MOBILIDADE        bigint              not null,
   ID_NIVEL_ISOLAMENTO  bigint              not null,
   ID_RELACAO_FAMILIA   bigint              not null,
   ID_FREQUENCIA_CONTACTO_SOCIAL bigint              not null,
   ID_TIPO_HABITACAO    bigint              not null,
   VIVE_SOZINHO         boolean,
   CONTACTO_EMERGENCIA  varchar(50),
   FAMILIAR_REFERENCIA  text,
   MEDICACAO_DIARIA     boolean,
   DIFICULDADE_ACESSO_SAUDE boolean,
   ACOMPANHAMENTO_REG   boolean,
   PARTICIPA_ATIVIDADES_FR boolean,
   TRISTESA_DEPRESSAO   boolean,
   LUTO_RECENTE         boolean,
   AQUECIMENTO_ADEQ_INV boolean,
   SEGURANCA            text,
   NECESSIDADE_ADPTACOES text,
   constraint PK_UTENTES_IDOSOS primary key (ID_UTENTE),
   constraint FK_UTENTES__ESTADO_CI_ESTADO_C foreign key (ID_ESTADO_CIVIL)
      references ESTADO_CIVIL (ID_ESTADO_CIVIL)
      on delete restrict on update restrict,
   constraint FK_UTENTES__AUTONOMIA_GRAU_AUT foreign key (ID_GRAU_AUTONOMIA)
      references GRAU_AUTONOMIA (ID_GRAU_AUTONOMIA)
      on delete restrict on update restrict,
   constraint FK_UTENTES__MOBILIDAD_MOBILIDA foreign key (ID_MOBILIDADE)
      references MOBILIDADE (ID_MOBILIDADE)
      on delete restrict on update restrict,
   constraint FK_UTENTES__ISOLAMENT_NIVEL_IS foreign key (ID_NIVEL_ISOLAMENTO)
      references NIVEL_ISOLAMENTO (ID_NIVEL_ISOLAMENTO)
      on delete restrict on update restrict,
   constraint FK_UTENTES__FAMILIA_I_RELACAO_ foreign key (ID_RELACAO_FAMILIA)
      references RELACAO_FAMILIA (ID_RELACAO_FAMILIA)
      on delete restrict on update restrict,
   constraint FK_UTENTES__CONTACTO__FREQUENC foreign key (ID_FREQUENCIA_CONTACTO_SOCIAL)
      references FREQUENCIA_CONTACTO_SOCIAL (ID_FREQUENCIA_CONTACTO_SOCIAL)
      on delete restrict on update restrict,
   constraint FK_UTENTES__HABITACAO_TIPO_HAB foreign key (ID_TIPO_HABITACAO)
      references TIPO_HABITACAO (ID_TIPO_HABITACAO)
      on delete restrict on update restrict,
   constraint FK_UTENTES__SER2_UTENTES foreign key (ID_UTENTE)
      references UTENTES (ID_UTENTE)
      on delete restrict on update restrict
);

/*==============================================================*/
/* Table: ATIVIDADES_DIARIA                                     */
/*==============================================================*/
create table ATIVIDADES_DIARIA (
   ID_ATIVIDADE_DIARIA  bigserial              not null,
   ID_UTENTE            bigint              not null,
   DESCRICAO_ATIVIDADE_DIARIA text,
   constraint PK_ATIVIDADES_DIARIA primary key (ID_ATIVIDADE_DIARIA),
   constraint FK_ATIVIDAD_IDOSOS_AT_UTENTES_ foreign key (ID_UTENTE)
      references UTENTES_IDOSOS (ID_UTENTE)
      on delete restrict on update restrict
);

/*==============================================================*/
/* Table: BARREIRAS_ARQUITETONICAS                              */
/*==============================================================*/
create table BARREIRAS_ARQUITETONICAS (
   ID_BARREIRA_ARQUITETONICA bigserial              not null,
   DESCRICAO_BARREIRA_ARQUITETONICA text,
   constraint PK_BARREIRAS_ARQUITETONICAS primary key (ID_BARREIRA_ARQUITETONICA)
);

/*==============================================================*/
/* Table: BARREIRAS_IDOSOS                                      */
/*==============================================================*/
create table BARREIRAS_IDOSOS (
   ID_UTENTE            bigint              not null,
   ID_BARREIRA_ARQUITETONICA bigint              not null,
   constraint PK_BARREIRAS_IDOSOS primary key (ID_UTENTE, ID_BARREIRA_ARQUITETONICA),
   constraint FK_BARREIRA_BARREIRAS_UTENTES_ foreign key (ID_UTENTE)
      references UTENTES_IDOSOS (ID_UTENTE)
      on delete restrict on update restrict,
   constraint FK_BARREIRA_BARREIRAS_BARREIRA foreign key (ID_BARREIRA_ARQUITETONICA)
      references BARREIRAS_ARQUITETONICAS (ID_BARREIRA_ARQUITETONICA)
      on delete restrict on update restrict
);

/*==============================================================*/
/* Table: TIPO_CONTACTO                                         */
/*==============================================================*/
create table TIPO_CONTACTO (
   ID_TIPO_CONTACTO     bigserial              not null,
   NOME_TIPO_CONTACTO   varchar(100),
   constraint PK_TIPO_CONTACTO primary key (ID_TIPO_CONTACTO)
);

/*==============================================================*/
/* Table: FREQUENCIA_CONTACTO                                   */
/*==============================================================*/
create table FREQUENCIA_CONTACTO (
   ID_FREQUENCIA_CONTACTO bigserial              not null,
   DESCRICAO_FREQUENCIA_CONTACTO varchar(50),
   constraint PK_FREQUENCIA_CONTACTO primary key (ID_FREQUENCIA_CONTACTO)
);

/*==============================================================*/
/* Table: CONTACTO                                              */
/*==============================================================*/
create table CONTACTO (
   ID_CONTACTO          bigserial              not null,
   ID_ADMINISTRADOR     bigint              not null,
   ID_TIPO_CONTACTO     bigint              not null,
   ID_FREQUENCIA_CONTACTO bigint              not null,
   ID_UTENTE            bigint              not null,
   DATA_CONTACTO        timestamp,
   OBSERVACOES_CONTACTO text,
   constraint PK_CONTACTO primary key (ID_CONTACTO),
   constraint FK_CONTACTO_FAZER_ADMINIST foreign key (ID_ADMINISTRADOR)
      references ADMINISTRADORES (ID_ADMINISTRADOR)
      on delete restrict on update restrict,
   constraint FK_CONTACTO_INCLUIR_UTENTES_ foreign key (ID_UTENTE)
      references UTENTES_IDOSOS (ID_UTENTE)
      on delete restrict on update restrict,
   constraint FK_CONTACTO_CONTACTO__TIPO_CON foreign key (ID_TIPO_CONTACTO)
      references TIPO_CONTACTO (ID_TIPO_CONTACTO)
      on delete restrict on update restrict,
   constraint FK_CONTACTO_CONTACTO__FREQUENC foreign key (ID_FREQUENCIA_CONTACTO)
      references FREQUENCIA_CONTACTO (ID_FREQUENCIA_CONTACTO)
      on delete restrict on update restrict
);

/*==============================================================*/
/* Table: NACIONALIDADE                                         */
/*==============================================================*/
create table NACIONALIDADE (
   ID_NACIONALIDADE     bigserial              not null,
   DESCRICAO_NACIONALIDADE varchar(50),
   constraint PK_NACIONALIDADE primary key (ID_NACIONALIDADE)
);

/*==============================================================*/
/* Table: TIPOLOGIA_AGREGADO_FAMILIAR                           */
/*==============================================================*/
create table TIPOLOGIA_AGREGADO_FAMILIAR (
   ID_TIPOLOGIA         bigserial              not null,
   DESCRICAO_TIPOLOGIA  varchar(50),
   constraint PK_TIPOLOGIA_AGREGADO_FAMILIAR primary key (ID_TIPOLOGIA)
);

/*==============================================================*/
/* Table: SITUACAO_HABITACIONAL                                 */
/*==============================================================*/
create table SITUACAO_HABITACIONAL (
   ID_SITUACAO_HABITACIONAL bigserial              not null,
   DESCRICAO_SITUACAO_HABITACIONAL varchar(50),
   constraint PK_SITUACAO_HABITACIONAL primary key (ID_SITUACAO_HABITACIONAL)
);

/*==============================================================*/
/* Table: SITUACAO_LABORAL                                      */
/*==============================================================*/
create table SITUACAO_LABORAL (
   ID_SITUACAO_LABORAL  bigserial              not null,
   DESCRICAO_SITUACAO_LABORAL varchar(50),
   constraint PK_SITUACAO_LABORAL primary key (ID_SITUACAO_LABORAL)
);

/*==============================================================*/
/* Table: TIPO_RENDIMENTO                                       */
/*==============================================================*/
create table TIPO_RENDIMENTO (
   ID_TIPO_RENDIMENTO   bigserial              not null,
   NOME_TIPO_RENDIMENTO varchar(50),
   constraint PK_TIPO_RENDIMENTO primary key (ID_TIPO_RENDIMENTO)
);

/*==============================================================*/
/* Table: UTENTES_SOCIO_ECONOMICAS                              */
/*==============================================================*/
create table UTENTES_SOCIO_ECONOMICAS (
   ID_UTENTE            bigint              not null,
   ID_NACIONALIDADE     bigint              not null,
   ID_TIPOLOGIA         bigint              not null,
   ID_SITUACAO_HABITACIONAL bigint              not null,
   ID_SITUACAO_LABORAL  bigint              not null,
   ID_TIPO_RENDIMENTO   bigint              not null,
   RISCO_SOCIAL         boolean,
   OBSERVACOES_UTENTE   text,
   CRITERIO_RISCO       text,
   constraint PK_UTENTES_SOCIO_ECONOMICAS primary key (ID_UTENTE),
   constraint FK_UTENTES__NACIONALI_NACIONAL foreign key (ID_NACIONALIDADE)
      references NACIONALIDADE (ID_NACIONALIDADE)
      on delete restrict on update restrict,
   constraint FK_UTENTES__TIPOLOGIA_TIPOLOGI foreign key (ID_TIPOLOGIA)
      references TIPOLOGIA_AGREGADO_FAMILIAR (ID_TIPOLOGIA)
      on delete restrict on update restrict,
   constraint FK_UTENTES__HABITACIO_SITUACAO foreign key (ID_SITUACAO_HABITACIONAL)
      references SITUACAO_HABITACIONAL (ID_SITUACAO_HABITACIONAL)
      on delete restrict on update restrict,
   constraint FK_UTENTES__LABORAL_U_SITUACAO foreign key (ID_SITUACAO_LABORAL)
      references SITUACAO_LABORAL (ID_SITUACAO_LABORAL)
      on delete restrict on update restrict,
   constraint FK_UTENTES__RENDIMENT_TIPO_REN foreign key (ID_TIPO_RENDIMENTO)
      references TIPO_RENDIMENTO (ID_TIPO_RENDIMENTO)
      on delete restrict on update restrict,
   constraint FK_UTENTES__SER_UTENTES foreign key (ID_UTENTE)
      references UTENTES (ID_UTENTE)
      on delete restrict on update restrict
);

/*==============================================================*/
/* Table: TIPO_DESPESA                                          */
/*==============================================================*/
create table TIPO_DESPESA (
   ID_TIPO_DESPESA      bigserial              not null,
   DESCRICAO_TIPO_DESPESA varchar(75),
   constraint PK_TIPO_DESPESA primary key (ID_TIPO_DESPESA)
);

/*==============================================================*/
/* Table: DESPESAS_FIXAS                                        */
/*==============================================================*/
create table DESPESAS_FIXAS (
   ID_DESPESA           bigserial              not null,
   ID_TIPO_DESPESA      bigint              not null,
   ID_UTENTE            bigint              not null,
   VALOR_DESPESA        real,
   constraint PK_DESPESAS_FIXAS primary key (ID_DESPESA),
   constraint FK_DESPESAS_DESPESA_UTENTES_ foreign key (ID_UTENTE)
      references UTENTES_SOCIO_ECONOMICAS (ID_UTENTE)
      on delete restrict on update restrict,
   constraint FK_DESPESAS_DESPESA_T_TIPO_DES foreign key (ID_TIPO_DESPESA)
      references TIPO_DESPESA (ID_TIPO_DESPESA)
      on delete restrict on update restrict
);

/*==============================================================*/
/* Table: DOENCAS_CRONICAS                                      */
/*==============================================================*/
create table DOENCAS_CRONICAS (
   ID_DOENCA_CRONICA    bigserial              not null,
   DESCRICAO_DOENCA_CRONICA text,
   constraint PK_DOENCAS_CRONICAS primary key (ID_DOENCA_CRONICA)
);

/*==============================================================*/
/* Table: DOENCAS_IDOSOS                                        */
/*==============================================================*/
create table DOENCAS_IDOSOS (
   ID_UTENTE            bigint              not null,
   ID_DOENCA_CRONICA    bigint              not null,
   constraint PK_DOENCAS_IDOSOS primary key (ID_UTENTE, ID_DOENCA_CRONICA),
   constraint FK_DOENCAS__DOENCAS_I_UTENTES_ foreign key (ID_UTENTE)
      references UTENTES_IDOSOS (ID_UTENTE)
      on delete restrict on update restrict,
   constraint FK_DOENCAS__DOENCAS_I_DOENCAS_ foreign key (ID_DOENCA_CRONICA)
      references DOENCAS_CRONICAS (ID_DOENCA_CRONICA)
      on delete restrict on update restrict
);

/*==============================================================*/
/* Table: TIPO_INTERVENCAO                                      */
/*==============================================================*/
create table TIPO_INTERVENCAO (
   ID_TIPO_INTERVENCAO  bigserial              not null,
   NOME_TIPO_INTERVENCAO varchar(100),
   constraint PK_TIPO_INTERVENCAO primary key (ID_TIPO_INTERVENCAO)
);

/*==============================================================*/
/* Table: ENTIDADE                                              */
/*==============================================================*/
create table ENTIDADE (
   ID_ENTIDADE          bigserial              not null,
   NOME_ENTIDADE        varchar(50),
   constraint PK_ENTIDADE primary key (ID_ENTIDADE)
);

/*==============================================================*/
/* Table: PROGRAMA                                              */
/*==============================================================*/
create table PROGRAMA (
   ID_PROGRAMA          bigserial              not null,
   PROGRAMA             varchar(50),
   constraint PK_PROGRAMA primary key (ID_PROGRAMA)
);

/*==============================================================*/
/* Table: INTERVENCAO                                           */
/*==============================================================*/
create table INTERVENCAO (
   ID_INTERVENCAO       bigserial              not null,
   ID_ADMINISTRADOR     bigint              not null,
   ID_TIPO_INTERVENCAO  bigint              not null,
   ID_ENTIDADE          bigint              not null,
   ID_PROGRAMA          bigint              not null,
   DATA_INTERVENCAO     timestamp,
   OBSERVACOES_INTERVENCAO text,
   constraint PK_INTERVENCAO primary key (ID_INTERVENCAO),
   constraint FK_INTERVEN_REALIZAR_ADMINIST foreign key (ID_ADMINISTRADOR)
      references ADMINISTRADORES (ID_ADMINISTRADOR)
      on delete restrict on update restrict,
   constraint FK_INTERVEN_INTERVENC_TIPO_INT foreign key (ID_TIPO_INTERVENCAO)
      references TIPO_INTERVENCAO (ID_TIPO_INTERVENCAO)
      on delete restrict on update restrict,
   constraint FK_INTERVEN_ENTIDADE__ENTIDADE foreign key (ID_ENTIDADE)
      references ENTIDADE (ID_ENTIDADE)
      on delete restrict on update restrict,
   constraint FK_INTERVEN_PROGRAMA__PROGRAMA foreign key (ID_PROGRAMA)
      references PROGRAMA (ID_PROGRAMA)
      on delete restrict on update restrict
);

/*==============================================================*/
/* Table: TIPO_RESPOSTA                                         */
/*==============================================================*/
create table TIPO_RESPOSTA (
   ID_TIPO_RESPOSTA     bigserial              not null,
   DESCRICAO_TIPO_RESPOSTA varchar(75),
   constraint PK_TIPO_RESPOSTA primary key (ID_TIPO_RESPOSTA)
);

/*==============================================================*/
/* Table: ENCAMINHAMENTOS_REDE                                  */
/*==============================================================*/
create table ENCAMINHAMENTOS_REDE (
   ID_ENCAMINHAMENTO    bigserial              not null,
   ID_INTERVENCAO       bigint              not null,
   ID_ENTIDADE          bigint              not null,
   ID_TIPO_RESPOSTA     bigint,
   DESCRICAO_ENCAMINHAMENTO text,
   ENCAMINHAMENTO_FEITO boolean,
   DATA_RESPOSTA        timestamp,
   TEMPO_RESPOSTA       integer,
   OBSERVACOES_ENCAMINHAMENTO text,
   constraint PK_ENCAMINHAMENTOS_REDE primary key (ID_ENCAMINHAMENTO),
   constraint FK_ENCAMINH_ASSOCIAR_INTERVEN foreign key (ID_INTERVENCAO)
      references INTERVENCAO (ID_INTERVENCAO)
      on delete restrict on update restrict,
   constraint FK_ENCAMINH_ENTIDADE__ENTIDADE foreign key (ID_ENTIDADE)
      references ENTIDADE (ID_ENTIDADE)
      on delete restrict on update restrict,
   constraint FK_ENCAMINH_RESPOSTA__TIPO_RES foreign key (ID_TIPO_RESPOSTA)
      references TIPO_RESPOSTA (ID_TIPO_RESPOSTA)
      on delete restrict on update restrict
);

/*==============================================================*/
/* Table: ESCALAO_RENDIMENTOS                                   */
/*==============================================================*/
create table ESCALAO_RENDIMENTOS (
   ID_ESCALAO           bigserial              not null,
   ID_UTENTE            bigint              not null,
   TIPO_ESCALAO         varchar(50),
   VALOR_EXATO          real,
   constraint PK_ESCALAO_RENDIMENTOS primary key (ID_ESCALAO),
   constraint FK_ESCALAO__LIGAR_UTENTES_ foreign key (ID_UTENTE)
      references UTENTES_SOCIO_ECONOMICAS (ID_UTENTE)
      on delete restrict on update restrict
);

/*==============================================================*/
/* Table: SINAIS_FRAGILIDADE                                    */
/*==============================================================*/
create table SINAIS_FRAGILIDADE (
   ID_SINAL_FRAGILIDADE bigserial              not null,
   DESCRICAO_FRAGILIDADE varchar(100),
   constraint PK_SINAIS_FRAGILIDADE primary key (ID_SINAL_FRAGILIDADE)
);

/*==============================================================*/
/* Table: FRAGILIDADE_IDOSO                                     */
/*==============================================================*/
create table FRAGILIDADE_IDOSO (
   ID_UTENTE            bigint              not null,
   ID_SINAL_FRAGILIDADE bigint              not null,
   constraint PK_FRAGILIDADE_IDOSO primary key (ID_UTENTE, ID_SINAL_FRAGILIDADE),
   constraint FK_FRAGILID_FRAGILIDA_UTENTES_ foreign key (ID_UTENTE)
      references UTENTES_IDOSOS (ID_UTENTE)
      on delete restrict on update restrict,
   constraint FK_FRAGILID_FRAGILIDA_SINAIS_F foreign key (ID_SINAL_FRAGILIDADE)
      references SINAIS_FRAGILIDADE (ID_SINAL_FRAGILIDADE)
      on delete restrict on update restrict
);

/*==============================================================*/
/* Table: MEMBROS_AGREGADO_FAMILIAR                             */
/*==============================================================*/
create table MEMBROS_AGREGADO_FAMILIAR (
   ID_MEMBRO            bigserial              not null,
   ID_UTENTE            bigint              not null,
   NOME_MEMBRO          varchar(50),
   ANO_NASCIMENTO       integer,
   GRAU_PARENTESCO      varchar(50),
   constraint PK_MEMBROS_AGREGADO_FAMILIAR primary key (ID_MEMBRO),
   constraint FK_MEMBROS__AGREGAR_UTENTES_ foreign key (ID_UTENTE)
      references UTENTES_SOCIO_ECONOMICAS (ID_UTENTE)
      on delete restrict on update restrict
);

/*==============================================================*/
/* Table: PARTICIPAR                                            */
/*==============================================================*/
create table PARTICIPAR (
   ID_UTENTE            bigint              not null,
   ID_INTERVENCAO       bigint              not null,
   constraint PK_PARTICIPAR primary key (ID_UTENTE, ID_INTERVENCAO),
   constraint FK_PARTICIP_PARTICIPA_INTERVEN foreign key (ID_INTERVENCAO)
      references INTERVENCAO (ID_INTERVENCAO)
      on delete restrict on update restrict,
   constraint FK_PARTICIP_PARTICIPA_UTENTES_ foreign key (ID_UTENTE)
      references UTENTES_SOCIO_ECONOMICAS (ID_UTENTE)
      on delete restrict on update restrict
);

/*==============================================================*/
/* Table: PROBLEMATICAS_IDENTIFICADAS                           */
/*==============================================================*/
create table PROBLEMATICAS_IDENTIFICADAS (
   ID_PROBLEMATICA      bigserial              not null,
   NOME_PROBLEMATICA    varchar(30),
   constraint PK_PROBLEMATICAS_IDENTIFICADAS primary key (ID_PROBLEMATICA)
);

/*==============================================================*/
/* Table: QUEDAS_IDOSO                                          */
/*==============================================================*/
create table QUEDAS_IDOSO (
   ID_QUEDA             bigserial              not null,
   ID_UTENTE            bigint              not null,
   DATA_QUEDA           date,
   OBSERVACOES_QUEDA    text,
   constraint PK_QUEDAS_IDOSO primary key (ID_QUEDA),
   constraint FK_QUEDAS_I_IDOSO_QUE_UTENTES_ foreign key (ID_UTENTE)
      references UTENTES_IDOSOS (ID_UTENTE)
      on delete restrict on update restrict
);

/*==============================================================*/
/* Table: TER                                                   */
/*==============================================================*/
create table TER (
   ID_TER               bigserial              not null,
   ID_UTENTE            bigint              not null,
   ID_PROBLEMATICA      bigint              not null,
   DATA_INICIO          date                 not null,
   DATA_FIM             date,
   ID_INTERVENCAO       bigint,                 
   constraint PK_TER primary key (ID_TER),
   constraint FK_TER_TER2_UTENTES_ foreign key (ID_UTENTE)
      references UTENTES_SOCIO_ECONOMICAS (ID_UTENTE)
      on delete restrict on update restrict,
   constraint FK_TER_TER_PROBLEMA foreign key (ID_PROBLEMATICA)
      references PROBLEMATICAS_IDENTIFICADAS (ID_PROBLEMATICA)
      on delete restrict on update restrict,
   CONSTRAINT fk_ter_intervencao FOREIGN KEY (id_intervencao) REFERENCES intervencao(id_intervencao) ON DELETE SET NULL
);
CREATE TABLE HISTORICO_UTENTE_SOCIOECONOMICO (
    ID_HISTORICO        BIGSERIAL PRIMARY KEY,
    ID_UTENTE           BIGINT NOT NULL,
    DATA_HISTORICO      TIMESTAMP NOT NULL DEFAULT NOW(),
    USUARIO             VARCHAR(100),
    SNAPSHOT_JSON       JSONB NOT NULL,
    CONSTRAINT fk_hist_socio_utente FOREIGN KEY (ID_UTENTE) REFERENCES UTENTES (ID_UTENTE) ON DELETE RESTRICT ON UPDATE RESTRICT
);
CREATE TABLE IF NOT EXISTS historico_idoso (
    id_historico BIGSERIAL PRIMARY KEY,
    id_utente BIGINT NOT NULL,
    data_historico TIMESTAMP NOT NULL DEFAULT NOW(),
    usuario VARCHAR(100),
    snapshot_json JSONB NOT NULL,
    CONSTRAINT fk_hist_idoso_utente FOREIGN KEY (ID_UTENTE) REFERENCES UTENTES (ID_UTENTE) ON DELETE RESTRICT ON UPDATE RESTRICT
);