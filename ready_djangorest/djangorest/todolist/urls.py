from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from .views import (TasklistCreateView, TasklistDetailsView, TaskCreateView, TaskDetailsView, TasklistsharedView, TagCreateView, 
    TaskCreateInListView, UserCreateView, Tokens, activate, TasklistsharedROview, )
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = {
    url(r'^todolists/$', TasklistCreateView.as_view(), name="lists"),
    url(r'^todolists/(?P<pk>[0-9]+)/$', TasklistDetailsView.as_view(), name="list-detail"),
    # url(r'^todolists/(?P<pk>[0-9]+)/owner/$', Tasklistowner.as_view(), name="task-owner"),
    url(r'^todolists/shared/$', TasklistsharedView.as_view(), name="list-shared"),
    url(r'^todolists/sharedro/$', TasklistsharedROview.as_view(), name="list-shared"),
    url(r'^todolists/(?P<list_id>[0-9]+)/tasks/$', TaskCreateInListView.as_view(), name="task-create"),
    url(r'^todolists/tasks/$', TaskCreateView.as_view(), name="task-create"),
    url(r'^todolists/(?P<list_id>[0-9]+)/tasks/(?P<pk>[0-9]+/$)', TaskDetailsView.as_view(), name="task-detail"),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'todolists/registration', UserCreateView.as_view(), name="user-registration"),
    url(r'todolists/tags/', TagCreateView.as_view(), name="tag-create"),
    url(r'^api-token-auth/', obtain_auth_token),
    url(r'^tokens/', Tokens.as_view(), name="tokens"),
    #url(r'^confirm', Keys.as_view(), name="confirmation"),
    url(r'^activate/(?P<activation_key>[0-9]+)/', activate, name="activation"),
}

urlpatterns = format_suffix_patterns(urlpatterns)
