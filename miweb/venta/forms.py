from django import forms
from django.core.validators import RegexValidator
#Importamos informacion de nuestro negocio
from .models import Cliente
from .models import Producto
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
    