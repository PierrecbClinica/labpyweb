from django.contrib import admin

# Register your models here.
from .models import Cliente
from .models import Producto
from .models import Venta
from .models import DetallesVenta

#Agregar el modelo Cliente al Admin
admin.site.register(Cliente)
admin.site.register(Producto)
admin.site.register(Venta)
admin.site.register(DetallesVenta)