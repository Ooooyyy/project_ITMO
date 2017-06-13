from django.shortcuts import render
import requests
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.encoding import force_text
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework.exceptions import NotFound
from rest_framework import generics
from django.contrib.auth.models import User
from django.core.serializers import serialize
from django.http import HttpResponseRedirect, Http404
from .forms import TasklistCreateForm, TaskCreateForm, TasklistDetailsForm, TaskDetailsForm, TagCreateForm, \
    RegisterForm, LoginForm, ConfirmationForm
from django.contrib.sessions.models import Session
from django.contrib import auth
from django.core.mail import send_mail
from django import forms

# все creatЫ работают по одному принципу: 1) проверяется логин пользователя
# 2) рендарим форму по гет запросу => заполняем данные в форму
# 3) проверяем валидность формы => делаем пост запрос к 9 лабе с передачей данных из формы


# Как работает изменение тасков или такслистов:
# у них есть 2 метода: put, delete
# если delete, то обращаемся к 9 лабе с запросом на удаление
# если put, то собираем данные с формы, проверяем валидность, делаем пост запрос к странице с деталями к 9 лабе


# как работает расшаривание и рид онли расшаривании:
# в бд есть 2 таблицы, где два столбца - id таблицы и id пользователя, которые может редактировать/смотреть тасклист в зависимости от таблицы
# мы смотрим для текущего пользователя в данных таблицах тасклисты, которые ему доступны, и возвращаем их
# а CRUD тасклиста для не владельца работает так: мы смотрим, есть ли текущий пользователь в разрешенной таблице
# затем если есть, смотрим владельца тасклиста, и при put запросе отправляем id владельца, а не текущего пользователя

#берет все задания данного пользователя
def get_tasks(request):
    response = requests.get('http://127.0.0.1:8000/todolists/tasks/',
                            headers=dict(Authorization=request.session['Authorization'])).json()
    tasks = [(i, response[i]['name']) for i in range(len(response))]
    return tasks


def get_tags():
    response = requests.get('http://127.0.0.1:8000/todolists/tags').json()
    return response


def create_tag(request, tag):
    requests.Session().post('http://127.0.0.1:8000/todolists/tags/',
                            data=dict(tag=tag),
                            headers=dict(Authorization=request.session['Authorization'])
                            )


# возвращает пользователей, кроме того, у кого сейчас сессия и владельца тасклиста/таска
def get_users(request, pk=False):
    response = requests.get('http://127.0.0.1:8000/todolists/registration/',
                            headers=dict(Authorization=request.session['Authorization'])).json()
    users = []
    if pk:
        owner_response = requests.get('http://127.0.0.1:8000/todolists/{}/'.format(pk),
                                headers=dict(Authorization=request.session['Authorization'])).json()
    for i in range(len(response)):
        if response[i]['username'] == request.session['Login']:
            pass
        elif pk and response[i]['id'] == owner_response['owner']:
            pass
        else:
            users.append([str(i), response[i]['username']])
    return users


def tasklist_create(request):
    try:
        a = request.session['Authorization']
    except:
        return HttpResponseRedirect('http://localhost:8080/ui/login/')
    if request.method == 'POST':
        form = TasklistCreateForm(request.POST)
        if form.is_valid():
            requests.Session().post('http://127.0.0.1:8000/todolists/',
                                    data=dict(name=form.cleaned_data['name'],
                                              friends=form.cleaned_data['friends'],
                                              ro_friends=form.cleaned_data['friends_read_only']),
                                    headers=dict(Authorization=a))
            return HttpResponseRedirect('http://localhost:8080/ui/')
        else:
            print(form.cleaned_data['friends'])
    else:
        form = TasklistCreateForm()
        form.fields['friends'].choices = get_users(request)
        form.fields['friends_read_only'].choices = get_users(request)
    resp = requests.get('http://127.0.0.1:8000/todolists/',
                        headers=dict(Authorization=a)).json()
    shared = requests.get('http://127.0.0.1:8000/todolists/shared',
                          headers=dict(Authorization=a)).json()
    ro_shared = requests.get('http://127.0.0.1:8000/todolists/sharedro',
                             headers=dict(Authorization=a)).json()
    return render(request, 'tasklistcreatetpl.html',
                  {'form': form, 'resp': resp, 'shared': shared, 'ro_shared': ro_shared})


