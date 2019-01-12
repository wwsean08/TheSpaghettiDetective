from django.urls import path

from . import views
from . import user_views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', user_views.SignUp.as_view(), name='signup'),
]
