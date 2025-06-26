from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect
# Create your views here.
#En la vista se debe considerar el modelo que se va a usar
from .models import Cliente
from .models import Producto
#Importamos nuestros formularios
from .forms import CreateClienteForms,UpdateClienteForm
from .forms import CreateProductoForms,UpdateProductoForm

# consulta_clientes es la vista que muestra la lista
def consultaClientes(request):
    clientes = Cliente.objects.all().order_by('apellidos_nombres')
    #Estos datos deben estar disponibles para una plantilla (Template)
    #Se creara un diccionario llamado context (será accesible desde la plantilla)
    context = {
        'clientes' : clientes,
        'titulo'   : 'Lista de Clientes'
    }
    #Se devolverá el enlace entre la plantilla y el contexto
    return render(request, 'venta\lista_clientes.html', context)

def crearCliente(request):
    dni_duplicado = False
    if request.method == 'POST':
        form = CreateClienteForms(request.POST)
        if form.is_valid():
            #Grabamos los datos
            form.save()
            messages.success(request, 'Cliente Registrado Correctamente')
            #Se redirecciona a la misma página
            return redirect('crear_cliente')
        else:
            if 'id_cliente' in form.errors:
                for error in form.errors['id_cliente']:
                    #Se recibe del raise
                    if str(error)=="DNI_duplicado":
                        dni_duplicado = True
                        #Se limpian los errores
                        form.errors['id_cliente'].clear()
                        break
    else:
        #No hace nada y devuelve la misma pantalla con los campos limpios
        form = CreateClienteForms()
    context = {
        'form':form,
        #Envia el estado del dni duplicado
        'dni_duplicado':dni_duplicado
    }
    return render(request, 'venta/crear_cliente.html', context)

def actualizarCliente(request):
    cliente = None
    dniBuscado = None
    form = None

    if request.method == 'POST':
        if 'buscar' in request.POST:
            #Buscar el cliente por DNI
            dniBuscado = request.POST.get('dni_busqueda')
            if dniBuscado:
                #intentear considerar la busqueda del cliente
                try:
                    #Obtener un objeto del tipo cliente
                    cliente = Cliente.objects.get(id_cliente = dniBuscado)
                    #Crear un formulario con los datos del objeto cliente
                    form = UpdateClienteForm(instance = cliente)
                    messages.success(request, f'Cliente con DNI {dniBuscado} encontrado')
                # Execpcion de cliente no existe
                except Cliente.DoesNotExist:
                    messages.error(request, f'No se encontro Cliente con DNI {dniBuscado}')
            else:
                messages.error(request, 'Ingrese un DNI existente para buscar')
        elif 'guardar' in request.POST:
            dniBuscado = request.POST.get('dni_busqueda') or request.POST.get('id_cliente')
            if dniBuscado:
                try:
                    cliente = Cliente.objects.get(id_cliente = dniBuscado)
                    form = UpdateClienteForm(request.POST, instance=cliente)
                    if form.is_valid():
                        form.save()
                        messages.success(request, 'Cliente actualizado correctamente')
                        #Formulario con datos actualizados
                        cliente.refresh_from_db()
                        #devolver al formulario
                        form = UpdateClienteForm(instance=cliente)
                    else:
                        messages.error(request, 'Error al actualizar los datos del formulario')
                except Cliente.DoesNotExist:
                    messages.error(request, 'Cliente no encontrado')
            else:
                messages.error(request, 'No se puede encontrar al cliente para actualizar')
    context = {
        'form':form,
        'dni_buscado':dniBuscado,
        'cliente_encontrado':cliente is not None,
        'cliente': cliente
    }
    return render(request, 'venta/u_cliente.html',context)

'''
9 puntos (la proxima se realizar preguntas)
1- Crear la vista de la lista de productos (max de 10 poductos) 
   url: venta/q_producto
2- Crear el formulario de registro de un nuevo producto
   url: venta/crea_producto
'''

