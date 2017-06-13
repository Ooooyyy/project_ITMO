from django.shortcuts import render, get_object_or_404
from rest_framework.exceptions import NotFound
from rest_framework import generics
import requests
from django.contrib.auth.models import User
from .serializers import (TaskSerializer, TasklistSerializer, TagSeializer, UserRegistrationSerializer, 
                          TokenSerializer, UserConfirmSerializer, KostylSerialiser)
from django.http import HttpResponseRedirect
from .models import Task, Tasklist, Tag, LoggedInMixin, UserProfile
from rest_framework.authtoken.models import Token
from rest_framework import permissions
from django.contrib import auth


class IsNotAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        return not request.user.is_authenticated()


class TagCreateView(generics.ListCreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSeializer


class TasklistsharedView(generics.ListCreateAPIView):
    serializer_class = TasklistSerializer

    def get_queryset(self):
        queryset =  Tasklist.objects.filter(friends=self.request.user)
        return queryset


class TasklistsharedROview(generics.ListAPIView):
    serializer_class = TasklistSerializer

    def get_queryset(self):
        queryset = Tasklist.objects.filter(ro_friends=self.request.user)
        return queryset


class TasklistCreateView(generics.ListCreateAPIView):
    serializer_class = TasklistSerializer

    def get_queryset(self):
        if len(Tasklist.objects.filter(friends=self.request.user).filter(pk=self.kwargs.get('pk', None))) != 0:
            idlist = Tasklist.objects.filter(friends=self.request.user).get(pk=self.kwargs.get('pk', None)).id
            owner = Tasklist.objects.get(id=idlist)
        queryset = Tasklist.objects.filter(owner=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TasklistDetailsView(generics.RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        if len(Tasklist.objects.filter(friends=self.request.user).filter(pk=self.kwargs.get('pk', None))) != 0:
            idlist = Tasklist.objects.filter(friends=self.request.user).get(pk=self.kwargs.get('pk', None)).id
            owner = Tasklist.objects.get(id=idlist)
            return Tasklist.objects.filter(owner=owner.owner.id).filter(pk=self.kwargs.get('pk', None))
        else:
            query = Tasklist.objects.filter(owner=self.request.user).filter(pk=self.kwargs.get('pk', None))
            return query
    serializer_class = TasklistSerializer


class TaskCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        if len(Tasklist.objects.filter(friends=self.request.user).filter(pk=self.kwargs.get('pk', None))) != 0:
            idlist = Tasklist.objects.filter(friends=self.request.user).get(pk=self.kwargs.get('pk', None)).id
            owner = Tasklist.objects.get(id=idlist)
            queryset = Task.objects.filter(tasklist__owner=owner)
        else:
            queryset = Task.objects.filter(tasklist__owner=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save()

class TaskCreateInListView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated():
            queryset = Task.objects.all()
            list_id = self.kwargs.get('list_id', None)
            if list_id is not None:
                if len(Tasklist.objects.filter(friends=self.request.user).filter(pk=self.kwargs.get('list_id', None))) != 0:

                    idlist = Tasklist.objects.filter(friends=self.request.user).get(pk=self.kwargs.get('list_id', None)).id
                    owner = Tasklist.objects.get(id=idlist)
                    queryset = queryset.filter(tasklist_id=list_id).filter(tasklist__owner=owner.owner)
                else:
                    queryset = queryset.filter(tasklist_id = list_id).filter(tasklist__owner=self.request.user)
        else:
            queryset = []
        return queryset

    def perform_create(self, serializer):
        list_id = self.kwargs.get('list_id', None)
        try:
            tasklist = Tasklist.objects.get(pk=list_id)
        except Tasklist.DoesNotExist:
            raise NotFound()
        serializer.save(tasklist=tasklist)


class TaskDetailsView(LoggedInMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        queryset = Task.objects.all()
        list_id = self.kwargs.get('list_id', None)
        if list_id is not None:
            if len(Tasklist.objects.filter(friends=self.request.user).filter(pk=self.kwargs.get('pk', None))) != 0:
                idlist = Tasklist.objects.filter(friends=self.request.user).get(pk=self.kwargs.get('pk', None)).id
                owner = Tasklist.objects.get(id=idlist)
                queryset = queryset.filter(tasklist_id=list_id).filter(tasklist__owner=owner)
            else:
                queryset = queryset.filter(tasklist_id = list_id).filter(tasklist__owner=self.request.user)
        return queryset

class UserCreateView(generics.ListCreateAPIView):
    serializer_class = UserRegistrationSerializer
    def get_queryset(self):
        queryset = User.objects.all()
        return queryset

    
class Tokens(generics.ListCreateAPIView):
    serializer_class = TokenSerializer
    def get_queryset(self):
        idx = self.request.user
        queryset = Token.objects.all()   # filter(user_id=idx.id)
        return queryset

#активация пользователя, после перехода по ссылке из мыла
def activate(request, activation_key):
    idx = get_object_or_404(UserProfile, activation_key=activation_key)
    u = User.objects.get(id=idx.user_id)
    u.is_active = True
    u.save()
    return render(request, 'confirmtpl.html')