from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from parceiros.models import Mercado
from math import radians, cos, sin, asin, sqrt

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

@login_required
def dashboard_view(request):
    mercados = []

    lat = request.GET.get("lat")
    lng = request.GET.get("lng")

    if lat and lng:
        lat = float(lat)
        lng = float(lng)

        for m in Mercado.objects.filter(ativo=True):
            distancia = haversine(lat, lng, m.latitude, m.longitude)
            if distancia <= 10000:
                mercados.append({
                    "id": m.id,
                    "nome": m.nome,
                    "endereco": m.endereco,
                    "distancia": round(distancia, 2)
                })

    return render(request, "dashboard/dashboard.html", {
        "mercados": mercados
    })


@login_required
def profile_view(request):
    user = request.user
    profile = getattr(user, 'profile', None)
    return render(request, 'dashboard/profile.html', {'user': user, 'profile': profile})


@login_required
def comecar_comprar(request):
    return render(request, "dashboard/comecar_comprar.html")
