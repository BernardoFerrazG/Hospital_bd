from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db import connection
from datetime import date, timedelta
from ..models import Consulta, LeitoCirurgico, LeitoUTI
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as login_django
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required(login_url='login_conselho')
def home_conselho(request):
    """
    Página do Conselho que já contém os relatórios (últimos 30 dias).
    Template: templates/home/home_conselho.html
    """
    hoje = date.today()
    inicio_periodo = hoje - timedelta(days=30)

    # 1) estatísticas de leitos
    def leitos_stats(model):
        total = model.objects.count()
        ocupados = model.objects.filter(status__iexact='ocupado').count()
        perc = (ocupados / total * 100) if total else 0
        return {"total": total, "ocupados": ocupados, "percentual": round(perc, 2)}

    stats_leito_cir = leitos_stats(LeitoCirurgico)
    stats_leito_uti = leitos_stats(LeitoUTI)

    # 2) consultórios usados no período (distinct andar/numero)
    consultorios_usados = (
        Consulta.objects.filter(data__gte=inicio_periodo, data__lte=hoje)
        .values('andar', 'numero').distinct().count()
    )

    # total de consultórios (raw SQL porque você não tem modelo Consultorio)
    with connection.cursor() as cur:
        try:
            cur.execute("SELECT COUNT(*) FROM consultorio;")
            row = cur.fetchone()
            total_consultorios = row[0] if row else 0
        except Exception:
            # se a tabela não existir ou erro, define 0 para evitar crash
            total_consultorios = 0

    consultorios_util_pct = round(
        (consultorios_usados / total_consultorios * 100) if total_consultorios else 0,
        2
    )

    # 3) total de consultas por médico (últimos 30 dias)
    consultas_ult30 = (
        Consulta.objects.filter(data__gte=inicio_periodo, data__lte=hoje)
        .values('fmedico__crm')
        .annotate(total=Count('pk'))
        .order_by('-total')
    )

    # 4) consultas por dia (últimos 30 dias)
    consultas_por_dia = (
        Consulta.objects.filter(data__gte=inicio_periodo, data__lte=hoje)
        .values('data')
        .annotate(total=Count('pk'))
        .order_by('data')
    )

    # 5) top consultórios (por quantidade) — usando SQL para contar
    top_consultorios = []
    with connection.cursor() as cur:
        try:
            cur.execute("""
                SELECT c.andar, c.numero, COUNT(*) AS total
                FROM consulta c
                GROUP BY c.andar, c.numero
                ORDER BY total DESC
                LIMIT 20;
            """)
            rows = cur.fetchall()
            for andar, numero, total in rows:
                cur.execute(
                    "SELECT departamento FROM consultorio WHERE andar = %s AND numero = %s LIMIT 1",
                    (andar, numero)
                )
                r = cur.fetchone()
                departamento = r[0] if r and r[0] else None
                top_consultorios.append({
                    "andar": andar, "numero": numero, "consultas": total, "departamento": departamento
                })
        except Exception:
            # se a tabela consultorio não existir, ignore e mantenha lista vazia
            top_consultorios = []

    context = {
        "inicio_periodo": inicio_periodo,
        "hoje": hoje,
        "stats_leito_cir": stats_leito_cir,
        "stats_leito_uti": stats_leito_uti,
        "total_consultorios": total_consultorios,
        "consultorios_usados": consultorios_usados,
        "consultorios_util_pct": consultorios_util_pct,
        "consultas_ult30": consultas_ult30,
        "consultas_por_dia": list(consultas_por_dia),
        "top_consultorios": top_consultorios,
    }

    return render(request, "home/home_conselho.html", context)


def login_conselho(request):
    """
    Login simples do Conselho: CPF + senha.
    Template: templates/login/login_conselho.html
    """
    if request.method == "POST":
        cpf = request.POST.get("cpf", "").strip()
        senha = request.POST.get("senha", "")

        if not (cpf and senha):
            messages.error(request, "Preencha CPF e senha.")
            return render(request, "login/login_conselho.html")

        user = authenticate(request, username=cpf, password=senha)
        if not user:
            messages.error(request, "Credenciais inválidas.")
            return render(request, "login/login_conselho.html")

        login_django(request, user)
        return redirect("home_conselho")

    # GET
    return render(request, "login/login_conselho.html")



