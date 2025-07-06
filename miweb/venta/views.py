from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required,permission_required
from django.http import HttpResponseForbidden
# Create your views here.
#En la vista se debe considerar el modelo que se va a usar
from .models import Cliente
from .models import Producto
from .models import Venta
from .models import DetallesVenta
#Importamos nuestros formularios
from .forms import CreateClienteForms,UpdateClienteForm
from .forms import CreateProductoForms,UpdateProductoForm
from .forms import CreateVentaForms,UpdateVentaForm
from .forms import CreateDetalleVentaForms,UpdateDetalleVentaForm

def handler_undefined_url(request):
    '''
    Gestiona los urls que no estan definidos
    '''
    if not request.user.is_authenticated:
        messages.warning(request, 'Debe iniciar sesión para accedaer al sistema')
        return redirect('login')
    else:
        messages.info(request, 'La página solicitada no existe. Se redirigirá al inicio')
        return redirect('home')

def userLogin(request):
    #Si ya esta autenticado, enviarlo a home
    if request.user.is_authenticated:
        return redirect('home')
    #Si no está autenticado pedir usuario y clave
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            user = authenticate(request, username = username, password = password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Error de usuario o clave')
        else:
            messages.error(request, 'Ingrese clave y contraseña')
    #Si hay falla de autenticación, permitir reintentar
    return render(request, 'venta/login.html')

def userlogout(request):
    logout(request)
    messages.success(request, 'sesion cerrada correctamente')
    return redirect('login')

#Vista principal del sistema
@login_required
def home(request):
    #Obtener los permisos
    userPermissions = {
        'canManageClients' : (
            request.user.is_superuser or 
            request.user.groups.filter(name = 'grp_cliente').exists() or
            request.user.has_perm('venta.add_cliente')
        ),
        'canManageProducts' : (
            request.user.is_superuser or 
            request.user.groups.filter(name = 'grp_producto').exists() or
            request.user.has_perm('venta.add_producto')
        ),
        'canManageProvider' : (
            request.user.is_superuser or 
            request.user.groups.filter(name = 'grp_provedor').exists()
        ),
        'canManageSales' : (
            request.user.is_superuser or 
            request.user.groups.filter(name = 'grp_venta').exists()
        ),
        'canManageDetailSales' : (
            request.user.is_superuser or 
            request.user.groups.filter(name = 'grp_detalleVenta').exists()
        ),
        'isAdmin' : request.user.is_superuser
    }

    context = {
        'userPermissions' : userPermissions,
        'user' : request.user
    }
    return render(request, 'venta\home.html', context)

# consulta_clientes es la vista que muestra la lista
@login_required
@permission_required('venta.view_cliente',raise_exception=True)
def consultaClientes(request):
    #verificar los permisos
    if not (
        request.user.is_superuser or 
        request.user.groups.filter(name = 'grp_cliente').exists() or
        request.user.has_perm('venta.view_cliente')):
        return HttpResponseForbidden('No tiene permisos para ingresar aquí')
    clientes = Cliente.objects.all().order_by('apellidos_nombres')
    #Estos datos deben estar disponibles para una plantilla (Template)
    #Se creara un diccionario llamado context (será accesible desde la plantilla)
    context = {
        'clientes' : clientes,
        'titulo'   : 'Lista de Clientes'
    }
    #Se devolverá el enlace entre la plantilla y el contexto
    return render(request, 'venta\lista_clientes.html', context)

@login_required
@permission_required('venta.add_cliente',raise_exception=True)
def crearCliente(request):
    #Verificamos los permisos
    if not (
        request.user.is_superuser or 
        request.user.groups.filter(name = 'grp_cliente').exists() or
        request.user.has_perm('venta.add_cliente')):
        return HttpResponseForbidden('No tiene permisos para crear cliente')
    
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

@login_required
@permission_required('venta.change_cliente',raise_exception=True)
def actualizarCliente(request):

    #Verificamos los permisos
    if not (
        request.user.is_superuser or 
        request.user.groups.filter(name = 'grp_cliente').exists() or
        request.user.has_perm('venta.change_cliente')):
        return HttpResponseForbidden('No tiene permisos para modificar cliente')
    
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
@login_required
@permission_required('venta.delete_cliente',raise_exception=True)
def borrarCliente(request):

    #Verificamos los permisos
    if not (
        request.user.is_superuser or 
        request.user.groups.filter(name = 'grp_cliente').exists() or
        request.user.has_perm('venta.delete_cliente')):
        return HttpResponseForbidden('No tiene permisos para borrar cliente')
    
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

# consulta_ventas es la vista que muestra la lista
@login_required
@permission_required('venta.view_venta',raise_exception=True)
def consultaVentas(request):
    #verificar los permisos
    if not (
        request.user.is_superuser or 
        request.user.groups.filter(name = 'grp_venta').exists() or
        request.user.has_perm('venta.view_venta')):
        return HttpResponseForbidden('No tiene permisos para ingresar aquí')
    ventas = Venta.objects.all().order_by('id_venta')
    detalleVentas = DetallesVenta.objects.all().order_by('id_venta')
    #Estos datos deben estar disponibles para una plantilla (Template)
    #Se creara un diccionario llamado context (será accesible desde la plantilla)
    context = {
        'ventas' : ventas,
        'detalleVentas' : detalleVentas,
        'titulo'   : 'Lista de Ventas'
    }
    #Se devolverá el enlace entre la plantilla y el contexto
    return render(request, 'venta\lista_ventas.html', context)

@login_required
@permission_required('venta.add_venta',raise_exception=True)
def crearVenta(request):
    productosEncontrados = []
    idBuscado = ''
    #Verificamos los permisos
    if not (
        request.user.is_superuser or 
        request.user.groups.filter(name = 'grp_venta').exists() or
        request.user.has_perm('venta.add_venta')):
        return HttpResponseForbidden('No tiene permisos para crear una venta')
    
    Codigo_VentaDuplicado = False
    if request.method == 'POST':
        idBuscado = request.POST.get('idBuscado','').strip()
        form = CreateVentaForms(request.POST)
        form2 = CreateDetalleVentaForms(request.POST)
        messages.success(request, 'Creando Venta')
        if form.is_valid() and form2.is_valid():
            #Grabamos los datos
            # form.add_Venta()
            # form2.add_detalleVenta()
            messages.success(request, 'Venta empesando a gravar')
            form.save()
            form2.save()
            messages.success(request, 'Venta Registrada Correctamente')
            #Se redirecciona a la misma página
            return redirect('crear_venta')
        else:
            if 'id_venta' in form.errors:
                for error in form.errors['id_venta']:
                    #Se recibe del raise
                    if str(error)=="Codigo_VentaDuplicado":
                        Codigo_VentaDuplicado = True
                        #Se limpian los errores
                        form.errors['id_venta'].clear()
                        break
    else:
        #No hace nada y devuelve la misma pantalla con los campos limpios
        form = CreateVentaForms()
        form2 = CreateDetalleVentaForms()
    context = {
        'form':form,
        'form2':form2,
        'idBuscado':idBuscado,
        'productoEncontrado':productosEncontrados,
        #Envia el estado del dni duplicado
        'Codigo_VentaDuplicado':Codigo_VentaDuplicado
    }
    return render(request, 'venta/crear_venta.html', context)

@login_required
@permission_required('venta.change_venta',raise_exception=True)
def actualizarVenta(request):

    #Verificamos los permisos
    if not (
        request.user.is_superuser or 
        request.user.groups.filter(name = 'grp_venta').exists() or
        request.user.has_perm('venta.change_venta')):
        return HttpResponseForbidden('No tiene permisos para modificar ventas')
    
    venta = None
    idBuscado = None
    form = None

    if request.method == 'POST':
        if 'buscar' in request.POST:
            #Buscar el cliente por DNI
            idBuscado = request.POST.get('id_busqueda')
            if idBuscado:
                #intentear considerar la busqueda del cliente
                try:
                    #Obtener un objeto del tipo cliente
                    venta = Venta.objects.get(id_venta = idBuscado)
                    #Crear un formulario con los datos del objeto cliente
                    form = UpdateVentaForm(instance = venta)
                    messages.success(request, f'Venta con ID {idBuscado} encontrado')
                # Execpcion de cliente no existe
                except Venta.DoesNotExist:
                    messages.error(request, f'No se encontro Venta con ID {idBuscado}')
            else:
                messages.error(request, 'Ingrese un ID existente para buscar')
        elif 'guardar' in request.POST:
            idBuscado = request.POST.get('id_busqueda') or request.POST.get('id_venta')
            if idBuscado:
                try:
                    venta = Venta.objects.get(id_venta = idBuscado)
                    form = UpdateVentaForm(request.POST, instance=venta)
                    if form.is_valid():
                        form.save()
                        messages.success(request, 'Venta actualizada correctamente')
                        #Formulario con datos actualizados
                        venta.refresh_from_db()
                        #devolver al formulario
                        form = UpdateVentaForm(instance=venta)
                    else:
                        messages.error(request, 'Error al actualizar los datos del formulario')
                except Venta.DoesNotExist:
                    messages.error(request, 'Venta no encontrada')
            else:
                messages.error(request, 'No se puede encontrar la venta para actualizar')
    context = {
        'form':form,
        'id_buscado':idBuscado,
        'venta_encontrado':venta is not None,
        'venta': venta
    }
    return render(request, 'venta/u_venta.html',context)

#Eliminar Ventas
@login_required
@permission_required('venta.delete_venta',raise_exception=True)
def borrarVenta(request):

    #Verificamos los permisos
    if not (
        request.user.is_superuser or 
        request.user.groups.filter(name = 'grp_venta').exists() or
        request.user.has_perm('venta.delete_venta')):
        return HttpResponseForbidden('No tiene permisos para borrar venta')
    
    ventasEncontradas = []
    tipoBusqueda = 'ID'
    # dentro de las cajas
    terminoBusqueda = ''
    totalRegistros = 0

    if request.method == 'POST':
        #
        if 'consultar' in request.POST:
            #Realizar la búsqueda
            tipoBusqueda = request.POST.get('tipoBusqueda','ID')
            terminoBusqueda = request.POST.get('terminoBusqueda','').strip()
            if terminoBusqueda:
                #proceder a realizar la busqueda
                if tipoBusqueda == 'ID':
                    try:
                        venta = Venta.objects.get(id_venta = terminoBusqueda)
                        ventasEncontradas = [venta]
                    except Venta.DoesNotExist:
                        messages.error(request, 'No se encontró venta con ese código')
                elif tipoBusqueda == 'cliente':
                    ventasEncontradas = Venta.objects.filter(
                        #Obtiene la coincidencias
                        apellidos_nombres__icontains = terminoBusqueda
                    ).order_by('id_cliente')
                    if not ventasEncontradas:
                        messages.error(request, 'No se encontraron ventas con ese DNI cliente')
                totalRegistros = len(ventasEncontradas)
                if totalRegistros > 0:
                    messages.success(request, f'Se encontraron {totalRegistros} registro(s)')
            else:
                messages.error(request, 'Ingrese un término de búsqueda')
        elif 'eliminar' in request.POST:
            #Eliminar venta
            idEliminar = request.POST.get('idEliminar')
            if idEliminar:
                try:
                    #buscar la venta a eliminar
                    venta = Venta.objects.get(id_venta = idEliminar)
                    venta.delete()
                    messages.success(request, f'venta con ID: {idEliminar} eliminado correctamente')
                    #Volver a hacer la búsqueda para actualizar la lista
                    tipoBusqueda = request.POST.get('tipoBusqueda_actual', 'id')
                    terminoBusqueda = request.POST.get('terminoBusqueda_actual','')

                    if terminoBusqueda:
                        if tipoBusqueda == 'id':
                            #Para ID, no mostrar nada porque ya se eliminó
                            ventasEncontradas = []
                        elif tipoBusqueda == 'cliente':
                            #En este caso hay que buscar nuevamente lo que queda
                            ventasEncontradas = Venta.objects.filter(
                                id_cliente__icontains = terminoBusqueda
                            ).order_by('id_cliente')
                        totalRegistros = len(ventasEncontradas)
                except Venta.DoesNotExist:
                    messages.error(request, 'Venta no encontrada')
    context = {
        'ventasEncontradas' : ventasEncontradas,
        'tipoBusqueda' : tipoBusqueda,
        'terminoBusqueda' : terminoBusqueda,
        'totalRegistros' : totalRegistros
    }
    return render(request, 'venta/borrar_venta.html', context)

# consulta_ventas es la vista que muestra la lista
@login_required
@permission_required('venta.view_detalleVenta',raise_exception=True)
def consultaDetalleVentas(request):
    #verificar los permisos
    if not (
        request.user.is_superuser or 
        request.user.groups.filter(name = 'grp_detalleVenta').exists() or
        request.user.has_perm('venta.view_detalleVenta')):
        return HttpResponseForbidden('No tiene permisos para ingresar aquí')
    detalleVentas = DetallesVenta.objects.all().order_by('id_detalleVenta')
    #Estos datos deben estar disponibles para una plantilla (Template)
    #Se creara un diccionario llamado context (será accesible desde la plantilla)
    context = {
        'detalleVentas' : detalleVentas,
        'titulo'   : 'Lista de Ventas'
    }
    #Se devolverá el enlace entre la plantilla y el contexto
    return render(request, 'venta\lista_detalleVentas.html', context)

@login_required
@permission_required('venta.add_DetalleVenta',raise_exception=True)
def crearDetalleVenta(request):
    productosEncontrados = []
    idBuscado = ''
    #Verificamos los permisos
    if not (
        request.user.is_superuser or 
        request.user.groups.filter(name = 'grp_detalleVenta').exists() or
        request.user.has_perm('venta.add_detalleVenta')):
        return HttpResponseForbidden('No tiene permisos para crear un detalle de venta')
    
    Codigo_VentaDuplicado = False
    if request.method == 'POST':
        idBuscado = request.POST.get('idBuscado','').strip()
        # form = CreateVentaForms(request.POST)
        form2 = CreateDetalleVentaForms(request.POST)
        # messages.success(request, 'Creando Venta')
        if form2.is_valid() and form2.is_valid():
            #Grabamos los datos
            # form.add_Venta()
            # form2.add_detalleVenta()
            # messages.success(request, 'Venta empesando a gravar')
            # form.save()
            form2.save()
            messages.success(request, 'Venta Registrada Correctamente')
            #Se redirecciona a la misma página
            return redirect('crear_detalleVenta')
        else:
            if 'id_detalleVenta' in form2.errors:
                for error in form2.errors['id_detalleVenta']:
                    #Se recibe del raise
                    if str(error)=="Codigo_VentaDuplicado":
                        Codigo_VentaDuplicado = True
                        #Se limpian los errores
                        form2.errors['id_detalleVenta'].clear()
                        break
    else:
        #No hace nada y devuelve la misma pantalla con los campos limpios
        # form = CreateVentaForms()
        form2 = CreateDetalleVentaForms()
    context = {
        # 'form':form,
        'form2':form2,
        'idBuscado':idBuscado,
        'productoEncontrado':productosEncontrados,
        #Envia el estado del dni duplicado
        'Codigo_VentaDuplicado':Codigo_VentaDuplicado
    }
    return render(request, 'venta/crear_detalleVenta.html', context)

@login_required
@permission_required('venta.change_detalleVenta',raise_exception=True)
def actualizarDetalleVenta(request):

    #Verificamos los permisos
    if not (
        request.user.is_superuser or 
        request.user.groups.filter(name = 'grp_detalleVenta').exists() or
        request.user.has_perm('venta.change_detalleVenta')):
        return HttpResponseForbidden('No tiene permisos para modificar detalles de ventas')
    
    detalleVenta = None
    idBuscado = None
    form = None

    if request.method == 'POST':
        if 'buscar' in request.POST:
            #Buscar el cliente por DNI
            idBuscado = request.POST.get('id_busqueda')
            if idBuscado:
                #intentear considerar la busqueda del cliente
                try:
                    #Obtener un objeto del tipo cliente
                    detalleVenta = DetallesVenta.objects.get(id_detalleVenta = idBuscado)
                    #Crear un formulario con los datos del objeto cliente
                    form = UpdateDetalleVentaForm(instance = detalleVenta)
                    messages.success(request, f'Detalle de Venta con ID {idBuscado} encontrado')
                # Execpcion de cliente no existe
                except DetallesVenta.DoesNotExist:
                    messages.error(request, f'No se encontro Detalle de Venta con ID {idBuscado}')
            else:
                messages.error(request, 'Ingrese un ID existente para buscar')
        elif 'guardar' in request.POST:
            idBuscado = request.POST.get('id_busqueda') or request.POST.get('id_detalleVenta')
            if idBuscado:
                try:
                    detalleVenta = DetallesVenta.objects.get(id_detalleVenta = idBuscado)
                    form = UpdateDetalleVentaForm(request.POST, instance=detalleVenta)
                    if form.is_valid():
                        form.save()
                        messages.success(request, 'Detalle de Venta actualizada correctamente')
                        #Formulario con datos actualizados
                        detalleVenta.refresh_from_db()
                        #devolver al formulario
                        form = UpdateDetalleVentaForm(instance=detalleVenta)
                    else:
                        messages.error(request, 'Error al actualizar los datos del formulario')
                except DetallesVenta.DoesNotExist:
                    messages.error(request, 'Venta no encontrada')
            else:
                messages.error(request, 'No se puede encontrar el detalle de venta para actualizar')
    context = {
        'form':form,
        'id_buscado':idBuscado,
        'detalleVenta_encontrado':detalleVenta is not None,
        'detalleVenta': detalleVenta
    }
    return render(request, 'venta/u_detalleVenta.html',context)

#Eliminar Ventas
@login_required
@permission_required('venta.delete_detalleVenta',raise_exception=True)
def borrarDetalleVenta(request):

    #Verificamos los permisos
    if not (
        request.user.is_superuser or 
        request.user.groups.filter(name = 'grp_detalleVenta').exists() or
        request.user.has_perm('venta.delete_detalleVenta')):
        return HttpResponseForbidden('No tiene permisos para borrar detalles de venta')
    
    ventasEncontradas = []
    tipoBusqueda = 'ID'
    # dentro de las cajas
    terminoBusqueda = ''
    totalRegistros = 0

    if request.method == 'POST':
        #
        if 'consultar' in request.POST:
            #Realizar la búsqueda
            tipoBusqueda = request.POST.get('tipoBusqueda','ID')
            terminoBusqueda = request.POST.get('terminoBusqueda','').strip()
            if terminoBusqueda:
                #proceder a realizar la busqueda
                if tipoBusqueda == 'ID':
                    try:
                        detalleVenta = DetallesVenta.objects.get(id_detalleVenta = terminoBusqueda)
                        ventasEncontradas = [detalleVenta]
                    except DetallesVenta.DoesNotExist:
                        messages.error(request, 'No se encontró detalle de venta con ese código')
                elif tipoBusqueda == 'venta':
                    ventasEncontradas = DetallesVenta.objects.filter(
                        #Obtiene la coincidencias
                        id_venta__icontains = terminoBusqueda
                    ).order_by('id_venta')
                    if not ventasEncontradas:
                        messages.error(request, 'No se encontraron ventas con ese ID ventas')
                totalRegistros = len(ventasEncontradas)
                if totalRegistros > 0:
                    messages.success(request, f'Se encontraron {totalRegistros} registro(s)')
            else:
                messages.error(request, 'Ingrese un término de búsqueda')
        elif 'eliminar' in request.POST:
            #Eliminar venta
            idEliminar = request.POST.get('idEliminar')
            if idEliminar:
                try:
                    #buscar la venta a eliminar
                    detalleVenta = DetallesVenta.objects.get(id_detalleVenta = idEliminar)
                    detalleVenta.delete()
                    messages.success(request, f'detalle de venta con ID: {idEliminar} eliminado correctamente')
                    #Volver a hacer la búsqueda para actualizar la lista
                    tipoBusqueda = request.POST.get('tipoBusqueda_actual', 'id')
                    terminoBusqueda = request.POST.get('terminoBusqueda_actual','')

                    if terminoBusqueda:
                        if tipoBusqueda == 'id':
                            #Para ID, no mostrar nada porque ya se eliminó
                            ventasEncontradas = []
                        elif tipoBusqueda == 'venta':
                            #En este caso hay que buscar nuevamente lo que queda
                            ventasEncontradas = DetallesVenta.objects.filter(
                                id_venta__icontains = terminoBusqueda
                            ).order_by('id_cliente')
                        totalRegistros = len(ventasEncontradas)
                except DetallesVenta.DoesNotExist:
                    messages.error(request, 'Venta no encontrada')
    context = {
        'ventasEncontradas' : ventasEncontradas,
        'tipoBusqueda' : tipoBusqueda,
        'terminoBusqueda' : terminoBusqueda,
        'totalRegistros' : totalRegistros
    }
    return render(request, 'venta/borrar_detalleVenta.html', context)