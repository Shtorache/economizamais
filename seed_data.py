import os
import django
from datetime import date

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from parceiros.models import Mercado, Produto, ItemMercado, PrecoItem

print("Iniciando seed do banco...")

# =========================
# MERCADOS
# =========================
mercados = [
    {
        "nome": "Rio Sul Supermercado",
        "endereco": "Av. Itaipuaçu, Maricá",
        "cidade": "Maricá",
        "latitude": -22.955305249998542,
        "longitude": -42.97657732836294,
        "ativo": True
    },
    {
        "nome": "Mercado Atlântico",
        "endereco": "Centro, Búzios",
        "cidade": "Búzios",
        "latitude": -22.77556521017071,
        "longitude": -41.92935013675178,
        "ativo": True
    },
]

mercados_db = []
for m in mercados:
    mercado, created = Mercado.objects.get_or_create(
        nome=m["nome"],
        defaults=m
    )
    mercados_db.append(mercado)

# =========================
# PRODUTOS
# =========================
produtos = [
    {"nome": "Arroz", "marca": "Tio João", "categoria": "Grãos"},
    {"nome": "Feijão", "marca": "Kicaldo", "categoria": "Grãos"},
    {"nome": "Leite", "marca": "Italac", "categoria": "Laticínios"},
    {"nome": "Achocolatado", "marca": "Nescau", "categoria": "Bebidas"},
    {"nome": "Óleo de Soja", "marca": "Soya", "categoria": "Óleos"},
]

produtos_db = []
for p in produtos:
    produto, created = Produto.objects.get_or_create(
        nome=p["nome"],
        marca=p["marca"],
        defaults=p
    )
    produtos_db.append(produto)

# =========================
# ITEM POR MERCADO + PREÇO
# =========================
for mercado in mercados_db:
    for produto in produtos_db:
        item, _ = ItemMercado.objects.get_or_create(
            mercado=mercado,
            produto=produto,
            defaults={"ativo": True}
        )

        PrecoItem.objects.get_or_create(
            item=item,
            data=date.today(),
            defaults={"preco": 9.90 + produtos_db.index(produto) * 4}
        )

print("Seed finalizado com sucesso!")
