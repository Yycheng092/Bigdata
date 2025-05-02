from django.http import JsonResponse
from django.shortcuts import render
from .crawler_with_cache import (
    crawl_movie_titles,
    crawl_incinemas_newrelease,
    crawl_third_column_data
)


def movie_home(request):
    third_data = crawl_third_column_data()
    movies = crawl_movie_titles()
    new_movies = crawl_incinemas_newrelease()
    context = {
        "third_data": third_data,
        "movies": movies,
        "new_movies": new_movies,
        "cinema_newreleases": new_movies,
    }
    return render(request, "line_today/movie_home.html", context)


def test_movie_titles(request):
    titles = crawl_movie_titles()
    return JsonResponse({"titles": titles})
