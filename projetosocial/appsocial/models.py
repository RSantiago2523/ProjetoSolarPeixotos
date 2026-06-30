from django.db import models

class Administradores(models.Model):
    id_administrador = models.BigAutoField(primary_key=True)
    nome_administrador = models.CharField(max_length=50, blank=True, null=True)
    email_administrador = models.CharField(max_length=50, blank=True, null=True)
    password_administrador = models.CharField(max_length=128, blank=True, null=True)
    cargo_administrador = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'administradores'

    def __str__(self):
        return self.nome_administrador or str(self.id_administrador)

class BarreirasArquitetonicas(models.Model):
    id_barreira_arquitetonica = models.BigAutoField(primary_key=True)
    descricao_barreira_arquitetonica = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'barreiras_arquitetonicas'

    def __str__(self):
        return self.descricao_barreira_arquitetonica or str(self.id_barreira_arquitetonica)


class BarreirasIdosos(models.Model):
    id_utente = models.ForeignKey('UtentesIdosos', models.PROTECT, db_column='id_utente')
    id_barreira_arquitetonica = models.ForeignKey(BarreirasArquitetonicas, models.PROTECT, db_column='id_barreira_arquitetonica')

    class Meta:
        managed = False
        db_table = 'barreiras_idosos'
        unique_together = (('id_utente', 'id_barreira_arquitetonica'),)


class Contacto(models.Model):
    id_contacto = models.BigAutoField(primary_key=True)
    id_administrador = models.ForeignKey(Administradores, models.PROTECT, db_column='id_administrador')
    id_tipo_contacto = models.ForeignKey('TipoContacto', models.PROTECT, db_column='id_tipo_contacto')
    id_frequencia_contacto = models.ForeignKey('FrequenciaContacto', models.PROTECT, db_column='id_frequencia_contacto')
    id_utente = models.ForeignKey('UtentesIdosos', models.PROTECT, db_column='id_utente')
    data_contacto = models.DateTimeField(blank=True, null=True)
    observacoes_contacto = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contacto'


class DespesasFixas(models.Model):
    id_despesa = models.BigAutoField(primary_key=True)
    id_tipo_despesa = models.ForeignKey('TipoDespesa', models.PROTECT, db_column='id_tipo_despesa')
    id_utente = models.ForeignKey('UtentesSocioEconomicas', models.PROTECT, db_column='id_utente')
    valor_despesa = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'despesas_fixas'


class DoencasCronicas(models.Model):
    id_doenca_cronica = models.BigAutoField(primary_key=True)
    descricao_doenca_cronica = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'doencas_cronicas'

    def __str__(self):
        return self.descricao_doenca_cronica or str(self.id_doenca_cronica)


class DoencasIdosos(models.Model):
    id_utente = models.ForeignKey('UtentesIdosos', models.PROTECT, db_column='id_utente')
    id_doenca_cronica = models.ForeignKey(DoencasCronicas, models.PROTECT, db_column='id_doenca_cronica')

    class Meta:
        managed = False
        db_table = 'doencas_idosos'
        unique_together = (('id_utente', 'id_doenca_cronica'),)


class EncaminhamentosRede(models.Model):
    id_encaminhamento = models.BigAutoField(primary_key=True)
    id_intervencao = models.ForeignKey('Intervencao', models.PROTECT, db_column='id_intervencao')
    id_entidade = models.ForeignKey('Entidade', models.PROTECT, db_column='id_entidade')
    id_tipo_resposta = models.ForeignKey('TipoResposta', models.PROTECT, db_column='id_tipo_resposta', blank=True, null=True)
    descricao_encaminhamento = models.TextField(blank=True, null=True)
    encaminhamento_feito = models.BooleanField(blank=True, null=True)
    data_resposta = models.DateTimeField(blank=True, null=True)
    tempo_resposta = models.IntegerField(blank=True, null=True)
    observacoes_encaminhamento = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'encaminhamentos_rede'


class Entidade(models.Model):
    id_entidade = models.BigAutoField(primary_key=True)
    nome_entidade = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'entidade'

    def __str__(self):
        return self.nome_entidade or str(self.id_entidade)


class EscalaoRendimentos(models.Model):
    id_escalao = models.BigAutoField(primary_key=True)
    id_utente = models.ForeignKey('UtentesSocioEconomicas', models.PROTECT, db_column='id_utente')
    tipo_escalao = models.CharField(max_length=50, blank=True, null=True)
    valor_exato = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'escalao_rendimentos'


