from django.db import models
from django.db.models import Q
from django.core.validators import MinValueValidator, MaxLengthValidator

class TopMovies(models.Model):

    title = models.CharField(max_length=255, blank=True)

class MovieManager(models.Manager):

    def get_related_movies(self, top_movies):
        return super().get_queryset().filter(top_movies=top_movies).order_by('rank')
    
    def create_movie(self, tmdb_id, title, release_date, poster_path, top_movies):
        movies = self.get_related_movies(top_movies)
        rank = len(movies) + 1
        movie, created = self.get_or_create(
            tmdb_id=tmdb_id,
            title=title,
            release_date=release_date,
            poster_path=poster_path,
            top_movies=top_movies,
            defaults={'rank': rank}
        )
        return movie

class Movie(models.Model):
    
    rank = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxLengthValidator(100)],
        default=1,
    )
    tmdb_id = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    release_date = models.DateField()
    poster_path = models.URLField(max_length=255, blank=True)
    top_movies = models.ForeignKey(
        TopMovies,
        on_delete=models.CASCADE,
        related_name="movie",
    )
    objects = MovieManager()

    class Meta:
        ordering = ['top_movies', 'rank']

    def _get_related_movies(self):
        return Movie.objects.get_related_movies(self.top_movies)

    related_movies = property(_get_related_movies)

    def reorder_rank(self, rank):
        if rank == self.rank:
            return
        if rank >= self.related_movies.count():
            rank = self.related_movies.count()
        if rank <= 0:
            rank = 1
        current_rank = self.rank
        affected_top_movies = self.related_movies.exclude(rank=current_rank) \
                                                 .filter(Q(rank__lte=max(rank, current_rank))
                                                         & Q(rank__gte=min(rank, current_rank)))
        for affected_top_movie in affected_top_movies:
            if current_rank > rank:
                affected_top_movie.rank += 1
            else:
                affected_top_movie.rank -= 1
            affected_top_movie.save()
        self.rank = rank
        self.save()
    
    def delete_rank(self):
        affected_top_movies = self.related_movies.filter(Q(rank__gt=self.rank))
        for affected_top_movie in affected_top_movies:
            affected_top_movie.rank -= 1
            affected_top_movie.save()
        self.delete()