from django.db import models
from django.conf import settings
import uuid
from pos_project.choices import EstadoEntidades,EstadoOrden

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    # otros campos...

class Vendedor(models.Model):
    nombre = models.CharField(max_length=100)
    # otros campos...

class GrupoArticulo(models.Model):
    grupo_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo_grupo = models.CharField(max_length=5, null=False)
    nombre_grupo = models.CharField(max_length=150, null=False)
    estado = models.IntegerField(choices=EstadoEntidades, default=EstadoEntidades.ACTIVO)

    class Meta:
        db_table = "grupos_articulos"
        ordering = ["codigo_grupo"]

    def __str__(self):
        return self.nombre_grupo


class LineaArticulo(models.Model):
    linea_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo_linea = models.CharField(max_length=10, null=False)
    grupo = models.ForeignKey(GrupoArticulo, on_delete=models.RESTRICT, null=False, related_name='grupo_linea')
    nombre_linea = models.CharField(max_length=150, null=False)
    estado = models.IntegerField(choices=EstadoEntidades, default=EstadoEntidades.ACTIVO)

    class Meta:
        db_table = "lineas_articulos"
        ordering = ["codigo_linea"]

    def __str__(self):
        return self.nombre_linea


class Articulo(models.Model):
    articulo_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo_articulo = models.CharField(max_length=50, unique=True)
    codigo_barras = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.CharField(max_length=255)
    presentacion = models.CharField(max_length=100, blank=True, null=True)
    stock = models.IntegerField(default=0)
    grupo = models.ForeignKey(GrupoArticulo, on_delete=models.CASCADE)
    linea = models.ForeignKey(LineaArticulo, on_delete=models.CASCADE)

    class Meta:
        db_table = "articulos"
        ordering = ["descripcion"]

    def __str__(self):
        return self.descripcion



class ListaPrecio(models.Model):
    lista_precio_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE)
    precio_1 = models.DecimalField(max_digits=10, decimal_places=2)
    precio_2 = models.DecimalField(max_digits=10, decimal_places=2)
    precio_3 = models.DecimalField(max_digits=10, decimal_places=2)
    precio_4 = models.DecimalField(max_digits=10, decimal_places=2)
    precio_costo = models.DecimalField(max_digits=10, decimal_places=2)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "lista_precios"

    def __str__(self):
        return f"{self.articulo.descripcion}"


class OrdenCompraCliente(models.Model):
    pedido_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    #nro_pedido = models.BigAutoField(unique=True, null=False, auto_created=True)
    nro_pedido = models.BigIntegerField(unique=True)
    fecha_pedido = models.DateField(auto_now_add=True, null=False)
    cliente = models.ForeignKey('Cliente', on_delete=models.RESTRICT, null=False)
    vendedor = models.ForeignKey('Vendedor', on_delete=models.RESTRICT, null=False)
    importe = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.IntegerField(choices=EstadoOrden, default=EstadoOrden.PENDIENTE)
    notas = models.TextField(blank=True, null=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, null=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=False)
    def actualizar_total(self):
        """Actualiza el total de la orden basado en los items"""
        total = sum(item.total_item for item in self.items_orden_compra.all())
        self.importe = total
        self.save()

    def __str__(self):
        return f"Orden #{self.nro_pedido} - {self.cliente}"

    class Meta:
        db_table = "ordenes_compra_cliente"
        ordering = ["-fecha_creacion"]

class ItemOrdenCompraCliente(models.Model): 
    item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pedido = models.ForeignKey(OrdenCompraCliente, on_delete=models.CASCADE, null=False, related_name='items_orden_compra')
    nro_item = models.PositiveIntegerField(default=1, null=False)
    articulo = models.ForeignKey('Articulo', on_delete=models.RESTRICT, null=False, related_name='articulo_item_orden_compra')
    cantidad = models.PositiveIntegerField(null=False, default=1)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2, null=False, default=0)
    total_item = models.DecimalField(max_digits=12, decimal_places=2, null=False, default=0)
    estado = models.IntegerField(choices=EstadoEntidades, default=EstadoEntidades.ACTIVO)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, null=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=False)
   
    def save(self, *args, **kwargs):
        # Calcular el total del item
        self.total_item = self.cantidad * self.precio_unitario

        # Si no se ha establecido el precio unitario, tomarlo del artículo
        if self.precio_unitario == 0:
            try:
                lista_precio = self.articulo.listaprecio
                self.precio_unitario = lista_precio.precio_1
                self.total_item = self.cantidad * self.precio_unitario
            except:
                pass
        super().save(*args, **kwargs)
        
        # Actualizar el total de la orden
        self.pedido.actualizar_total()

    def __str__(self):
        return f"{self.cantidad} x {self.articulo.descripcion}"

    class Meta:
        db_table = "items_ordenes_compra_cliente"