class EstadoCivil(models.Model):
    id_estado_civil = models.BigAutoField(primary_key=True)
    descricao_estado_civil = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'estado_civil'

    def __str__(self):
        return self.descricao_estado_civil or str(self.id_estado_civil)


class FragilidadeIdoso(models.Model):
    id_utente = models.ForeignKey('UtentesIdosos', models.PROTECT, db_column='id_utente')
    id_sinal_fragilidade = models.ForeignKey('SinaisFragilidade', models.PROTECT, db_column='id_sinal_fragilidade')

    class Meta:
        managed = False
        db_table = 'fragilidade_idoso'
        unique_together = (('id_utente', 'id_sinal_fragilidade'),)


class FrequenciaContacto(models.Model):
    id_frequencia_contacto = models.BigAutoField(primary_key=True)
    descricao_frequencia_contacto = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'frequencia_contacto'

    def __str__(self):
        return self.descricao_frequencia_contacto or str(self.id_frequencia_contacto)


class FrequenciaContactoSocial(models.Model):
    id_frequencia_contacto_social = models.BigAutoField(primary_key=True)
    descricao_frequencia_contacto_social = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'frequencia_contacto_social'

    def __str__(self):
        return self.descricao_frequencia_contacto_social or str(self.id_frequencia_contacto_social)


class Genero(models.Model):
    id_genero = models.BigAutoField(primary_key=True)
    descricao_genero = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'genero'

    def __str__(self):
        return self.descricao_genero or str(self.id_genero)


class GrauAutonomia(models.Model):
    id_grau_autonomia = models.BigAutoField(primary_key=True)
    nome_grau_autonomia = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'grau_autonomia'

    def __str__(self):
        return self.nome_grau_autonomia or str(self.id_grau_autonomia)


class Intervencao(models.Model):
    id_intervencao = models.BigAutoField(primary_key=True)
    id_administrador = models.ForeignKey(Administradores, models.PROTECT, db_column='id_administrador')
    id_tipo_intervencao = models.ForeignKey('TipoIntervencao', models.PROTECT, db_column='id_tipo_intervencao')
    id_entidade = models.ForeignKey(Entidade, models.PROTECT, db_column='id_entidade')
    id_programa = models.ForeignKey('Programa', models.PROTECT, db_column='id_programa')
    data_intervencao = models.DateTimeField(blank=True, null=True)
    observacoes_intervencao = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'intervencao'


class MembrosAgregadoFamiliar(models.Model):
    id_membro = models.BigAutoField(primary_key=True)
    id_utente = models.ForeignKey('UtentesSocioEconomicas', models.PROTECT, db_column='id_utente')
    nome_membro = models.CharField(max_length=50, blank=True, null=True)
    ano_nascimento = models.IntegerField(blank=True, null=True)
    grau_parentesco = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'membros_agregado_familiar'


class Mobilidade(models.Model):
    id_mobilidade = models.BigAutoField(primary_key=True)
    nome_mobilidade = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mobilidade'

    def __str__(self):
        return self.nome_mobilidade or str(self.id_mobilidade)


class Nacionalidade(models.Model):
    id_nacionalidade = models.BigAutoField(primary_key=True)
    descricao_nacionalidade = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nacionalidade'

    def __str__(self):
        return self.descricao_nacionalidade or str(self.id_nacionalidade)


class NivelIsolamento(models.Model):
    id_nivel_isolamento = models.BigAutoField(primary_key=True)
    nivel_isolamento = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nivel_isolamento'

    def __str__(self):
        return self.nivel_isolamento or str(self.id_nivel_isolamento)


class Participar(models.Model):
    id_utente = models.ForeignKey('UtentesSocioEconomicas', models.PROTECT, db_column='id_utente')
    id_intervencao = models.ForeignKey(Intervencao, models.PROTECT, db_column='id_intervencao')

    class Meta:
        managed = False
        db_table = 'participar'
        unique_together = (('id_utente', 'id_intervencao'),)


class ProblematicasIdentificadas(models.Model):
    id_problematica = models.BigAutoField(primary_key=True)
    nome_problematica = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'problematicas_identificadas'

    def __str__(self):
        return self.nome_problematica or str(self.id_problematica)


