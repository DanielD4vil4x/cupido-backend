from django.http import HttpResponse

def home_view(request):
    return HttpResponse("¡Bienvenido a cUPido backend!")


