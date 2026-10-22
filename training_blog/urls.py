from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, re_path

from diary.views import diary_page, entry_detail

urlpatterns = [
    path('entries/<int:pk>/', entry_detail, name='entry'),
    path('login/', LoginView.as_view(template_name='diary/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    re_path(r'^(?P<page_path>.*)$', diary_page, name='index'),
]