class Programa(models.Model):
    id_programa = models.BigAutoField(primary_key=True)
    programa = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'programa'

    def __str__(self):
        return self.programa or str(self.id_programa)


class QuedasIdoso(models.Model):
    id_queda = models.BigAutoField(primary_key=True)
    id_utente = models.ForeignKey('UtentesIdosos', models.PROTECT, db_column='id_utente')
    data_queda = models.DateField(blank=True, null=True)
    observacoes_queda = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'quedas_idoso'


class RelacaoFamilia(models.Model):
    id_relacao_familia = models.BigAutoField(primary_key=True)
    descricao_relacao_familia = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'relacao_familia'

    def __str__(self):
        return self.descricao_relacao_familia or str(self.id_relacao_familia)


class SinaisFragilidade(models.Model):
    id_sinal_fragilidade = models.BigAutoField(primary_key=True)
    descricao_fragilidade = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sinais_fragilidade'

    def __str__(self):
        return self.descricao_fragilidade or str(self.id_sinal_fragilidade)


class SituacaoHabitacional(models.Model):
    id_situacao_habitacional = models.BigAutoField(primary_key=True)
    descricao_situacao_habitacional = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'situacao_habitacional'

    def __str__(self):
        return self.descricao_situacao_habitacional or str(self.id_situacao_habitacional)


class SituacaoLaboral(models.Model):
    id_situacao_laboral = models.BigAutoField(primary_key=True)
    descricao_situacao_laboral = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'situacao_laboral'

    def __str__(self):
        return self.descricao_situacao_laboral or str(self.id_situacao_laboral)


