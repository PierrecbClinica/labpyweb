from django import forms
from django.core.validators import RegexValidator
#Importamos informacion de nuestro negocio
from .models import Cliente
from .models import Producto
from .models import Venta
from .models import DetallesVenta
#Para gestionar errores
from django.core.exceptions import ValidationError
#from .models import ModelForm

class CreateClienteForms(forms.ModelForm):
    class Meta:
        model = Cliente
        #Atributos de modelos cuyos valores se agregaran
        fields = ['id_cliente','apellidos_nombres','fecha_registro']
        labels = {
            'id_cliente':'DNI',
            'apellidos_nombres':'Apellidos y Nombres',
            'fecha_registro':'Fecha de Registro'
        }
        widgets = {
            'fecha_registro' : forms.DateInput(attrs={'type':'date'})
        }
        error_messages = {
            'id_cliente' : {
                'max_length' : "El DNI debe tener máximo 8 caracteres",
            }
        }
    def clean_id_cliente(self):
        #id_cliente viene de la plantilla(html)
        id_cliente = self.cleaned_data.get('id_cliente')

        if id_cliente:
            #Verifica si ya existe un DNI
            if Cliente.objects.filter(id_cliente = id_cliente).exists():
                #Realiza un lanzamiento de error
                raise ValidationError("DNI_duplicado")
            return id_cliente
    
#Clase para modificar un cliente
class UpdateClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['apellidos_nombres','fecha_registro']
        labels = {
            'apellidos_nombres':'Apellidos y Nombres',
            'fecha_registro':'Fecha de Registro'
        }
        widgets = {
            'apellidos_nombres': forms.TextInput(
                attrs={
                    'placeholder' : 'Ingrese apellidos y nombres'
                }
            ),
            'fecha_registro' : forms.DateInput(
                attrs={
                    'type':'date'
                }, 
                format='%Y-%m-%d'
            )
        }


class CreateProductoForms(forms.ModelForm):
    class Meta:
        model = Producto
        #Atributos de modelos cuyos valores se agregaran
        fields = ['id_producto','nombre_producto','descripcion_producto','precio','stock','activo','fecha_vencimiento','fecha_registro']
        labels = {
            'id_producto':'ID del Producto',
            'nombre_producto':'Nombre del Producto',
            'descripcion_producto':'Descripción',
            'precio':'Precio',
            'stock':'Stock',
            'activo':'Activo',
            'fecha_vencimiento':'Fecha de Vencimiento',
            'fecha_registro':'Fecha de Registro'
        }
        widgets = {
            'fecha_vencimiento' : forms.DateInput(attrs={'type':'date'}),
            'fecha_registro' : forms.DateInput(attrs={'type':'date'})
        }
        error_messages = {
            'id_producto' : {
                'max_length' : "El DNI ya existe",
            }
        }
    
    #Clase para modificar un producto
class UpdateProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre_producto', 'descripcion_producto', 'precio', 'stock', 'activo', 'fecha_vencimiento', 'fecha_registro']
        labels = {
            'nombre_producto':'Nombre del Producto',
            'descripcion_producto':'Descripción del Producto',
            'precio':'Precio del Producto',
            'stock':'Stock del Producto',
            'activo':'Activo',
            'fecha_vencimiento':'Fecha de Vencimiento del Producto',
            'fecha_registro':'Fecha de Registro'
        }
        widgets = {
            'nombre_producto': forms.TextInput(
                attrs={
                    'placeholder' : 'Ingrese nombre del producto'
                }
            ),
            'descripcion_producto': forms.TextInput(
                attrs={
                    'placeholder' : 'Ingrese descripción del producto'
                }
            ),
            # 'precio': forms.TextInput(
            #     attrs={
            #         'placeholder' : 'Ingrese precio del producto'
            #     }
            # ),
            # 'stock': forms.TextInput(
            #     attrs={
            #         'placeholder' : 'Ingrese stock del producto'
            #     }
            # ),
            
            'fecha_vencimiento': forms.DateInput(
                attrs={
                    'type':'date'
                }, 
                format='%Y-%m-%d'
            ),
            'fecha_registro' : forms.DateInput(
                attrs={
                    'type':'date'
                }, 
                format='%Y-%m-%d'
            )
        }

