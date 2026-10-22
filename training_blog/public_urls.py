from django.urls import re_path
from diary.views import public_page

urlpatterns = [re_path(r'^(?P<page_path>.*)$', public_page)]
