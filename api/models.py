from django.db import models

class TopMovies(models.Model):
    pass

class Movie(models.Model):
    
    tmdb_id = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    release_date = models.DateField()
    poster_path = models.URLField(max_length=255, blank=True)
    top_movies = models.ForeignKey(
        TopMovies,
        on_delete=models.CASCADE,
        related_name="movie",
    )