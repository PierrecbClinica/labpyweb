from django.urls import path, re_path
from . import views

urlpatterns = [
    path('',views.userLogin, name='login'),
    path('logout/',views.userlogout, name='logout'),
    #pagina principal
    path('home/',views.home, name='home'),
    path('venta/q_cliente',views.consultaClientes, name='lista_clientes'),
    path('venta/c_cliente',views.crearCliente, name='crear_cliente'),
    path('venta/u_cliente',views.actualizarCliente, name='actualizar_cliente'),
    path('venta/d_cliente',views.borrarCliente, name='borrar_cliente'),
    path('venta/q_producto',views.consultaProductos, name='lista_productos'),
    path('venta/c_producto',views.crearProducto, name='crear_producto'),
    path('venta/u_producto',views.actualizarProducto, name='actualizar_producto'),   
    path('venta/d_producto',views.borrarProducto, name='borrar_producto'),
    path('venta/q_venta',views.consultaVentas, name='lista_ventas'),
    path('venta/c_venta',views.crearVenta, name='crear_venta'),
    path('venta/u_venta',views.actualizarVenta, name='actualizar_venta'),
    path('venta/d_venta',views.borrarVenta, name='borrar_venta'),
    path('venta/q_detalleVenta',views.consultaDetalleVentas, name='lista_detalleVentas'),
    path('venta/c_detalleVenta',views.crearDetalleVenta, name='crear_detalleVenta'),
    path('venta/u_detalleVenta',views.actualizarDetalleVenta, name='actualizar_detalleVenta'),
    path('venta/d_detalleVenta',views.borrarDetalleVenta, name='borrar_detalleVenta'),
    #Poner al final de la lista
    re_path(r'^.*/$', views.handler_undefined_url, name = 'catch_all'),
]
