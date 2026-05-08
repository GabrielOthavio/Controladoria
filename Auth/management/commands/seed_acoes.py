import random
import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from Auth.models import Acao, TipoAcao

User = get_user_model()

TIPOS = [
    ("Auditoria Interna",       "Verificação periódica dos processos internos.",
     "Analisar conformidade dos processos com as normas vigentes.",
     "Processos auditados e não conformidades registradas."),
    ("Fiscalização de Contratos", "Acompanhamento de execução contratual.",
     "Avaliar cumprimento das cláusulas contratuais.",
     "Contrato em conformidade / irregularidades identificadas."),
    ("Análise de Prestação de Contas", "Revisão de documentos de prestação de contas.",
     "Verificar regularidade das despesas apresentadas.",
     "Prestação de contas aprovada / reprovada com ressalvas."),
    ("Assessoria Técnica",      "Apoio técnico às unidades.",
     "Orientar a unidade sobre procedimentos normativos.",
     "Orientações emitidas e registradas no sistema."),
    ("Elaboração de Relatório", "Produção de relatório gerencial ou técnico.",
     "Consolidar dados e produzir relatório executivo.",
     "Relatório elaborado e encaminhado à chefia."),
    ("Capacitação",             "Ação de treinamento e desenvolvimento.",
     "Avaliar aderência do conteúdo às necessidades da equipe.",
     "Capacitação realizada com X participantes."),
    ("Diligência",              "Solicitação de informações complementares.",
     "Verificar resposta da unidade à diligência emitida.",
     "Resposta recebida e analisada."),
    ("Inspeção",                "Inspeção presencial nas instalações.",
     "Verificar condições físicas e documentais in loco.",
     "Inspeção concluída com laudo emitido."),
]

AVALIACOES = [
    "Os processos analisados apresentam conformidade com as normas vigentes.",
    "Foram identificadas inconsistências nos documentos apresentados.",
    "A unidade demonstrou boa organização e controle interno eficiente.",
    "Há pendências que precisam ser sanadas no prazo estabelecido.",
    "Os registros estão atualizados e dentro dos parâmetros exigidos.",
    "Constatou-se ausência de documentação comprobatória em alguns itens.",
    "Os procedimentos adotados estão alinhados com as melhores práticas.",
    "A gestão demonstrou dificuldades no cumprimento dos prazos legais.",
    "Foram verificados controles preventivos eficazes contra fraudes.",
    "A execução financeira está dentro dos limites aprovados pelo orçamento.",
]

CONCLUSOES = [
    "Recomenda-se a regularização das pendências em até 30 dias.",
    "Processo encerrado sem ressalvas. Arquivar após ciência da chefia.",
    "Encaminhar para a unidade responsável adotar as medidas corretivas.",
    "Situação normalizada após adoção das providências recomendadas.",
    "Manter monitoramento contínuo nas próximas auditorias.",
    "Emitir nota técnica com as irregularidades para apreciação superior.",
    "Solicitar plano de ação à unidade com cronograma de implementação.",
    "Homologar os procedimentos após verificação das correções efetuadas.",
    "Registrar no sistema de controle interno para acompanhamento futuro.",
    "Encerrar o processo com recomendação de melhoria nos controles.",
]

UNIDADES   = [c[0] for c in Acao.UNIDADE_CHOICES]
STATUSES   = [c[0] for c in Acao.STATUS_CHOICES]


class Command(BaseCommand):
    help = "Popula o banco com 100 registros de Ação para demonstração."

    def handle(self, *args, **options):
        usuario = User.objects.first()
        if not usuario:
            self.stderr.write("Nenhum usuário encontrado. Crie um superusuário primeiro.")
            return

        # garante tipos existem
        tipos = []
        for nome, motivo, aval, concl in TIPOS:
            t, _ = TipoAcao.objects.get_or_create(
                nome_acao=nome,
                defaults={
                    "motivo_acao": motivo,
                    "mensagem_padrao_avaliacao": aval,
                    "mensagem_padrao_conclusao": concl,
                },
            )
            tipos.append(t)

        hoje = datetime.date.today()
        criados = 0

        for i in range(100):
            delta = random.randint(-540, 60)   # ~18 meses atrás até 2 meses à frente
            data  = hoje + datetime.timedelta(days=delta)

            Acao.objects.create(
                data_execucao=data,
                tipo_acao=random.choice(tipos),
                usuario=usuario,
                avaliacao=random.choice(AVALIACOES),
                conclusao=random.choice(CONCLUSOES),
                status=random.choice(STATUSES),
                unidade=random.choice(UNIDADES),
                is_paint=random.random() < 0.25,
            )
            criados += 1

        self.stdout.write(self.style.SUCCESS(f"{criados} ações criadas com sucesso."))
