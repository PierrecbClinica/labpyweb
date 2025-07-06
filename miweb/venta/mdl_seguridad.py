#Midleware
class SimpleMiddleware:
    def __init__(self, get_response):
        #Se inicia cada vez que se carga el servidor
        self.get_response = get_response
    
    def __call__(self, request):
        print('Antes de la vista')
        response = self.get_response(request)
        print('Después de la vista')

        return response
    
    