from django.conf.urls import url
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken.views import obtain_auth_token

from pugorugh import views


urlpatterns = format_suffix_patterns([
    url(r'^api/user/login/$', obtain_auth_token, name='login-user'),
    url(r'^api/user/$', views.UserRegisterView.as_view(), name='register-user'),
    url(r'^favicon\.ico$',
        RedirectView.as_view(
            url='/static/icons/favicon.ico',
            permanent=True
        )),
    url(r'^$', TemplateView.as_view(template_name='index.html')),
    url(
        r'^api/user/preferences/$',
        views.RetrieveUpdateUserPrefView.as_view(),
        name='userpref'
    ),
    url(
        r'^api/dog/$',
        views.CreateDogView.as_view(),
        name='createdog'
    ),
    url(
        r'^api/dog/(?P<pk>\d+)/$',
        views.DestroyDogView.as_view(),
        name='destroydog'
    ),
    url(
        r'^api/dog/(?P<pk>(-)?\d+)/(?P<status>\w+)/next/$',
        views.RetrieveDogView.as_view(),
        name='dog'
    ),
    url(
        r'^api/dog/(?P<pk>(-)?\d+)/(?P<status>\w+)/$',
        views.UpdateUserDogView.as_view(),
        name='userdog'
    )
])
