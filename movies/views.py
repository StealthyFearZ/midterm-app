from django.shortcuts import render, redirect, get_object_or_404

from cart.models import Item
from .models import Movie, Review, Report
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from django.http import JsonResponse

def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()
    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html',
                  {'template_data': template_data})

def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie)
    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    user_reported = False
    for r in reviews:
        if Report.objects.filter(review=r).exists():
            user_reported = True
    template_data['user_reported'] = user_reported
    return render(request, 'movies/show.html',
                  {'template_data': template_data})

@login_required
def map(request):
    movies = Movie.objects.all()
    items = Item.objects.all()
    template_data = {}
    template_data['title'] = 'Local Popularity Map'
    template_data['movies'] = movies
    template_data['items'] = items
    return render(request, 'movies/map.html',
                  {"movies_json": serialize("json", movies),
                   "items_json": serialize("json", items),
                   'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        # Add 1  to numReviews of for each purchase
        Movie.objects.all().filter(id=movie.id).update(numreviews=movie.numreviews + 1)
        toprev = Movie.objects.all().order_by('numreviews').last()
        isrev = (toprev.numreviews == movie.numreviews + 1)
        Movie.objects.all().filter(id=movie.id).update(mostreviews= "Yes" if isrev else "No")
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)
    
@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html',
            {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)
    
@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    # Add 1  to numReviews of for each purchase
    movie = Movie.objects.get(id=id)
    Movie.objects.all().filter(id=id).update(numreviews=movie.numreviews - 1)
    toprev = Movie.objects.all().order_by('numreviews').last()
    isrev = (toprev.numreviews == movie.numreviews - 1)
    Movie.objects.all().filter(id=movie.id).update(mostreviews= "Yes" if isrev else "No")
    review.delete()
    return redirect('movies.show', id=id)

@login_required
def report_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    report = Report()
    report.review = review
    report.user = request.user
    report.save()
    return redirect('movies.show', id=id)