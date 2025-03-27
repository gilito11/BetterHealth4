from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages

def home(request):
    """
    Renderiza la página de inicio de sesión.

    Args:
        request: El objeto HttpRequest.

    Returns:
        HttpResponse: La respuesta HTTP con el contenido de la página de inicio de sesión.
    """
    return render(request, 'home/login.html')



def login_view(request):
        """
        Maneja la vista de inicio de sesión.

        Args:
            request: El objeto HttpRequest.

        Returns:
            HttpResponse: La respuesta HTTP con el contenido de la página de inicio de sesión o redirige a la página del dashboard.
        """
        if request.method == "POST":
            username = request.POST["username"]
            password = request.POST["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("dashboard")  # Redirigir a una página después del login
            else:
                messages.error(request, "Usuario o contraseña incorrectos")
        return render(request, "home/login.html")

def index(request):
    """
    Renderiza la página principal.

    Args:
        request: El objeto HttpRequest.

    Returns:
        HttpResponse: La respuesta HTTP con el contenido de la página principal.
    """
    return render(request, 'home/index.html')


def register(request):
    """
    Renderiza la página de registro.

    Args:
        request: El objeto HttpRequest.

    Returns:
        HttpResponse: La respuesta HTTP con el contenido de la página de registro.
    """
    return render(request, 'home/register.html')  # Página de registro
