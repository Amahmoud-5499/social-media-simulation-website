from django.urls import path
from . import views 
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.index, name = "index"),
    path('settings', views.settings, name = "settings"),
    path('upload', views.upload, name = "upload"),
    path('follow', views.follow, name = "follow"),
    path('search', views.search, name = "search"),
    path('profile/<str:pk>', views.profile, name = "profile"),
    path('post_like', views.post_like, name = "post_like"),
    path('signup', views.signup, name = "signup"),
    path('signin', views.signin, name = "signin"),
    path('logout', LogoutView.as_view(next_page = '/signin'), name = "logout"),
]
