from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from movies.models import Movie
from moviesstore import settings
from .utils import calculate_cart_total
from .models import Order, Item
from django.contrib.auth.models import User
from topbuyers.models import Top_Buyer
from django.contrib.auth.decorators import login_required
from django.contrib.gis.geoip2 import GeoIP2

def index(request):
    cart_total = 0
    movies_in_cart = []
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())
    if (movie_ids != []):
        movies_in_cart = Movie.objects.filter(id__in=movie_ids)
        cart_total = calculate_cart_total(cart, movies_in_cart)
    template_data = {}
    template_data['title'] = 'Cart'
    template_data['movies_in_cart'] = movies_in_cart
    template_data['cart_total'] = cart_total
    return render(request, 'cart/index.html',
        {'template_data': template_data})

def add(request, id):
    get_object_or_404(Movie, id=id)
    cart = request.session.get('cart', {})
    cart[id] = request.POST['quantity']
    request.session['cart'] = cart
    return redirect('cart.index')

def clear(request):
    request.session['cart'] = {}
    return redirect('cart.index')

@login_required
def purchase(request):
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())
    if (movie_ids == []):
        return redirect('cart.index')
    movies_in_cart = Movie.objects.filter(id__in=movie_ids)
    cart_total = calculate_cart_total(cart, movies_in_cart)
    order = Order()
    order.user = request.user
    order.total = cart_total
    order.save()

    # get user IP
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')  # request client IP
    # if request returned a valid list of IPs
    if x_forwarded_for:
        userIP = x_forwarded_for.split(',')[0]
    # sometimes, above request will come back empty (ex. when server is locally hosted)
    else:
        # thus use the following - returns localhost
        userIP = request.META.get('REMOTE_ADDR')
    
    # get continent code from IP
    # database file for geo data is GeoLite2-City.mmdb, in base directory (update path if moved)
    try:
        userRegion = GeoIP2(path=settings.BASE_DIR).city(order.ip)['continent_code']
    except:     # when developing locally, localhost will not be within the geo database
        userRegion = "NA" # North America

    for movie in movies_in_cart:
        item = Item()
        item.movie = movie
        item.price = movie.price
        item.order = order
        item.quantity = cart[str(movie.id)]
        # assign previously resolved ip and region info to items in the order
        item.ip = userIP
        item.region = userRegion
        # Add quantity of purchase to numOrders of movie
        Movie.objects.all().filter(id=movie.id).update(numorders=movie.numorders + int(item.quantity))
        item.save()

    topord = Movie.objects.all().order_by('-numorders').first()

    for moviex in Movie.objects.all():
        isord = (topord.numorders == moviex.numorders)
        if isord:
            Movie.objects.all().filter(id=moviex.id).update(mostorders= "Yes")      
        else:
            Movie.objects.all().filter(id=moviex.id).update(mostorders= "No")    

    for userx in User.objects.all():
        buyer, booleanCheck = Top_Buyer.objects.get_or_create(user=userx)

        all_items = Item.objects.filter(order__user=userx)
        total_purchased = 0
        for item in all_items:
            total_purchased += item.quantity
        Top_Buyer.objects.all().filter(user=userx).update(numPurchased=total_purchased)

    Top_Buyer.objects.all().update(mostPurchased=False)
    topuser = Top_Buyer.objects.all().order_by('numPurchased').last() # the most purchased user would be ascendingly at the bottom of the list
    if topuser:
        Top_Buyer.objects.all().filter(id=topuser.id).update(mostPurchased=True)
    request.session['cart'] = {}
    template_data = {}
    template_data['title'] = 'Purchase confirmation'
    template_data['order_id'] = order.id
    return render(request, 'cart/purchase.html',
        {'template_data': template_data})