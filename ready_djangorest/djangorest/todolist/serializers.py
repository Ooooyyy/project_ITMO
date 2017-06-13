from rest_framework import serializers
from .models import Task, Tasklist, Tag, UserProfile
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
import random
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail

class TagSeializer(serializers.ModelSerializer):
    tasks = serializers.SlugRelatedField(many=True, queryset=Task.objects.all(), slug_field='name')

    class Meta:
        model = Tag
        fields = ('id', 'tag', 'tasks')
        read_only_fields = ('id', 'tasks', )

class TaskSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(many=True, queryset=Tag.objects.all(), slug_field='tag')

    class Meta:
        model = Task
        fields = ('id', 'name', 'description', 'completed', 'date_created', 
                  'date_modified', 'due_date', 'priority', 'tasklist', 'tags')
        read_only_fields = ('date_created', 'date_modified', 'tags', 'tasklist')

class TasklistSerializer(serializers.ModelSerializer):
    tasks = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
    friends = serializers.SlugRelatedField(many=True, queryset=User.objects.all(), slug_field='username')
    ro_friends = serializers.SlugRelatedField(many=True, queryset=User.objects.all(), slug_field='username')

    class Meta:
        model = Tasklist
        fields = ('id', 'name', 'tasks', 'friends', 'ro_friends', 'owner')
        read_only_fields = ('tasks', 'owner', )

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email',  )
        write_only_fields = ('password', )
        read_only_fields = ('id', )

    def create(self, validated_data):
        #создание пользователя и его запись в бд + отправка письма на мыло
        activation_key=str(random.randint(10**9, 10**10-1))
        email=validated_data['email']
        user = User.objects.create(
            username=validated_data['username'],
            email=email,
            is_active=False,
        )
        t = Token.objects.create(user=user)
        user.set_password(validated_data['password'])
        user.save()
        new_profile = UserProfile(user=user, activation_key=activation_key)
        new_profile.save()
        email_subject = 'Confirmation'
        email_body = 'Hey! Follow this link: http://127.0.0.1:8000/activate/{}'.format(activation_key)
        send_mail(email_subject, email_body, 'prikladnaya16@yandex.ru', [email], fail_silently=False)
        return user

class TokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = Token
        fields = ('user_id', 'key',)
        read_only_fields = ('user_id', 'key', )



class UserConfirmSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ('user_id', 'activation_key', )
        read_only_fields = ('user_id', )

    def create(self, validated_data):
        activation_key = validated_data['activation_key']
        user_profile = get_object_or_404(UserProfile, activation_key=activation_key)
        user = user_profile.user
        user.is_active = True
        user.save()

class KostylSerialiser(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('user_id', 'activation_key', )
        read_only_fields = ('user_id', 'activation_key', )
