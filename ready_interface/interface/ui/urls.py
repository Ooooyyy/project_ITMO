from django.conf.urls import url, include
from . import views

urlpatterns = {
    url(r'^ui/$', views.tasklist_create, name="list-create"),
    url(r'^ui/(?P<pk>[0-9]+)/$', views.tasklist_details, name="list-details"),
    url(r'^ui/(?P<list_id>[0-9]+)/tasks/$', views.task_create, name="task-create"),
    url(r'^ui/(?P<list_id>[0-9]+)/tasks/(?P<pk>[0-9]+/$)', views.task_details, name="task-details"),
    url(r'^ui/(?P<pk>[0-9]+)/$', views.tasklist_details, name="list-detail"),
    url(r'^ui/tags/', views.tag_create, name="tag-create"),
    url(r'^ui/registration/', views.user_registration, name="user-register"),
    url(r'^ui/login/', views.user_login, name="user-login"),
    url(r'^ui/confirm/', views.user_confirm, name="user-confirmation"),
    url(r'^ui/activate/(?P<activation_key>[0-9]+)/', views.user_activate, name="user-activation"),
    url(r'^ui/logout/', views.user_logout, name="user-logout"),
}