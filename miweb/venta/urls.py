from django.urls import path
from . import views

urlpatterns = [
    path('venta/q_cliente',views.consultaClientes, name='lista_clientes'),
    path('venta/c_cliente',views.crearCliente, name='crear_cliente'),
    path('venta/u_cliente',views.actualizarCliente, name='actualizar_cliente'),
    path('venta/q_producto',views.consultaProductos, name='lista_productos'),
    path('venta/c_producto',views.crearProducto, name='crear_producto')   
]
