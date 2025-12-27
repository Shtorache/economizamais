from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Produto(models.Model):
    nome = models.CharField(max_length=150)
    marca = models.CharField(max_length=100, blank=True)
    categoria = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nome} ({self.marca})"


class Mercado(models.Model):
    nome = models.CharField(max_length=150)
    endereco = models.CharField(max_length=255)
    cidade = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome


class ItemMercado(models.Model):
    mercado = models.ForeignKey(Mercado, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    ativo = models.BooleanField(default=True)

    class Meta:
        unique_together = ("mercado", "produto")

    def __str__(self):
        return f"{self.produto.nome} - {self.mercado.nome}"


class PrecoItem(models.Model):
    item = models.ForeignKey(ItemMercado, on_delete=models.CASCADE)
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    data = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.item.produto.nome} - R$ {self.preco}"


class Compra(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mercado = models.ForeignKey("Mercado", on_delete=models.CASCADE)
    criado_em = models.DateTimeField(default=timezone.now)

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    # Nota fiscal
    comprovada = models.BooleanField(default=False)
    nota_fiscal = models.FileField(
        upload_to="notas_fiscais/",
        null=True,
        blank=True
    )
    ocr_processado = models.BooleanField(default=False)

    def __str__(self):
        return f"Compra #{self.id} - {self.user.username}"


class CompraItem(models.Model):
    compra = models.ForeignKey(
        Compra,
        related_name="itens",
        on_delete=models.CASCADE
    )
    item = models.ForeignKey("ItemMercado", on_delete=models.CASCADE)
    preco_pago = models.DecimalField(max_digits=8, decimal_places=2)
    quantidade = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.preco_pago * self.quantidade
    
class AvaliacaoMercado(models.Model):
    compra = models.OneToOneField(
        Compra,
        on_delete=models.CASCADE,
        related_name="avaliacao"
    )
    mercado = models.ForeignKey(Mercado, on_delete=models.CASCADE)

    estrelas = models.PositiveSmallIntegerField()  # 1 a 5
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.mercado.nome} - {self.estrelas}⭐"
