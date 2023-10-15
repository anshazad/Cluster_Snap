from django.urls import path
from home import views

urlpatterns = [
    path("landing", views.landing, name="landing")
]
