from django.contrib import admin

# Register your models here.
from .models import Cliente
from .models import Producto

#Agregar el modelo Cliente al Admin
admin.site.register(Cliente)
admin.site.register(Producto)