from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection, transaction
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import date
from django.utils import timezone
from ..import models
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from io import BytesIO
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.enums import TA_CENTER, TA_LEFT

@login_required
def socioeconomicos_pdf(request, id_utente):
    with connection.cursor() as cursor:
        # 1️⃣ Dados principais (igual)
        cursor.execute("""
            SELECT 
                u.ID_UTENTE,
                u.NOME_UTENTE,
                EXTRACT(YEAR FROM AGE(CURRENT_DATE, u.DATA_NASCIMENTO)) AS idade,
                n.DESCRICAO_NACIONALIDADE,
                z.DESCRICAO_ZONA_UTENTE,
                sh.DESCRICAO_SITUACAO_HABITACIONAL,
                sl.DESCRICAO_SITUACAO_LABORAL,
                tr.NOME_TIPO_RENDIMENTO,
                ta.DESCRICAO_TIPOLOGIA,
                usec.RISCO_SOCIAL,
                usec.OBSERVACOES_UTENTE,
                usec.CRITERIO_RISCO
            FROM UTENTES u
            JOIN UTENTES_SOCIO_ECONOMICAS usec ON u.ID_UTENTE = usec.ID_UTENTE
            JOIN NACIONALIDADE n ON usec.ID_NACIONALIDADE = n.ID_NACIONALIDADE
            JOIN ZONA_UTENTE z ON u.ID_ZONA_UTENTE = z.ID_ZONA_UTENTE
            JOIN SITUACAO_HABITACIONAL sh ON usec.ID_SITUACAO_HABITACIONAL = sh.ID_SITUACAO_HABITACIONAL
            JOIN SITUACAO_LABORAL sl ON usec.ID_SITUACAO_LABORAL = sl.ID_SITUACAO_LABORAL
            JOIN TIPO_RENDIMENTO tr ON usec.ID_TIPO_RENDIMENTO = tr.ID_TIPO_RENDIMENTO
            JOIN TIPOLOGIA_AGREGADO_FAMILIAR ta ON usec.ID_TIPOLOGIA = ta.ID_TIPOLOGIA
            WHERE u.ID_UTENTE = %s
        """, [id_utente])
        utente = cursor.fetchone()
        if not utente:
            return redirect('socioeconomicos_lista')

        # 2️⃣ Intervenções
        cursor.execute("""
            SELECT 
                i.ID_INTERVENCAO,
                ti.NOME_TIPO_INTERVENCAO,
                e.NOME_ENTIDADE,
                p.PROGRAMA,
                i.DATA_INTERVENCAO,
                i.OBSERVACOES_INTERVENCAO
            FROM INTERVENCAO i
            JOIN TIPO_INTERVENCAO ti ON i.ID_TIPO_INTERVENCAO = ti.ID_TIPO_INTERVENCAO
            JOIN ENTIDADE e ON i.ID_ENTIDADE = e.ID_ENTIDADE
            JOIN PROGRAMA p ON i.ID_PROGRAMA = p.ID_PROGRAMA
            JOIN PARTICIPAR pa ON i.ID_INTERVENCAO = pa.ID_INTERVENCAO
            WHERE pa.ID_UTENTE = %s
            ORDER BY i.DATA_INTERVENCAO DESC
        """, [id_utente])
        intervencoes = cursor.fetchall()

        # 3️⃣ Problemáticas
        cursor.execute("""
            SELECT 
                p.NOME_PROBLEMATICA,
                t.DATA_INICIO,
                t.DATA_FIM,
                CASE WHEN t.DATA_FIM IS NULL THEN 'Ativa' ELSE 'Resolvida' END AS ESTADO
            FROM TER t
            JOIN PROBLEMATICAS_IDENTIFICADAS p ON t.ID_PROBLEMATICA = p.ID_PROBLEMATICA
            WHERE t.ID_UTENTE = %s
            ORDER BY t.DATA_INICIO DESC
        """, [id_utente])
        problematicas = cursor.fetchall()

        # 4️⃣ Membros do agregado
        cursor.execute("""
            SELECT NOME_MEMBRO, ANO_NASCIMENTO, GRAU_PARENTESCO
            FROM MEMBROS_AGREGADO_FAMILIAR
            WHERE ID_UTENTE = %s
        """, [id_utente])
        membros_agregado = cursor.fetchall()

        # 5️⃣ Despesas fixas
        cursor.execute("""
            SELECT td.DESCRICAO_TIPO_DESPESA, df.VALOR_DESPESA
            FROM DESPESAS_FIXAS df
            JOIN TIPO_DESPESA td ON df.ID_TIPO_DESPESA = td.ID_TIPO_DESPESA
            WHERE df.ID_UTENTE = %s
        """, [id_utente])
        despesas = cursor.fetchall()

        # 6️⃣ Escalões de rendimento
        cursor.execute("""
            SELECT TIPO_ESCALAO, VALOR_EXATO
            FROM ESCALAO_RENDIMENTOS
            WHERE ID_UTENTE = %s
            ORDER BY ID_ESCALAO DESC
        """, [id_utente])
        escaloes = cursor.fetchall()

    # --- Construção do PDF com reportlab ---
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="utente_{id_utente}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm, leftMargin=1.5*cm, rightMargin=1.5*cm)
    styles = getSampleStyleSheet()

    # Estilos personalizados
    titulo_estilo = ParagraphStyle('TituloEstilo', parent=styles['Title'], fontSize=16, textColor=colors.HexColor('#0d6efd'), alignment=TA_CENTER, spaceAfter=20)
    subtitulo_estilo = ParagraphStyle('SubtituloEstilo', parent=styles['Heading2'], fontSize=12, textColor=colors.black, alignment=TA_LEFT, spaceBefore=10, spaceAfter=6)
    normal_estilo = ParagraphStyle('NormalEstilo', parent=styles['Normal'], fontSize=9, leading=12)
    celula_estilo = ParagraphStyle('CelulaEstilo', parent=styles['Normal'], fontSize=8, leading=10)

    story = []

    # Cabeçalho
    story.append(Paragraph("Ficha do Utente Socioeconómico", titulo_estilo))
    story.append(Paragraph(f"<b>Nome:</b> {utente[1]}", normal_estilo))
    story.append(Paragraph(f"<b>Código:</b> #{utente[0]}", normal_estilo))
    story.append(Spacer(1, 0.5*cm))

    # 1. Informação Pessoal
    story.append(Paragraph("Informação Pessoal", subtitulo_estilo))
    info_data = [
        ["Idade:", f"{utente[2]} anos"],
        ["Nacionalidade:", utente[3] or "-"],
        ["Zona/Freguesia:", utente[4] or "-"],
        ["Tipologia Agregado:", utente[8] or "-"],
    ]
    t_info = Table(info_data, colWidths=[4*cm, 10*cm])
    t_info.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 0.3*cm))

    # 2. Situação Social
    story.append(Paragraph("Situação Social", subtitulo_estilo))
    story.append(Paragraph(f"<b>Situação Habitacional:</b> {utente[5] or '-'}", normal_estilo))
    story.append(Spacer(1, 0.3*cm))

    # 3. Situação Económica
    story.append(Paragraph("Situação Económica", subtitulo_estilo))
    story.append(Paragraph(f"<b>Situação Laboral:</b> {utente[6] or '-'}", normal_estilo))
    story.append(Paragraph(f"<b>Tipo de Rendimento:</b> {utente[7] or '-'}", normal_estilo))
    story.append(Paragraph(f"<b>Risco Social:</b> {'Em risco' if utente[9] else 'Estável'}", normal_estilo))
    story.append(Spacer(1, 0.2*cm))

    if escaloes:
        story.append(Paragraph("<b>Escalões de Rendimento:</b>", normal_estilo))
        for e in escaloes:
            story.append(Paragraph(f"• {e[0]}: {e[1]} €", normal_estilo))
    else:
        story.append(Paragraph("Nenhum escalão registado.", normal_estilo))
    story.append(Spacer(1, 0.2*cm))

    if despesas:
        story.append(Paragraph("<b>Despesas Fixas:</b>", normal_estilo))
        for d in despesas:
            story.append(Paragraph(f"• {d[0]}: {d[1]} €", normal_estilo))
    else:
        story.append(Paragraph("Nenhuma despesa fixa registada.", normal_estilo))
    story.append(Spacer(1, 0.5*cm))

    # 4. Intervenções
    story.append(Paragraph("Intervenções", subtitulo_estilo))
    if intervencoes:
        # Preparar dados com Paragraph para wrap automático
        table_data = [[
            Paragraph("Tipo", celula_estilo),
            Paragraph("Entidade", celula_estilo),
            Paragraph("Programa", celula_estilo),
            Paragraph("Data", celula_estilo),
            Paragraph("Observações", celula_estilo)
        ]]
        for i in intervencoes:
            obs = i[5] if i[5] else "-"
            # Limitar a 200 caracteres e usar Paragraph
            if len(obs) > 200:
                obs = obs[:197] + "..."
            row = [
                Paragraph(i[1] or "-", celula_estilo),
                Paragraph(i[2] or "-", celula_estilo),
                Paragraph(i[3] or "-", celula_estilo),
                Paragraph(i[4].strftime("%d/%m/%Y %H:%M") if i[4] else "-", celula_estilo),
                Paragraph(obs, celula_estilo)
            ]
            table_data.append(row)
        # Larguras ajustáveis: a última coluna (Observações) é mais larga
        col_widths = [2.8*cm, 2.8*cm, 2.8*cm, 2.8*cm, 5*cm]
        t_interv = Table(table_data, colWidths=col_widths, repeatRows=1)
        t_interv.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
        ]))
        story.append(KeepTogether(t_interv))
    else:
        story.append(Paragraph("Sem intervenções registadas.", normal_estilo))
    story.append(Spacer(1, 0.5*cm))

    # 5. Problemáticas
    story.append(Paragraph("Problemáticas", subtitulo_estilo))
    if problematicas:
        table_data = [[
            Paragraph("Problemática", celula_estilo),
            Paragraph("Data Início", celula_estilo),
            Paragraph("Data Fim", celula_estilo),
            Paragraph("Estado", celula_estilo)
        ]]
        for p in problematicas:
            row = [
                Paragraph(p[0] or "-", celula_estilo),
                Paragraph(p[1].strftime("%d/%m/%Y") if p[1] else "-", celula_estilo),
                Paragraph(p[2].strftime("%d/%m/%Y") if p[2] else "-", celula_estilo),
                Paragraph(p[3], celula_estilo)
            ]
            table_data.append(row)
        t_prob = Table(table_data, colWidths=[5*cm, 3*cm, 3*cm, 3*cm], repeatRows=1)
        t_prob.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(KeepTogether(t_prob))
    else:
        story.append(Paragraph("Sem problemáticas associadas.", normal_estilo))
    story.append(Spacer(1, 0.5*cm))

    # 6. Agregado Familiar
    story.append(Paragraph("Agregado Familiar", subtitulo_estilo))
    if membros_agregado:
        table_data = [[
            Paragraph("Nome", celula_estilo),
            Paragraph("Ano Nascimento", celula_estilo),
            Paragraph("Parentesco", celula_estilo)
        ]]
        for m in membros_agregado:
            row = [
                Paragraph(m[0] or "-", celula_estilo),
                Paragraph(str(m[1]) if m[1] else "-", celula_estilo),
                Paragraph(m[2] or "-", celula_estilo)
            ]
            table_data.append(row)
        t_agreg = Table(table_data, colWidths=[6*cm, 4*cm, 4*cm], repeatRows=1)
        t_agreg.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(KeepTogether(t_agreg))
    else:
        story.append(Paragraph("Nenhum membro do agregado registado.", normal_estilo))
    story.append(Spacer(1, 0.5*cm))

    # 7. Observações
    story.append(Paragraph("Observações", subtitulo_estilo))
    story.append(Paragraph(utente[10] or "Sem observações.", normal_estilo))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Critério de Risco", subtitulo_estilo))
    story.append(Paragraph(utente[11] or "-", normal_estilo))

    # Rodapé
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(f"Documento gerado automaticamente em {timezone.now().strftime('%d/%m/%Y %H:%M')}", normal_estilo))

    # Gerar PDF
    doc.build(story)
    return response

