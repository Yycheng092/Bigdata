
from django.urls import path
from . import views

app_name = 'line_today'

urlpatterns = [
    path('movie/', views.movie_home, name='movie_home'),
    path('api/test_movie_titles/', views.test_movie_titles,
         name='test_movie_titles'),
]