def task_create(request, list_id):
    try:
        a = request.session['Authorization']
    except:
        return HttpResponseRedirect('http://localhost:8080/ui/login/')
    all_tags = get_tags()
    tag_dict = {}
    for tag in all_tags:
        tag_dict[tag['tag']] = tag['id']
    if request.method == 'POST':
        form = TaskCreateForm(request.POST)
        if form.is_valid():
            tags = form.cleaned_data['tags']
            tags = tags.split()
            wereNew = False
            for tag in tags:
                if tag not in tag_dict.keys():
                    wereNew = True
                    create_tag(request, tag)
            requests.Session().post('http://127.0.0.1:8000/todolists/' + str(list_id) + '/tasks/',
                                    data=dict(name=form.cleaned_data['name'],
                                              description=form.cleaned_data['description'],
                                              completed=form.cleaned_data['completed'],
                                              due_date=form.cleaned_data['due_date'],
                                              tags=form.cleaned_data['tags'],
                                              priority=form.cleaned_data['priority']),
                                    headers=dict(Authorization=a))
    else:
        form = TaskCreateForm()
    resp = requests.get('http://127.0.0.1:8000/todolists/' + str(list_id) + '/tasks/',
                        headers=dict(Authorization=a)).json()
    return render(request, 'taskcreatetpl.html', {'form': form, 'action': request.path, 'resp': resp, 'list': list_id})


def task_details(request, list_id, pk):
    try:
        a = request.session['Authorization']
    except:
        return HttpResponseRedirect('http://localhost:8080/ui/login/')
    all_tags = get_tags()
    tag_dict = {}
    for tag in all_tags:
        tag_dict[tag['tag']] = tag['id']
    if request.method == 'POST':
        form = TaskDetailsForm(request.POST)
        if form.is_valid():
            method = form.cleaned_data['method']
            if method == 'put':
                if form.is_valid():
                    tags = form.cleaned_data['tags']
                    tags = tags.split()
                    wereNew = False
                    for tag in tags:
                        if tag not in tag_dict.keys():
                            wereNew = True
                    create_tag(request, tags)
                    requests.Session().put('http://127.0.0.1:8000/todolists/' + str(list_id) + '/tasks/' + str(pk),
                                           data=dict(name=form.cleaned_data['name'],
                                                     description=form.cleaned_data['description'],
                                                     completed=form.cleaned_data['completed'],
                                                     # date_created = dd.today(),
                                                     due_date=form.cleaned_data['due_date'],
                                                     # date_modified = dd.today(),
                                                     tags=form.cleaned_data['tags'],
                                                     priority=form.cleaned_data['priority']),
                                           headers=dict(Authorization=a))
            else:
                requests.Session().delete('http://127.0.0.1:8000/todolists/' + str(list_id) + '/tasks' + str(pk) + '/',
                                          headers=dict(Authorization=a))
                return HttpResponseRedirect('http://localhost:8080/ui/' + str(list_id) + '/tasks/')
    else:
        form = TaskDetailsForm()
    resp = requests.get('http://127.0.0.1:8000/todolists/' + str(list_id) + '/tasks/',
                        headers=dict(Authorization=a)).json()
    task = ''
    for i in resp:
        if str(i['id']) + '/' == str(pk):
            task = i
    if task == '':
        raise Http404
    for i in ['name', 'description', 'completed', 'due_date', 'tags', 'priority']:
        form.fields[i].initial = task[i]
    form.fields['tags'].initial = ''
    for i in task['tags']:
        form.fields['tags'].initial += i + ' '
    return render(request, 'taskdetailstpl.html', {'form': form, 'action': request.path})