class CreateVentaForms(forms.ModelForm):
    class Meta:
        model = Venta
        clientes = Cliente.objects.all()
        #Atributos de modelos cuyos valores se agregaran
        fields = ['id_venta','id_cliente','total','fecha_registro']
        labels = {
            'id_venta':'Codigo Venta',
            'id_cliente':'DNI Cliente',
            'total':'Total',
            'fecha_registro':'Fecha de Registro'
        }
        widgets = {
            'fecha_registro' : forms.DateInput(attrs={'type':'date'}),
            #'id_cliente':forms.ModelChoiceField(queryset=Clientes)
        }

    def clean_id_venta(self):
        #id_cliente viene de la plantilla(html)
        id_venta = self.cleaned_data.get('id_venta')

        if id_venta:
            #Verifica si ya existe un DNI
            if Venta.objects.filter(id_venta = id_venta).exists():
                #Realiza un lanzamiento de error
                raise ValidationError("ID_duplicado")
            return id_venta
        
    def add_Venta(self):
        #id_cliente viene de la plantilla(html)
        id_venta = self.cleaned_data.get('id_venta')
        id_cliente = self.cleaned_data.get('id_cliente')
        fecha_registro = self.cleaned_data.get('fecha_registro')
        total = 0

        if id_cliente and id_venta and fecha_registro:
            detalleVentaEncontradas = DetallesVenta.objects.filter(id_venta = id_venta)
            subTotal = detalleVentaEncontradas.values('subTotal')
            total = total + subTotal
            #Verifica si ya existe un DNI
            Venta.objects.create(id_cliente=id_cliente,total=total,fecha_registro=fecha_registro)

#Clase para modificar una Venta
class UpdateVentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        clientes = Cliente.objects.all()
        fields = ['id_venta','id_cliente','fecha_registro']
        labels = {
            'id_venta':'ID Venta',
            'id_cliente':'DNI',
            'fecha_registro':'Fecha de Registro'
        }
        widgets = {
            #'id_cliente':forms.ModelChoiceField(queryset=clientes),
            'fecha_registro' : forms.DateInput(attrs={'type':'date'},format='%Y-%m-%d')
        }

class CreateDetalleVentaForms(forms.ModelForm):
    class Meta:
        model = DetallesVenta
        # productos = Producto.objects.all()
        #Atributos de modelos cuyos valores se agregaran
        fields = ['id_detalleVenta','id_venta','id_producto','precio','cantidad','subTotal']
        labels = {
            'id_detalleVenta':'ID Detalle Venta',
            'id_venta':'Codigo Venta',
            'id_producto':'ID Producto',
            'precio':'Precio del Producto',
            'cantidad':'Cantidad del Producto Selecionado',
            'subTotal':'Total a pagar por Producto'
        }

    def clean_id_detalleVenta(self):
        #id_cliente viene de la plantilla(html)
        id_detalleVenta = self.cleaned_data.get('id_detalleVenta')

        if id_detalleVenta:
            #Verifica si ya existe un DNI
            if DetallesVenta.objects.filter(id_detalleVenta = id_detalleVenta).exists():
                #Realiza un lanzamiento de error
                raise ValidationError("ID_duplicado")
            return id_detalleVenta
    
    def add_detalleVenta(self):
        #id_cliente viene de la plantilla(html)
        id_detalleVenta = self.cleaned_data.get('id_detalleVenta')
        id_producto = self.cleaned_data.get('id_producto')
        id_venta = self.cleaned_data.get('id_venta')
        cantidad = self.cleaned_data.get('cantidad')
        precio = 0

        if id_detalleVenta and id_producto and cantidad:
            productoEncontrado = Producto.objects.filter(id_producto = id_producto)
            precio = productoEncontrado.values('precio')
            subTotal = cantidad * precio
            #Verifica si ya existe un DNI
            DetallesVenta.objects.create(id_detalleVenta=id_detalleVenta,id_venta=id_venta,id_producto=id_producto,cantidad=cantidad,precio=precio,subTotal=subTotal)

#Clase para modificar una Venta
class UpdateDetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetallesVenta
        # productos = Producto.objects.all()
        fields = ['id_venta','id_producto','cantidad']
        labels = {
            'id_venta':'ID Venta',
            'id_producto':'ID Producto',
            'cantidad':'cantidad'
        }