# consulta_clientes es la vista que muestra la lista
def consultaProductos(request):
    productos = Producto.objects.all().order_by('nombre_producto')
    #Estos datos deben estar disponibles para una plantilla (Template)
    #Se creara un diccionario llamado context (será accesible desde la plantilla)
    context = {
        'productos' : productos,
        'titulo'   : 'Lista de Productos'
    }
    #Se devolverá el enlace entre la plantilla y el contexto
    return render(request, 'venta\lista_productos.html', context)

def crearProducto(request):
    if request.method == 'POST':
        form = CreateProductoForms(request.POST)
        if form.is_valid():
            #Grabamos los datos
            form.save()
            messages.success(request, 'Producto Registrado Correctamente')
            #Se redirecciona a la misma página
            return redirect('crear_producto')
    else:
        #No hace nada y devuelve la misma pantalla con los campos limpios
        form = CreateProductoForms()
    return render(request, 'venta/crear_producto.html', {'form' : form})

#Eliminar Clientes
def borrarCliente(request):
    clientesEncontrados = []
    tipoBusqueda = 'dni'
    # dentro de las cajas
    terminoBusqueda = ''
    totalRegistros = 0

    if request.method == 'POST':
        #
        if 'consultar' in request.POST:
            #Realizar la búsqueda
            tipoBusqueda = request.POST.get('tipoBusqueda','dni')
            terminoBusqueda = request.POST.get('terminoBusqueda','').strip()
            if terminoBusqueda:
                #proceder a realizar la busqueda
                if tipoBusqueda == 'dni':
                    try:
                        cliente = Cliente.objects.get(id_cliente = terminoBusqueda)
                        clientesEncontrados = [cliente]
                    except Cliente.DoesNotExist:
                        messages.error(request, 'No se encontró cliente con ese DNI')
                elif tipoBusqueda == 'nombre':
                    clientesEncontrados = Cliente.objects.filter(
                        #Obtiene la coincidencias
                        apellidos_nombres__icontains = terminoBusqueda
                    ).order_by('id_cliente')
                    if not clientesEncontrados:
                        messages.error(request, 'No se encontraron clientes con ese nombre')
                totalRegistros = len(clientesEncontrados)
                if totalRegistros > 0:
                    messages.success(request, f'Se encontraron {totalRegistros} registro(s)')
            else:
                messages.error(request, 'Ingrese un término de búsqueda')
        elif 'eliminar' in request.POST:
            #Eliminar cliente
            dniEliminar = request.POST.get('dniEliminar')
            if dniEliminar:
                try:
                    #buscar al cliente a eliminar
                    cliente = Cliente.objects.get(id_cliente = dniEliminar)
                    cliente.delete()
                    messages.success(request, f'Cliente con DNI: {dniEliminar} eliminado correctamente')
                    #Volver a hacer la búsqueda para actualizar la lista
                    tipoBusqueda = request.POST.get('tipoBusqueda_actual', 'dni')
                    terminoBusqueda = request.POST.get('terminoBusqueda_actual','')

                    if terminoBusqueda:
                        if tipoBusqueda == 'dni':
                            #Para DNI, no mostrar nada porque ya se eliminó
                            clientesEncontrados = []
                        elif tipoBusqueda == 'nombre':
                            #En este caso hay que buscar nuevamente lo que queda
                            clientesEncontrados = Cliente.objects.filter(
                                apellidos_nombres__icontains = terminoBusqueda
                            ).order_by('id_cliente')
                        totalRegistros = len(clientesEncontrados)
                except Cliente.DoesNotExist:
                    messages.error(request, 'Cliente no encontrado')
    context = {
        'clientesEncontrados' : clientesEncontrados,
        'tipoBusqueda' : tipoBusqueda,
        'terminoBusqueda' : terminoBusqueda,
        'totalRegistros' : totalRegistros
    }
    return render(request, 'venta/borrar_cliente.html', context)