@login_required
def idosos_pdf(request, id_utente):
    with connection.cursor() as cursor:
        # 1. Dados básicos do idoso (igual à view de detalhe)
        cursor.execute("""
            SELECT 
                u.ID_UTENTE,
                u.NOME_UTENTE,
                EXTRACT(YEAR FROM AGE(CURRENT_DATE, u.DATA_NASCIMENTO)) AS IDADE,
                g.DESCRICAO_GENERO AS SEXO,
                z.DESCRICAO_ZONA_UTENTE AS ZONA,
                ec.DESCRICAO_ESTADO_CIVIL,
                ga.NOME_GRAU_AUTONOMIA AS GRAU_AUTONOMIA,
                m.NOME_MOBILIDADE AS MOBILIDADE,
                ni.NIVEL_ISOLAMENTO,
                rf.DESCRICAO_RELACAO_FAMILIA,
                fcs.DESCRICAO_FREQUENCIA_CONTACTO_SOCIAL AS FREQUENCIA_CONTACTO_SOCIAL,
                th.DESCRICAO_TIPO AS TIPO_HABITACAO,
                ui.VIVE_SOZINHO,
                ui.CONTACTO_EMERGENCIA,
                ui.FAMILIAR_REFERENCIA,
                ui.MEDICACAO_DIARIA,
                ui.DIFICULDADE_ACESSO_SAUDE,
                ui.ACOMPANHAMENTO_REG,
                ui.PARTICIPA_ATIVIDADES_FR,
                ui.TRISTESA_DEPRESSAO,
                ui.LUTO_RECENTE,
                ui.AQUECIMENTO_ADEQ_INV,
                ui.SEGURANCA,
                ui.NECESSIDADE_ADPTACOES
            FROM UTENTES u
            JOIN UTENTES_IDOSOS ui ON u.ID_UTENTE = ui.ID_UTENTE
            JOIN GENERO g ON u.ID_GENERO = g.ID_GENERO
            JOIN ZONA_UTENTE z ON u.ID_ZONA_UTENTE = z.ID_ZONA_UTENTE
            JOIN ESTADO_CIVIL ec ON ui.ID_ESTADO_CIVIL = ec.ID_ESTADO_CIVIL
            JOIN GRAU_AUTONOMIA ga ON ui.ID_GRAU_AUTONOMIA = ga.ID_GRAU_AUTONOMIA
            JOIN MOBILIDADE m ON ui.ID_MOBILIDADE = m.ID_MOBILIDADE
            JOIN NIVEL_ISOLAMENTO ni ON ui.ID_NIVEL_ISOLAMENTO = ni.ID_NIVEL_ISOLAMENTO
            JOIN RELACAO_FAMILIA rf ON ui.ID_RELACAO_FAMILIA = rf.ID_RELACAO_FAMILIA
            JOIN FREQUENCIA_CONTACTO_SOCIAL fcs ON ui.ID_FREQUENCIA_CONTACTO_SOCIAL = fcs.ID_FREQUENCIA_CONTACTO_SOCIAL
            JOIN TIPO_HABITACAO th ON ui.ID_TIPO_HABITACAO = th.ID_TIPO_HABITACAO
            WHERE u.ID_UTENTE = %s
        """, [id_utente])
        utente = cursor.fetchone()
        if not utente:
            messages.error(request, 'Idoso não encontrado')
            return redirect('idosos_lista')

        # 2. Atividades da vida diária
        cursor.execute("""
            SELECT DESCRICAO_ATIVIDADE_DIARIA
            FROM ATIVIDADES_DIARIA
            WHERE ID_UTENTE = %s
        """, [id_utente])
        atividades = cursor.fetchall()

        # 3. Doenças crónicas
        cursor.execute("""
            SELECT dc.DESCRICAO_DOENCA_CRONICA
            FROM DOENCAS_IDOSOS di
            JOIN DOENCAS_CRONICAS dc ON di.ID_DOENCA_CRONICA = dc.ID_DOENCA_CRONICA
            WHERE di.ID_UTENTE = %s
        """, [id_utente])
        doencas = cursor.fetchall()

        # 4. Barreiras arquitetónicas
        cursor.execute("""
            SELECT ba.DESCRICAO_BARREIRA_ARQUITETONICA
            FROM BARREIRAS_IDOSOS bi
            JOIN BARREIRAS_ARQUITETONICAS ba ON bi.ID_BARREIRA_ARQUITETONICA = ba.ID_BARREIRA_ARQUITETONICA
            WHERE bi.ID_UTENTE = %s
        """, [id_utente])
        barreiras = cursor.fetchall()

        # 5. Contactos
        cursor.execute("""
            SELECT
                c.ID_CONTACTO, 
                c.DATA_CONTACTO,
                tc.NOME_TIPO_CONTACTO,
                fc.DESCRICAO_FREQUENCIA_CONTACTO,
                c.OBSERVACOES_CONTACTO
            FROM CONTACTO c
            JOIN TIPO_CONTACTO tc ON c.ID_TIPO_CONTACTO = tc.ID_TIPO_CONTACTO
            JOIN FREQUENCIA_CONTACTO fc ON c.ID_FREQUENCIA_CONTACTO = fc.ID_FREQUENCIA_CONTACTO
            WHERE c.ID_UTENTE = %s
            ORDER BY c.DATA_CONTACTO DESC
        """, [id_utente])
        contactos = cursor.fetchall()

        # 6. Quedas
        cursor.execute("""
            SELECT DATA_QUEDA, OBSERVACOES_QUEDA
            FROM QUEDAS_IDOSO
            WHERE ID_UTENTE = %s
            ORDER BY DATA_QUEDA DESC
        """, [id_utente])
        quedas = cursor.fetchall()

        # 7. Sinais de fragilidade
        cursor.execute("""
            SELECT sf.DESCRICAO_FRAGILIDADE
            FROM FRAGILIDADE_IDOSO fi
            JOIN SINAIS_FRAGILIDADE sf ON fi.ID_SINAL_FRAGILIDADE = sf.ID_SINAL_FRAGILIDADE
            WHERE fi.ID_UTENTE = %s
        """, [id_utente])
        fragilidades = cursor.fetchall()

    # --- Construção do PDF com reportlab (corrigido) ---
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="idoso_{id_utente}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm, leftMargin=1.5*cm, rightMargin=1.5*cm)
    styles = getSampleStyleSheet()

    # Estilos personalizados
    titulo_estilo = ParagraphStyle('TituloEstilo', parent=styles['Title'], fontSize=16, textColor=colors.HexColor('#0d6efd'), alignment=TA_CENTER, spaceAfter=20)
    subtitulo_estilo = ParagraphStyle('SubtituloEstilo', parent=styles['Heading2'], fontSize=12, textColor=colors.black, alignment=TA_LEFT, spaceBefore=10, spaceAfter=6)
    normal_estilo = ParagraphStyle('NormalEstilo', parent=styles['Normal'], fontSize=9, leading=12)
    celula_estilo = ParagraphStyle('CelulaEstilo', parent=styles['Normal'], fontSize=8, leading=10)

    # Corrigir o hífen no título "Bem‑estar" usando o caractere Unicode correcto (U+2010)
    bem_estar_texto = "Bem Estar e Social"  # hífen Unicode (não é o traço normal)

    story = []

    # Título e identificação
    story.append(Paragraph("Ficha do Utente Idoso", titulo_estilo))
    story.append(Paragraph(f"<b>Nome:</b> {utente[1]}", normal_estilo))
    story.append(Paragraph(f"<b>Código:</b> #{utente[0]}", normal_estilo))
    story.append(Spacer(1, 0.5*cm))

    # 1. Informação Pessoal
    story.append(Paragraph("Informação Pessoal", subtitulo_estilo))
    info_data = [
        ["Idade:", f"{utente[2]} anos"],
        ["Sexo:", utente[3] or "-"],
        ["Zona/Freguesia:", utente[4] or "-"],
        ["Estado Civil:", utente[5] or "-"],
        ["Contacto Emergência:", utente[13] or "-"],
        ["Familiar/Cuidador:", utente[14] or "-"],
        ["Vive Sozinho:", "Sim" if utente[12] else "Não"],
    ]
    t_info = Table(info_data, colWidths=[4*cm, 10*cm])
    t_info.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ('FONTSIZE', (0,0), (-1,-1), 9),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 0.3*cm))

    # 2. Saúde e Autonomia
    story.append(Paragraph("Saúde e Autonomia", subtitulo_estilo))
    saude_data = [
        ("Grau de Autonomia:", utente[6] or "-"),
        ("Mobilidade:", utente[7] or "-"),
        ("Medicação Diária:", "Sim" if utente[15] else "Não"),
        ("Dificuldade Acesso Saúde:", "Sim" if utente[16] else "Não"),
        ("Acompanhamento Centro Saúde:", "Sim" if utente[17] else "Não"),
    ]
    for label, value in saude_data:
        story.append(Paragraph(f"<b>{label}</b> {value}", normal_estilo))
    story.append(Spacer(1, 0.3*cm))

    # 3. Bem‑estar e Social (com hífen corrigido)
    story.append(Paragraph(bem_estar_texto, subtitulo_estilo))
    social_data = [
        ("Nível de Isolamento:", utente[8] or "-"),
        ("Relação com a Família:", utente[9] or "-"),
        ("Frequência Contacto Social:", utente[10] or "-"),
        ("Participa Atividades Freguesia:", "Sim" if utente[18] else "Não"),
        ("Sinais Tristeza/Depressão:", "Sim" if utente[19] else "Não"),
        ("Luto Recente:", "Sim" if utente[20] else "Não"),
    ]
    for label, value in social_data:
        story.append(Paragraph(f"<b>{label}</b> {value}", normal_estilo))
    story.append(Spacer(1, 0.3*cm))

    # 4. Habitação e Segurança
    story.append(Paragraph("Habitação e Segurança", subtitulo_estilo))
    hab_data = [
        ("Tipo de Habitação:", utente[11] or "-"),
        ("Aquecimento Adequado Inverno:", "Sim" if utente[21] else "Não"),
        ("Segurança (risco quedas):", utente[22] or "-"),
        ("Necessidade de Adaptações:", utente[23] or "-"),
    ]
    for label, value in hab_data:
        story.append(Paragraph(f"<b>{label}</b> {value}", normal_estilo))
    story.append(Spacer(1, 0.5*cm))

    # 5. Atividades da Vida Diária (AVD)
    story.append(Paragraph("Atividades da Vida Diária (AVD)", subtitulo_estilo))
    if atividades:
        for a in atividades:
            story.append(Paragraph(f"• {a[0]}", normal_estilo))
    else:
        story.append(Paragraph("Nenhuma atividade registada.", normal_estilo))
    story.append(Spacer(1, 0.5*cm))

    # 6. Doenças Crónicas
    story.append(Paragraph("Doenças Crónicas", subtitulo_estilo))
    if doencas:
        for d in doencas:
            story.append(Paragraph(f"• {d[0]}", normal_estilo))
    else:
        story.append(Paragraph("Nenhuma doença crónica registada.", normal_estilo))
    story.append(Spacer(1, 0.5*cm))

    # 7. Barreiras Arquitetónicas
    story.append(Paragraph("Barreiras Arquitetónicas", subtitulo_estilo))
    if barreiras:
        for b in barreiras:
            story.append(Paragraph(f"• {b[0]}", normal_estilo))
    else:
        story.append(Paragraph("Nenhuma barreira arquitetónica registada.", normal_estilo))
    story.append(Spacer(1, 0.5*cm))

    # 8. Sinais de Fragilidade
    story.append(Paragraph("Sinais de Fragilidade", subtitulo_estilo))
    if fragilidades:
        for f in fragilidades:
            story.append(Paragraph(f"• {f[0]}", normal_estilo))
    else:
        story.append(Paragraph("Nenhum sinal de fragilidade registado.", normal_estilo))
    story.append(Spacer(1, 0.5*cm))

    # 9. Contactos realizados
    story.append(Paragraph("Histórico de Contactos", subtitulo_estilo))
    if contactos:
        table_data = [[
            Paragraph("Data", celula_estilo),
            Paragraph("Tipo", celula_estilo),
            Paragraph("Frequência", celula_estilo),
            Paragraph("Observações", celula_estilo)
        ]]
        for c in contactos:
            obs = c[4] if c[4] else "-"
            if len(obs) > 100:
                obs = obs[:97] + "..."
            row = [
                Paragraph(c[1].strftime("%d/%m/%Y %H:%M") if c[1] else "-", celula_estilo),
                Paragraph(c[2] or "-", celula_estilo),
                Paragraph(c[3] or "-", celula_estilo),
                Paragraph(obs, celula_estilo)
            ]
            table_data.append(row)
        col_widths = [2.8*cm, 2.8*cm, 2.8*cm, 7*cm]
        t_contactos = Table(table_data, colWidths=col_widths, repeatRows=1)
        t_contactos.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
        ]))
        story.append(KeepTogether(t_contactos))
    else:
        story.append(Paragraph("Nenhum contacto registado.", normal_estilo))
    story.append(Spacer(1, 0.5*cm))

    # 10. Quedas
    story.append(Paragraph("Registo de Quedas", subtitulo_estilo))
    if quedas:
        table_data = [[
            Paragraph("Data", celula_estilo),
            Paragraph("Observações", celula_estilo)
        ]]
        for q in quedas:
            row = [
                Paragraph(q[0].strftime("%d/%m/%Y") if q[0] else "-", celula_estilo),
                Paragraph(q[1] or "-", celula_estilo)
            ]
            table_data.append(row)
        t_quedas = Table(table_data, colWidths=[3*cm, 12*cm], repeatRows=1)
        t_quedas.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(KeepTogether(t_quedas))
    else:
        story.append(Paragraph("Nenhuma queda registada.", normal_estilo))

    # Rodapé
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(f"Documento gerado automaticamente em {timezone.now().strftime('%d/%m/%Y %H:%M')}", normal_estilo))

    doc.build(story)
    return response


