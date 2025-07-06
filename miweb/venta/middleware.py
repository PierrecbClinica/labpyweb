from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import get_user

class AuthenticationMiddleware:
    '''
    verifica que el usurio este autenticado antes de acceder a 
    cualquiere url del sistema
    '''

    def __init__(self, get_response):
        self.get_response = get_response

        #URLs que no requieren verificación de autentificación 
        self.public_urls = [
            '/',
            '/admin/login/',
            '/admin/login',
            '/admin/',
            '/admin',
            '/logout/',
            '/logout',
        ]
    
    def __call__(self, request):
        #Verificar si el url actual esta en la lista public_urls
        if self.is_public_url(request.path):
            response = self.get_response(request)
            return response
        #Si el usuario no esta autenticado, redirigir al login
        if not request.user.is_authenticated:
            return redirect('login')
        
        response = self.get_response(request)
        return response
    
    def is_public_url(self, path):
        '''
        si la url es pública, no requiere autenticación
        '''
        if path in self.public_urls:
            return True
        
        return False
    