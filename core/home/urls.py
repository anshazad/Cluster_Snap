from django.urls import path
from home import views

urlpatterns = [
    path("", views.index, name="index"),
    path("landing", views.landing, name="landing"),
    path("login", views.loginUser, name="login"),
    path("logout", views.logoutUser, name="logout"),
    path("register", views.registerUser, name="register"),
    path("register2", views.registerUser2, name="register2"),
    path("process", views.process, name="process"),
]
