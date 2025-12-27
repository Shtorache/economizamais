from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Mercado, ItemMercado, PrecoItem, Compra, CompraItem, AvaliacaoMercado
from math import radians, cos, sin, asin, sqrt
from datetime import date, timedelta
from collections import defaultdict


def parceiros_login(request):
    return render(request, 'parceiros/login.html')


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c


def mercados_proximos(request):
    lat = float(request.GET.get("lat"))
    lng = float(request.GET.get("lng"))

    mercados = []
    for m in Mercado.objects.filter(ativo=True):
        distancia = haversine(lat, lng, m.latitude, m.longitude)
        if distancia <= 1000:  # 1000 km (teste)
            mercados.append({
                "id": m.id,
                "nome": m.nome,
                "endereco": m.endereco,
                "latitude": m.latitude,
                "longitude": m.longitude,
                "distancia": round(distancia, 2)
            })

    return JsonResponse({"mercados": mercados})


@login_required
def mercado_detalhe(request, id):
    mercado = get_object_or_404(Mercado, id=id)

    # ======================
    # CARRINHO
    # ======================
    carrinho = request.session.get("carrinho", {})
    total = 0
    for v in carrinho.values():
        total += v["preco"] * v["quantidade"]
    total = round(total, 2)

    # ======================
    # FILTROS
    # ======================
    q = request.GET.get("q", "")
    filtro = request.GET.get("filtro", "hoje")

    itens = ItemMercado.objects.filter(mercado=mercado, ativo=True)

    if q:
        itens = itens.filter(produto__nome__icontains=q)

    dados = []

    for item in itens:
        hoje = PrecoItem.objects.filter(item=item, data=date.today()).first()
        semana = PrecoItem.objects.filter(item=item, data=date.today() - timedelta(days=7)).first()
        mes = PrecoItem.objects.filter(item=item, data=date.today() - timedelta(days=30)).first()

        ultimo_pago = None
        ultimo_item = (
            CompraItem.objects
            .filter(
                compra__user=request.user,
                item=item
            )
            .order_by("-compra__criado_em")
            .first()
        )

        if ultimo_item:
            ultimo_pago = ultimo_item.preco_pago

        dados.append({
            "item": item,
            "hoje": hoje.preco if hoje else None,
            "semana": semana.preco if semana else None,
            "mes": mes.preco if mes else None,
            "ultimo_pago": ultimo_pago
        })

    return render(request, "parceiros/mercado.html", {
        "mercado": mercado,
        "dados": dados,
        "q": q,
        "filtro": filtro,
        "total_carrinho": total
    })


@login_required
def adicionar_ao_carrinho(request, item_id):
    carrinho = request.session.get("carrinho", {})

    item = get_object_or_404(ItemMercado, id=item_id)
    preco_hoje = PrecoItem.objects.filter(item=item, data=date.today()).first()

    if not preco_hoje:
        return redirect(request.META.get("HTTP_REFERER", "/"))

    if str(item_id) not in carrinho:
        carrinho[str(item_id)] = {
            "nome": item.produto.nome,
            "preco": float(preco_hoje.preco),
            "quantidade": 1
        }
    else:
        carrinho[str(item_id)]["quantidade"] += 1

    request.session["carrinho"] = carrinho
    request.session.modified = True

    return redirect(request.META.get("HTTP_REFERER", "/"))


@login_required
def finalizar_compra(request):
    carrinho = request.session.get("carrinho", {})

    if not carrinho:
        return redirect("/dashboard/")

    # Descobre mercado (todos os itens são do mesmo mercado)
    primeiro_item = ItemMercado.objects.get(id=list(carrinho.keys())[0])
    mercado = primeiro_item.mercado

    compra = Compra.objects.create(
        user=request.user,
        mercado=mercado
    )

    total = 0

    for item_id, dados in carrinho.items():
        item = ItemMercado.objects.get(id=item_id)

        CompraItem.objects.create(
            compra=compra,
            item=item,
            preco_pago=dados["preco"],
            quantidade=dados["quantidade"]
        )

        total += dados["preco"] * dados["quantidade"]

    compra.total = total
    compra.save()

    request.session["carrinho"] = {}
    request.session.modified = True

    return redirect("minhas_compras")


@login_required
def minhas_compras(request):
    compras = (
        Compra.objects
        .filter(user=request.user)
        .prefetch_related("itens__item__produto", "itens__item__mercado")
        .order_by("-criado_em")
    )

    return render(request, "minhas_compras.html", {
        "compras": compras
    })


@login_required
def enviar_nota_fiscal(request, compra_id):
    compra = get_object_or_404(
        Compra,
        id=compra_id,
        user=request.user
    )

    if request.method == "POST" and request.FILES.get("nota"):
        compra.nota_fiscal = request.FILES["nota"]
        compra.comprovada = True
        compra.save()

        return redirect("minhas_compras")

    return render(request, "enviar_nota.html", {
        "compra": compra
    })

@login_required
def avaliar_mercado(request, compra_id):
    compra = get_object_or_404(
        Compra,
        id=compra_id,
        user=request.user
    )

    if request.method == "POST":
        estrelas = int(request.POST.get("estrelas"))

        if 1 <= estrelas <= 5:
            AvaliacaoMercado.objects.update_or_create(
                compra=compra,
                defaults={
                    "mercado": compra.mercado,
                    "estrelas": estrelas
                }
            )

        return redirect("minhas_compras")

    return redirect("minhas_compras")
