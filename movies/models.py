from django.db import models
from django.contrib.auth.models import User
class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='movie_images/')
    # The number of orders/reviews a movie has
    numorders = models.IntegerField(db_default=0)
    numreviews = models.IntegerField(db_default=0)
    
    # Displays Y/N if movie has the most orders/reviews
    mostorders =  models.CharField(max_length=10, db_default="No")
    mostreviews = models.CharField(max_length=10, db_default="No")

    def __str__(self):
        return str(self.id) + ' - ' + self.name + ' | Number of orders: ' + str(self.numorders) + ' | Number of reviews: ' + str(self.numreviews) + ' | Has most orders: ' + self.mostorders + ' | Has most reviews: ' + self.mostreviews
    
class Review(models.Model):
    id = models.AutoField(primary_key=True)
    comment = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.id) + ' - ' + self.movie.name
    
class Report(models.Model):
    id = models.AutoField(primary_key=True)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.review) + ' - ' + str(self.id)

class Rating(models.Model):
    THUMBS_UP = 'up'
    THUMBS_DOWN = 'down'
    VOTE_CHOICES = [(THUMBS_UP, 'Thumbs Up'), (THUMBS_DOWN, ['Thumbs Down'])]
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vote = models.CharField(max_length=4, choices=VOTE_CHOICES)

    # Add way to make sure that user can vote only once
    class Meta:
        unique_together = ('movie', 'user')
