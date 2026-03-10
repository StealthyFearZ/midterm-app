from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, Report, Rating
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from topcommenters.models import Top_Commenter
from django.contrib.auth.models import User

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

    ratings = movie.ratings.aggregate( #type: ignore
        total=Count('id'),
        thumbs_up = Count('id', filter=Q(vote='up')),
        thumbs_down = Count('id', filter=Q(vote='down'))
    )
    if ratings['total'] > 0:
        approval = round((ratings['thumbs_up'] / ratings['total']) * 100)
    else:
        approval = None
    template_data['ratings'] = ratings
    template_data['approval'] = approval
    user_rating = None
    # Rating has a direct movie
    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(movie=movie, user=request.user).first()
        print(f"user_rating: {user_rating}, vote: {user_rating.vote if user_rating else None}")
        # Report links to Review, not Movie — filter through review
        Report.objects.filter(review__movie=movie, user=request.user).exists()
    template_data['user_reported'] = user_reported
    template_data['user_rating'] = user_rating
    for r in reviews:
        if Report.objects.filter(review=r).exists():
            user_reported = True
    template_data['user_reported'] = user_reported
    return render(request, 'movies/show.html',
                  {'template_data': template_data})

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
        isrev = (toprev.numreviews == movie.numreviews + 1) # type: ignore
        Movie.objects.all().filter(id=movie.id).update(mostreviews= "Yes" if isrev else "No")
        review.save()
        recalculate_commenters()
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
    isrev = (toprev.numreviews == movie.numreviews - 1) # type: ignore
    Movie.objects.all().filter(id=movie.id).update(mostreviews= "Yes" if isrev else "No")
    review.delete()
    recalculate_commenters()
    return redirect('movies.show', id=id)

@login_required
def report_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    report = Report()
    report.review = review
    report.user = request.user
    report.save()
    return redirect('movies.show', id=id)


@login_required
def rate_movie(request, id):
    if request.method == 'POST':
        movie = get_object_or_404(Movie, id=id)
        vote = request.POST.get('vote')
        if vote in ['up', 'down']:
            rating, created = Rating.objects.update_or_create(
                movie=movie,
                user=request.user,
                defaults={'vote': vote} # type: ignore
            )
            print(f"Rating Saved {rating.vote}, created: {created}")
    return redirect('movies.show', id=id)

def recalculate_commenters(): # reuse with create and delete review
    for userx in User.objects.all():
        commenter, booleanCheck = Top_Commenter.objects.get_or_create(user=userx)

        total_reviews = Review.objects.filter(user=userx).count()
        Top_Commenter.objects.all().filter(user=userx).update(numComments=total_reviews)

    Top_Commenter.objects.all().update(mostComments=False)
    topuser = Top_Commenter.objects.all().order_by('numComments').last() # ascending, so get last val
    if topuser:
        Top_Commenter.objects.all().filter(id=topuser.id).update(mostComments=True)