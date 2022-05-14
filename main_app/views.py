from distutils.log import Log
import http
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import LoginForm
from .models import Cat, CatToy

# Create your views here.
# these functions are called by our main_app's urls.py file
# those urls are registered in our project, catcollector's urls.py
# we're going to define our view functions
# first one is just a basic function for an index request
def index(request):
    # return HttpResponse('<h1>Hello World! /ᐠ｡‸｡ᐟ\ﾉ</h1>')
    # render index.html
    return render(request, 'index.html')

# here is our about view
def about(request):
    # return HttpResponse('<h1>I am Timm, the developer</h1>')
    # we're actually going to render our html template
    return render(request, 'about.html')

# here's where our Cat class will live, and that's the data we'll pass to our templates

# used this before we had a database, to test out our templates
# class Cat:
#     def __init__(self, name, breed, description, age):
#         self.name = name
#         self.breed = breed
#         self.description = description
#         self.age = age

# this is our list of cats(more specifically, cat dictionaries)
# cats = [
#     Cat('Lolo', 'tabby', 'foul little demon', 3),
#     Cat('Sachi', 'tortoise shell', 'diluted tortoise shell', 0),
#     Cat('Raven', 'black tripod', '3 legged cat', 4)
# ]

def cats_index(request):
    cats = Cat.objects.all()
    return render(request, 'cats/index.html', {'cats': cats})

# define cats show function
# we will get an id from the route parameter, defined in urls
def cats_show(request, cat_id):
    cat = Cat.objects.get(id=cat_id)
    # get all of the cat toys that is not associated with
    available_toys = CatToy.objects.exclude(id__in = cat.cattoys.all().values_list('id'))
    # print to test to make sure the query is 
    # print('all the toys this cat aint got')
    # print(available_toys)
    return render(request, 'cats/show.html', {'cat': cat, 'available_toys': available_toys})

class CatCreate(CreateView):
    # use the model Cat
    model = Cat
    # utilize all fields from the model cat
    # fields = '__all__'
    fields = ['name', 'breed', 'description', 'age']
    # redirect upon successful creation
    success_url = '/cats'

    def form_valid(self, form):
        # creating an object from the form
        self.object = form.save(commit=False)
        # adding a user to that object
        self.object.user = self.request.user
        # saving the object in the db
        self.object.save()
        # redirecting to the main index page
        return HttpResponseRedirect('/cats')

class CatUpdate(UpdateView):
    # use the model Cat
    model = Cat
    # we need to define the fields, but only use the right ones
    # that means, no changing or attempting to change the id
    fields = ['name', 'breed', 'description', 'age', 'cattoys']

    # now we use a function to determine if our form data is valid
    def form_valid(self, form):
        # commit=False is useful when we're getting data from a form
        # but we need to populate with some non-null data
        # saving with commit=False gets us a model object, then we can add our extra data and save
        self.object = form.save(commit=False)
        self.object.save()
        # pk is the primary key, aka the id of the object
        return HttpResponseRedirect('/cats/' + str(self.object.pk))

@method_decorator(login_required, name='dispatch')
class CatDelete(DeleteView):
    model = Cat
    success_url = '/cats'


# user profile view
@login_required
def profile(request, username):
    user = User.objects.get(username=username)
    cats = Cat.objects.filter(user=user)
    return render(request, 'profile.html', {'username': username, 'cats': cats})


# CatToy views
class CatToyCreate(CreateView):
    model = CatToy
    fields = '__all__'

class CatToyUpdate(UpdateView):
    model = CatToy
    fields = ['name', 'color']

class CatToyDelete(DeleteView):
    model = CatToy
    success_url = '/cattoys'

# here are our show and index catToy views
def cattoys_index(request):
    cattoys = CatToy.objects.all()
    return render(request, 'cattoys/index.html', { 'cattoys': cattoys })

# show(otherwise known as detail view)
def cattoys_detail(request, cattoy_id):
    cattoy = CatToy.objects.get(id=cattoy_id)
    return render(request, 'cattoys/detail.html', { 'cattoy': cattoy })

# view to give toy to cat
def give_toy(request, cat_id, toy_id):
    # note all we need for your association of cat and a toy are their ids
    # we don't need the whole object
    Cat.objects.get(id=cat_id).cattoys.add(toy_id)
    return HttpResponseRedirect('/cats/' + str(cat_id))

# view to take toy from cat
def take_toy(request, cat_id, toy_id):
    # note all we need for your association of cat and a toy are their ids
    # we don't need the whole object
    Cat.objects.get(id=cat_id).cattoys.remove(toy_id)
    return HttpResponseRedirect('/cats/' + str(cat_id))

# login view 
def login_view(request):
    # we can use the same view for multiple HTTP requests
    # this can be done with a simple if statement
    if request.method == 'POST':
        # handle post request
        # we want to authenticate the user with the username and pw
        form = LoginForm(request.POST)
        if form.is_valid():
            # get the username and pw and save them to variables
            u = form.cleaned_data['username']
            p = form.cleaned_data['password']
            # here we use django's built in authenticate method
            user = authenticate(username = u, password = p)  
            # if you found a user with matching credentials     
            if user is not None:
                # if the user has not been disabled by admin
                if user.is_active:
                    # use django's built in login function 
                    login(request, user)
                    return HttpResponseRedirect('/user/' + str(user.username))
                else:
                    print('the account has been disabled')
            else:
             print('the username or password is incorrect')
    else:
        # the request is a get, we render the login page
        form = LoginForm()
        return render(request, 'login.html', {'form': form})

# logout view
def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/cats/')

# sign up view
def signup_view(request):
    # if the req is a post, then sign them up
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return HttpResponseRedirect('/user/' + str(user.username))
    # if the req is a get, then show the form
    else:
        form = UserCreationForm()
        return render(request, 'signup.html', {'form': form})



