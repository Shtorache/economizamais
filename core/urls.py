
from django.contrib import admin
from django.urls import path, include
from pages.views import home
from dashboard.views import dashboard_view, profile_view, comecar_comprar
from parceiros.views import parceiros_login, mercados_proximos, mercado_detalhe, adicionar_ao_carrinho, finalizar_compra, minhas_compras, enviar_nota_fiscal, avaliar_mercado

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('parceiros/', parceiros_login, name='parceiros'),
    path('accounts/', include('allauth.urls')),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('profile/', profile_view, name='profile'),
    path("api/mercados/proximos/", mercados_proximos),
    path("comecar-comprar/", comecar_comprar, name="comecar_comprar"),
    path("mercado/<int:id>/", mercado_detalhe, name="mercado_detalhe"),
    path("carrinho/add/<int:item_id>/", adicionar_ao_carrinho, name="add_carrinho"),
    path("carrinho/finalizar/", finalizar_compra, name="finalizar_compra"),
    path("minhas-compras/", minhas_compras, name="minhas_compras"),
    path("minhas-compras/enviar-nota/<int:compra_id>/",enviar_nota_fiscal,name="enviar_nota_fiscal"),
    path( "minhas-compras/avaliar/<int:compra_id>/", avaliar_mercado, name="avaliar_mercado" ),
]