def tasklist_details(request, pk):
    try:
        a = request.session['Authorization']
    except:
        return HttpResponseRedirect('http://localhost:8080/ui/login/')
    if request.method == 'POST':
        form = TasklistDetailsForm(request.POST)
        if form.is_valid():
            method = form.cleaned_data['method']
            if method == 'put':
                if form.is_valid():
                    requests.Session().put('http://127.0.0.1:8000/todolists/' + str(pk) + '/',
                                           data=dict(name=form.cleaned_data['name'],
                                                     friends=form.cleaned_data['friends'],
                                                     ro_friends=form.cleaned_data['friends_read_only']),
                                           headers=dict(Authorization=a))
            else:
                requests.Session().delete('http://127.0.0.1:8000/todolists/' + str(pk) + '/',
                                          headers=dict(Authorization=a))
                return HttpResponseRedirect('http://localhost:8080/ui/')
    else:
        form = TasklistDetailsForm()
        form.fields['friends'].choices = get_users(request, pk)
        form.fields['friends_read_only'].choices = get_users(request, pk)
    resp = requests.get('http://127.0.0.1:8000/todolists/{}/'.format(pk),
                        headers=dict(Authorization=a)).json()
    return render(request, 'tasklistdetailstpl.html', {'form': form, 'list': resp, 'pk': pk})


def tag_create(request):
    try:
        a = request.session['Authorization']
    except:
        return HttpResponseRedirect('http://localhost:8080/ui/login/')
    if request.method == 'POST':
        form = TagCreateForm(request.POST)
        form.fields['tasks'].choices = get_tasks(request)
        if form.is_valid():
            requests.Session().post('http://127.0.0.1:8000/todolists/tags',
                                    data=dict(name=form.cleaned_data['name'],
                                              tasks=form.cleaned_data['tasks']),
                                    headers=dict(Authorization=a))
    else:
        form = TagCreateForm()
        form.fields['tasks'].choices = get_tasks(request)
    resp = requests.get('http://127.0.0.1:8000/todolists/tags',
                        headers=dict(Authorization=a)).json()
    return render(request, 'tagcreatetpl.html', {'form': form, 'action': request.path, 'resp': resp})


def user_confirm(request):
    return render(request, 'confirmtpl.html')

#активация пользователя, переход к 9 лабе
def user_activate(request, activation_key):
    resp = requests.get('http://127.0.0.1:8000/activate/{}'.format(activation_key))
    return HttpResponseRedirect('http://localhost:8080/ui/login')


#проверка на авторизацию, если да, то главная страница с таксками, если нет, то проверяем гет и пост методы, если пост, то отправляем регистрацию к 9 лабе
#регистрация реализована в 9 лабе
def user_registration(request):
    try:
        a = request.session['Authorization']
        return HttpResponseRedirect('http://localhost:8080/ui/')
    except:
        if request.method == 'POST':
            form = RegisterForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                email = form.cleaned_data['email']
                data = dict(username=username, password=password, email=email)
                response = requests.post('http://127.0.0.1:8000/todolists/registration', data)
                return HttpResponseRedirect('http://localhost:8080/ui/confirm/')
        else:
            form = RegisterForm()
        return render(request, 'regtpl.html', {'form': form})

#в сессию добавляем токен
def user_login(request):
    text = ''
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            data = dict(username=username, password=password)
            response = requests.post('http://127.0.0.1:8000/api-token-auth/', data)
            if response.status_code == 200:
                request.session['Authorization'] = 'Token ' + str(response.json()['token'])
                request.session['Login'] = username
                requests.Session().headers = dict(Authorization=request.session['Authorization'])
                return HttpResponseRedirect('http://localhost:8080/ui/')
            else:
                text = 'Sorry, wrong username or password'
    else:
        try:
            a = request.session['Authorization']
            return HttpResponseRedirect('http://localhost:8080/ui/')
        except:
            pass
        form = LoginForm()
    return render(request, 'logintpl.html', {'form': form, 'text': text})

#удаляем из сессии токен пользователя
def user_logout(request):
    request.session.pop('Authorization')
    return HttpResponseRedirect('http://localhost:8080/ui/login/')
