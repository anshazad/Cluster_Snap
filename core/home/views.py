from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import logout, login
from django.http import HttpResponse
from home.models import Photo, Person, PersonGallery
import re


# ReGEx required for getting photo name
post_type = re.compile(r"static/images/(.*)")


# Create your views here.
def landing(request):
    return render(request, "landing.html")

def loginUser(request):
    if request.method == "POST":
        roomcode = request.POST.get("roomCode")
        password = request.POST.get("inputPassword")
        user = authenticate(username=roomcode, password=password)
        if user is not None:
            login(request, user)
            return redirect("/")
        else:
            return render(request, "login.html")
    return render(request, "login.html")

def index(request):
    user = request.user
    if user.is_anonymous:
        return redirect("/landing")

    elif request.method == "POST":
        images = request.FILES.getlist("images")
        for image in images:
            print(image)
            photo = Photo.objects.create(user=user, image=image)
            photo.save()

    photos = Photo.objects.filter(user=user)
    count = photos.count()

    context = {"photos": photos, "count": count}
    return render(request, "index.html", context)

def loginUser(request):
    pass

def logoutUser(request):
    pass

def registerUser(request):
    pass

def registerUser2(request):
    pass

def process(request):
    user = request.user
    if user.is_anonymous:
        return redirect("/login")
    Person.objects.filter(user=user).delete()
    photos = Photo.objects.filter(user=user)
    if photos.count() == 0:
        context = {
            "error_message": "No photos to process.\n Upload some photos and then Try again"
        }
        return render(request, "404.html", context)
    imagePaths = [("static/images/" + str(photo.image)) for photo in photos]
    data = []



