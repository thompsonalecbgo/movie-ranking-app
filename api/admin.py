from django.contrib import admin

from .models import TopMovies, Movie


admin.site.register(TopMovies)
admin.site.register(Movie)