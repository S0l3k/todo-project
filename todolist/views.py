from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import ToDoForm
from .models import ToDo
from django.utils import timezone
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, 'todolist/home.html')

def signupuser(request):
    if request.method == 'GET':
        return render(request, 'todolist/signupuser.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttodos')
            except IntegrityError:
                return render(request, 'todolist/signupuser.html',
                              {'form': UserCreationForm(),
                               'error': 'That username has already been taken. Please, choose another username'})
        else:
            return render(request, 'todolist/signupuser.html',
                          {'form': UserCreationForm(),
                           'error': 'Password did not match'})

def loginuser(request):
    if request.method == 'GET':
        return render(request, 'todolist/loginuser.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'todolist/loginuser.html',
                          {'form': AuthenticationForm(),
                           'error':'Username and passeword did not match'})
        else:
            login(request, user)
            return redirect('currenttodos')

def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')

@login_required
def currenttodos(request):
    todos = ToDo.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'todolist/currenttodos.html', {'todos':todos})

@login_required
def completedtodos(request):
    todos = ToDo.objects.filter(user=request.user, datecompleted__isnull=False)\
        .order_by('-datecompleted')
    return render(request, 'todolist/completedtodos.html', {'todos':todos})

@login_required
def createtodo(request):
    if request.method == 'GET':
        return render(request, 'todolist/createtodo.html',
                      {'form': ToDoForm()})
    else:
        try:
            form = ToDoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todolist/createtodo.html',
                          {'form': ToDoForm(), 'error':'Bad date passed in!'})

@login_required
def viewtodo(request, todo_pk):
    todo = get_object_or_404(ToDo, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        form = ToDoForm(instance=todo)
        return render(request, 'todolist/viewtodo.html',
                      {'todo': todo, 'form': form})
    else:
        try:
            form = ToDoForm(request.POST, instance=todo)
            form.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todolist/viewtodo.html',
                          {'todo':todo,
                           'form': form,
                           'error': 'Bad info!'})

@login_required
def completetodo(request, todo_pk):
    todo = get_object_or_404(ToDo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('currenttodos')

@login_required
def deletetodo(request, todo_pk):
    todo = get_object_or_404(ToDo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('currenttodos')