from django.db import models

# Create your models here.
'''
    Definir la entidad (el nombre de la tabla y sus atributos (con tipos y validaciones))
    Cliente
        id_cliente, texto numerico de 8 caracteres, clave principal
        apellidos_nombres, max de 80 caracteres
        fecha_registro, Fecha (formato dd/mm/aaaa)
        fecha_sistema, fecha y hora en que se registre el dato(timestamp)
'''
class Cliente(models.Model):
    id_cliente = models.CharField(primary_key=True, max_length=8, error_messages='El texto debe tener max 8 digitos')
    apellidos_nombres = models.CharField(max_length=80)
    fecha_registro = models.DateField()
    fecha_sistema = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'\nNombres: {self.apellidos_nombres},\n DNI: {self.id_cliente}'

'''
    Crear el modelo Producto
    Producto
        id_producto, numero enntero autocorrelativo que comienza en 1, sera clave principal
        nombre_producto, texto de 50 caracteres como maximo
        descripcion_producto, texto de 500 caracteres multilineas
        precio, numero real positivo de dos decimales
        stock, numero entero mayor o igual que cero
        activo, valor lógico (True si esta activo, de otra forma sera False)
        fecha_vencimiento, tipo fecha (aaaa-mm-dd)
        fecha_registro, tipo fecha y hora (registro del momento del guardado timestamp)
'''
class Producto(models.Model):
    id_producto = models.IntegerField(primary_key=True,serialize=True)
    nombre_producto = models.CharField(max_length=50)
    descripcion_producto = models.TextField(max_length=500)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    activo = models.BooleanField()
    fecha_vencimiento = models.DateField()
    fecha_registro = models.DateTimeField()

    def __str__(self):
        return f'\nID_Producto: {self.id_producto}, Producto: {self.nombre_producto}, Precio:{self.precio}, Stock: {self.stock}, Fecha Vencimiento {self.fecha_vencimiento} '
    
'''
    Captura de la imagen de la tabla Producto en el Admin
    Enviar la captura por el chat grupal
'''