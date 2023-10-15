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

def logoutUser(request):
    logout(request)
    return redirect("/login")


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

    for (i, imagePath) in enumerate(imagePaths):
        # load the input image and convert it from RGB (OpenCV ordering)
        # to dlib ordering (RGB)
        print("[INFO] processing image {}/{}".format(i + 1, len(imagePaths)))
        print(imagePath)
        image = cv2.imread(imagePath)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # detect the (x, y)-coordinates of the bounding boxes
        # corresponding to each face in the input image
        boxes = face_recognition.face_locations(rgb, model="hog")
        # compute the facial embedding for the face
        encodings = face_recognition.face_encodings(rgb, boxes)
        # build a dictionary of the image path, bounding box location,
        # and facial encodings for the current image
        d = [
            {"imagePath": imagePath, "loc": box, "encoding": enc}
            for (box, enc) in zip(boxes, encodings)
        ]
        data.extend(d)
    data = np.array(data)
    encodings = [d["encoding"] for d in data]
    # cluster the embeddings
    clt = DBSCAN(
        metric="cosine",
        n_jobs=-1,
        min_samples=1,
        eps=0.06,
        # for cosine use eps="0.06"
        # for metric="euclidean" use eps="0.55"
    )  # of parallel jobs to run (-1 will use all CPUs)
    clt.fit(encodings)
    # determine the total number of unique faces found in the dataset
    labelIDs = np.unique(clt.labels_)
    numUniqueFaces = len(np.where(labelIDs > -1)[0])

    for labelID in labelIDs:
        idxs = np.where(clt.labels_ == labelID)[0]
        owner_pic = data[idxs[0]]["imagePath"]
        image = cv2.imread(owner_pic)
        (top, right, bottom, left) = data[idxs[0]]["loc"]
        face = image[top:bottom, left:right]
        face = cv2.resize(face, (96, 96))
        face_img_path = f"{user.get_username()}_owner{labelID}.jpg"
        cv2.imwrite(f"static/images/{face_img_path}", face)
        person = Person.objects.create(user=user, thumbnail=face_img_path)
        person.save()

        for i in idxs:
            src_direc = data[i]["imagePath"]
            link = post_type.search(src_direc)
            personGallery = PersonGallery.objects.create(
                person=person, image=str(link.group(1))
            )
            personGallery.save()
    user = request.user
    persons = Person.objects.filter(user=user)

    score_list = []
    numUniqueFaces = persons.count()
    path = os.getcwd() + str("/static/images/")

    for i in range(numUniqueFaces):
        intmd_lst = []
        for j in range(i + 1, numUniqueFaces):
            image1 = cv2.imread(path + str(persons[i].thumbnail))
            image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
            image2 = cv2.imread(path + str(persons[j].thumbnail))
            image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
            score = dist.cosine(image1.reshape(-1), image2.reshape(-1))
            intmd_lst.append([i, j, score])
            print(i, j, score)
        score_list.append(intmd_lst)

    result = []
    unsorted_person = [i for i in range(1, numUniqueFaces)]
    sorted_person = []
    start = 0
    next = score_list[0][0][1]
    sorted_person.append(start)
    i = 0
    for _ in range(numUniqueFaces - 1):
        print(score_list[start])
        min = 1
        for ele in score_list[start]:
            if ele[2] < min:
                min = ele[2]
                next = ele[1]
        print(min, next)

        if start == next:
            break
        else:
            unsorted_person.remove(next)
            sorted_person.append(next)
            start = next
    final = sorted_person + unsorted_person
    for ele in final:
        result.append(persons[ele])

    context = {"persons": result, "faces": numUniqueFaces}
    return render(request, "process.html", context)