class Ter(models.Model):
    id_ter = models.BigAutoField(primary_key=True)
    id_utente = models.ForeignKey('UtentesSocioEconomicas', models.PROTECT, db_column='id_utente')
    id_problematica = models.ForeignKey(ProblematicasIdentificadas, models.PROTECT, db_column='id_problematica')
    data_inicio = models.DateField()
    data_fim = models.DateField(blank=True, null=True)
    id_intervencao = models.ForeignKey('Intervencao', models.PROTECT, db_column='id_intervencao', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ter'


class TipoContacto(models.Model):
    id_tipo_contacto = models.BigAutoField(primary_key=True)
    nome_tipo_contacto = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipo_contacto'

    def __str__(self):
        return self.nome_tipo_contacto or str(self.id_tipo_contacto)


class TipoDespesa(models.Model):
    id_tipo_despesa = models.BigAutoField(primary_key=True)
    descricao_tipo_despesa = models.CharField(max_length=75, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipo_despesa'

    def __str__(self):
        return self.descricao_tipo_despesa or str(self.id_tipo_despesa)


class TipoHabitacao(models.Model):
    id_tipo_habitacao = models.BigAutoField(primary_key=True)
    descricao_tipo = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipo_habitacao'

    def __str__(self):
        return self.descricao_tipo or str(self.id_tipo_habitacao)


class TipoIntervencao(models.Model):
    id_tipo_intervencao = models.BigAutoField(primary_key=True)
    nome_tipo_intervencao = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipo_intervencao'

    def __str__(self):
        return self.nome_tipo_intervencao or str(self.id_tipo_intervencao)


class TipoRendimento(models.Model):
    id_tipo_rendimento = models.BigAutoField(primary_key=True)
    nome_tipo_rendimento = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipo_rendimento'

    def __str__(self):
        return self.nome_tipo_rendimento or str(self.id_tipo_rendimento)


class TipoResposta(models.Model):
    id_tipo_resposta = models.BigAutoField(primary_key=True)
    descricao_tipo_resposta = models.CharField(max_length=75, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipo_resposta'

    def __str__(self):
        return self.descricao_tipo_resposta or str(self.id_tipo_resposta)


class TipoUtente(models.Model):
    id_tipo_utente = models.BigAutoField(primary_key=True)
    nome_tipo_utente = models.CharField(max_length=50, blank=True, null=True)
    descricao_tipo_utente = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipo_utente'

    def __str__(self):
        return self.nome_tipo_utente or str(self.id_tipo_utente)


class TipologiaAgregadoFamiliar(models.Model):
    id_tipologia = models.BigAutoField(primary_key=True)
    descricao_tipologia = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tipologia_agregado_familiar'

    def __str__(self):
        return self.descricao_tipologia or str(self.id_tipologia)


class Utentes(models.Model):
    id_utente = models.BigAutoField(primary_key=True)   # ← alterado
    id_tipo_utente = models.ForeignKey(TipoUtente, models.PROTECT, db_column='id_tipo_utente')
    id_genero = models.ForeignKey(Genero, models.PROTECT, db_column='id_genero')
    id_zona_utente = models.ForeignKey('ZonaUtente', models.PROTECT, db_column='id_zona_utente')
    nome_utente = models.CharField(max_length=50, blank=True, null=True)
    data_nascimento = models.DateField(blank=True, null=True)
    data_criacao = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'utentes'


class UtentesIdosos(models.Model):
    id_utente = models.OneToOneField(Utentes, models.PROTECT, db_column='id_utente', primary_key=True)
    id_estado_civil = models.ForeignKey(EstadoCivil, models.PROTECT, db_column='id_estado_civil')
    id_grau_autonomia = models.ForeignKey(GrauAutonomia, models.PROTECT, db_column='id_grau_autonomia')
    id_mobilidade = models.ForeignKey(Mobilidade, models.PROTECT, db_column='id_mobilidade')
    id_nivel_isolamento = models.ForeignKey(NivelIsolamento, models.PROTECT, db_column='id_nivel_isolamento')
    id_relacao_familia = models.ForeignKey(RelacaoFamilia, models.PROTECT, db_column='id_relacao_familia')
    id_frequencia_contacto_social = models.ForeignKey(FrequenciaContactoSocial, models.PROTECT, db_column='id_frequencia_contacto_social')
    id_tipo_habitacao = models.ForeignKey(TipoHabitacao, models.PROTECT, db_column='id_tipo_habitacao')
    vive_sozinho = models.BooleanField(blank=True, null=True)
    contacto_emergencia = models.CharField(max_length=50, blank=True, null=True)
    familiar_referencia = models.TextField(blank=True, null=True)
    medicacao_diaria = models.BooleanField(blank=True, null=True)
    dificuldade_acesso_saude = models.BooleanField(blank=True, null=True)
    acompanhamento_reg = models.BooleanField(blank=True, null=True)
    participa_atividades_fr = models.BooleanField(blank=True, null=True)
    tristesa_depressao = models.BooleanField(blank=True, null=True)
    luto_recente = models.BooleanField(blank=True, null=True)
    aquecimento_adeq_inv = models.BooleanField(blank=True, null=True)
    seguranca = models.TextField(blank=True, null=True)
    necessidade_adptacoes = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'utentes_idosos'

    def __str__(self):
        return f"Idoso: {self.id_utente}"


class UtentesSocioEconomicas(models.Model):
    id_utente = models.OneToOneField(Utentes, models.PROTECT, db_column='id_utente', primary_key=True)
    id_nacionalidade = models.ForeignKey(Nacionalidade, models.PROTECT, db_column='id_nacionalidade')
    id_tipologia = models.ForeignKey(TipologiaAgregadoFamiliar, models.PROTECT, db_column='id_tipologia')
    id_situacao_habitacional = models.ForeignKey(SituacaoHabitacional, models.PROTECT, db_column='id_situacao_habitacional')
    id_situacao_laboral = models.ForeignKey(SituacaoLaboral, models.PROTECT, db_column='id_situacao_laboral')
    id_tipo_rendimento = models.ForeignKey(TipoRendimento, models.PROTECT, db_column='id_tipo_rendimento')
    risco_social = models.BooleanField(blank=True, null=True)
    observacoes_utente = models.TextField(blank=True, null=True)
    criterio_risco = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'utentes_socio_economicas'

    def __str__(self):
        return f"SocioEcon: {self.id_utente}"


class ZonaUtente(models.Model):
    id_zona_utente = models.BigAutoField(primary_key=True)
    descricao_zona_utente = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'zona_utente'

    def __str__(self):
        return self.descricao_zona_utente or str(self.id_zona_utente)

class AtividadesDiaria(models.Model):
    id_atividade_diaria = models.BigAutoField(primary_key=True)
    id_utente = models.ForeignKey(UtentesIdosos, models.PROTECT, db_column='id_utente')
    descricao_atividade_diaria = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'atividades_diaria'

    def __str__(self):
        return self.descricao_atividade_diaria or str(self.id_atividade_diaria)