def actualizarProducto(request):
    producto = None
    idBuscado = None
    form = None

    if request.method == 'POST':
        if 'buscar' in request.POST:
            #Buscar el producto por ID
            idBuscado = request.POST.get('id_busqueda')
            if idBuscado:
                #intentear considerar la busqueda del producto
                try:
                    #Obtener un objeto del tipo producto
                    producto = Producto.objects.get(id_producto = idBuscado)
                    #Crear un formulario con los datos del objeto cliente
                    form = UpdateProductoForm(instance = producto)
                    messages.success(request, f'Producto con ID {idBuscado} encontrado')
                # Execpcion de cliente no existe
                except Producto.DoesNotExist:
                    messages.error(request, f'No se encontro Producto con ID {idBuscado}')
            else:
                messages.error(request, 'Ingrese un ID existente para buscar')
        elif 'guardar' in request.POST:
            idBuscado = request.POST.get('id_busqueda') or request.POST.get('id_producto')
            if idBuscado:
                try:
                    producto = Producto.objects.get(id_producto = idBuscado)
                    form = UpdateProductoForm(request.POST, instance=producto)
                    if form.is_valid():
                        form.save()
                        messages.success(request, 'Producto actualizado correctamente')
                        #Formulario con datos actualizados
                        producto.refresh_from_db()
                        #devolver al formulario
                        form = UpdateProductoForm(instance=producto)
                    else:
                        messages.error(request, 'Error al actualizar los datos del formulario')
                except Producto.DoesNotExist:
                    messages.error(request, 'Producto no encontrado')
            else:
                messages.error(request, 'No se puede encontrar al Producto para actualizar')
    context = {
        'form':form,
        'id_buscado':idBuscado,
        'producto_encontrado':producto is not None,
        'producto': producto
    }
    return render(request, 'venta/u_producto.html',context)

#Eliminar Productos
def borrarProducto(request):
    productosEncontrados = []
    tipoBusqueda = 'dni'
    # dentro de las cajas
    terminoBusqueda = ''
    totalRegistros = 0

    if request.method == 'POST':
        #
        if 'consultar' in request.POST:
            #Realizar la búsqueda
            tipoBusqueda = request.POST.get('tipoBusqueda','id')
            terminoBusqueda = request.POST.get('terminoBusqueda','').strip()
            if terminoBusqueda:
                #proceder a realizar la busqueda
                if tipoBusqueda == 'id':
                    try:
                        producto = Producto.objects.get(id_producto = terminoBusqueda)
                        productosEncontrados = [producto]
                    except Producto.DoesNotExist:
                        messages.error(request, 'No se encontró producto con ese ID')
                elif tipoBusqueda == 'nombre':
                    productosEncontrados = Producto.objects.filter(
                        #Obtiene la coincidencias
                        nombre_producto__icontains = terminoBusqueda
                    ).order_by('id_producto')
                    if not productosEncontrados:
                        messages.error(request, 'No se encontraron productos con ese nombre')
                totalRegistros = len(productosEncontrados)
                if totalRegistros > 0:
                    messages.success(request, f'Se encontraron {totalRegistros} registro(s)')
            else:
                messages.error(request, 'Ingrese un término de búsqueda')
        elif 'eliminar' in request.POST:
            #Eliminar cliente
            idEliminar = request.POST.get('idEliminar')
            if idEliminar:
                try:
                    #buscar al cliente a eliminar
                    producto = Producto.objects.get(id_producto = idEliminar)
                    producto.delete()
                    messages.success(request, f'Producto con ID: {idEliminar} eliminado correctamente')
                    #Volver a hacer la búsqueda para actualizar la lista
                    tipoBusqueda = request.POST.get('tipoBusqueda_actual', 'id')
                    terminoBusqueda = request.POST.get('terminoBusqueda_actual','')

                    if terminoBusqueda:
                        if tipoBusqueda == 'id':
                            #Para DNI, no mostrar nada porque ya se eliminó
                            productosEncontrados = []
                        elif tipoBusqueda == 'nombre':
                            #En este caso hay que buscar nuevamente lo que queda
                            productosEncontrados = Producto.objects.filter(
                                nombre_producto__icontains = terminoBusqueda
                            ).order_by('id_producto')
                        totalRegistros = len(productosEncontrados)
                except Producto.DoesNotExist:
                    messages.error(request, 'Producto no encontrado')
    context = {
        'productosEncontrados' : productosEncontrados,
        'tipoBusqueda' : tipoBusqueda,
        'terminoBusqueda' : terminoBusqueda,
        'totalRegistros' : totalRegistros
    }
    return render(request, 'venta/borrar_producto.html', context)