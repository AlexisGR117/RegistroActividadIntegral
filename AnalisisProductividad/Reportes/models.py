from django.db import models


# Create your models here.
class Actividad(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField()
    nombre_computador = models.CharField(max_length=100)
    usuario = models.CharField(max_length=100)
    titulo_ventana = models.CharField(max_length=255, null=True, blank=True)
    nombre_proceso = models.CharField(max_length=255)
    pantalla = models.CharField(max_length=50)
    segundos_empleados = models.DecimalField(max_digits=20, decimal_places=7)

    class Meta:
        db_table = 'actividades'
        managed = False


class Categoria(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255)

    def __str__(self):
        return str(self.nombre)


class ActividadCategoria(models.Model):
    id = models.AutoField(primary_key=True)
    titulo_ventana = models.CharField(max_length=255, null=True, blank=True)
    nombre_proceso = models.CharField(max_length=255, null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    def __str__(self):
        return (
            (self.nombre_proceso or 'N/A') +
            ' - ' +
            (self.titulo_ventana or 'N/A') +
            ' - ' +
            str(self.categoria)
        )
