from django import forms
import requests
from django.forms import widgets

class RegisterForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
    email = forms.EmailField()

class ConfirmationForm(forms.Form):
    activation_key = forms.CharField()

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())


class TasklistCreateForm(forms.Form):
    name = forms.CharField(max_length=200)
    friends = forms.MultipleChoiceField(widget=widgets.SelectMultiple, required=False)
    friends_read_only = forms.MultipleChoiceField(required=False)


def get_tags():
    response = requests.get('http://127.0.0.1:8000/todolists/tags').json()
    tags = ''
    for i in response:
        tags += i['tag'] + ' '
    return tags


class TaskCreateForm(forms.Form):
    name = forms.CharField(max_length=200)
    description = forms.CharField(max_length=1000, required=False)
    completed = forms.BooleanField(required=False)
    due_date = forms.CharField(required=False)
    tags = forms.CharField(required=False)

    PRIORITY = (
        ('h', 'High'),
        ('m', 'Medium'),
        ('l', 'Low'),
        ('n', 'None')
    )

    priority = forms.ChoiceField(choices=PRIORITY, initial='n')


class TaskDetailsForm(TaskCreateForm):
    method = forms.ChoiceField(choices=((1, 'put'), (2, 'delete')))


class TasklistDetailsForm(TasklistCreateForm):
    method = forms.ChoiceField(choices=((1, 'put'), (2, 'delete')))


class TagCreateForm(forms.Form):
    name = forms.CharField(max_length=200)
    tasks = forms.MultipleChoiceField(required=False)
