from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import connection

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Verificar se está na tabela ADMINISTRADORES
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT ID_ADMINISTRADOR
                    FROM ADMINISTRADORES
                    WHERE EMAIL_ADMINISTRADOR = %s
                """, [user.email])
                admin = cursor.fetchone()
            if admin:
                login(request, user)
                return redirect("home")
            else:
                messages.error(request, "Não é um administrador autorizado.")
        else:
            messages.error(request, "Credenciais inválidas.")
    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def home (request):
    return render(request, 'home.html')