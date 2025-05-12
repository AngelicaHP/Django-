from django.db import models
class EstadoEntidades(models.IntegerChoices):
 ACTIVO = 1, "Activo"
 DE_BAJA = 9, "De baja"

class EstadoOrden(models.IntegerChoices):
 PENDIENTE = 1, "Pendiente"
 PROCESANDO = 2, "Procesando"
 COMPLETADA = 3, "Completada"
 CANCELADA = 4, "Cancelada"
