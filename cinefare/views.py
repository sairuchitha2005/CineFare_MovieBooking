from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from movies.models import ads,Movie,movieComment,movie_rating,theatre,booked_seats,location
from math import ceil
from django.views.decorators.csrf import csrf_exempt
import razorpay
from django.utils import timezone
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
current_date = timezone.localdate()
current_time = timezone.localtime(timezone.now()).time()

# Pages
def locationPage(request):
    return render(request,'location.html')

# ,show__gte=current_time

def HomePage(request,city):
    req_user = request.user
    leng = 0
    if req_user.is_authenticated:
        booked = booked_seats.objects.filter(user=req_user,date__gte=current_date).order_by('date')
        leng = len(booked)
    else:
        booked = None

    objects = ads.objects.all()
    no = len(objects)
    req_loc = location.objects.get(location__iexact=city)
    theatres = theatre.objects.filter(location=req_loc)
    movies = Movie.objects.filter(theatres__in=theatres).distinct()
    telugu_movies = Movie.objects.filter(theatres__in=theatres, language__contains='Telugu').distinct()
    tamil_movies = Movie.objects.filter(theatres__in=theatres, language__contains='Tamil').distinct()
    hindi_movies = Movie.objects.filter(theatres__in=theatres, language__contains='Hindi').distinct()
    params={'movies':movies, 'ads':objects, 'noads':range(no),'telugu_movies':telugu_movies,'tamil_movies':tamil_movies, 'hindi_movies':hindi_movies,'city':city,'booked':booked,'len':leng}
    return render(request,'home.html',params)

def allmovies(request, city):
    req_loc = location.objects.get(location__iexact=city)
    theatres = theatre.objects.filter(location=req_loc)
    objects = ads.objects.all()
    movies = Movie.objects.filter(theatres__in=theatres).distinct()
    no = len(objects)
    lang_filter = "Language"
    gen_filter = "Genre"
    params={'movies':movies, 'ads':objects, 'noads':range(no),'city':city,'lang_filter':lang_filter,'gen_filter':gen_filter}
    return render(request,'allmovies.html',params)

def genlang(request, city, gen, lang):
    req_loc = location.objects.get(location__iexact=city)
    theatres = theatre.objects.filter(location=req_loc)
    objects = ads.objects.all()
    if gen!="gen":
        if lang!="lang":
            movies = Movie.objects.filter(theatres__in=theatres,genre__contains=gen, language__contains=lang).distinct()
        else:
            movies = Movie.objects.filter(theatres__in=theatres,genre__contains=gen).distinct()
    else:
        movies = Movie.objects.filter(theatres__in=theatres,language__contains=lang).distinct()

    no = len(objects)
    lang_filter = lang
    gen_filter = gen
    params={'movies':movies, 'ads':objects, 'noads':range(no),'city':city,'lang_filter':lang_filter,'gen_filter':gen_filter}
    return render(request,'allmovies.html',params)

def movie(request, id, city):
    movie = Movie.objects.get(movie_id=id)
    try:
        rate = movie_rating.objects.get(movie=movie)
    except movie_rating.DoesNotExist:
        rate = movie_rating(movie=movie, rating=0, numratings=0)
        rate.save()
    comments = movieComment.objects.filter(movie=movie)
    genres = movie.genre.split(',')
    liked = Movie.objects.filter(genre__icontains=genres[0].strip()).exclude(movie_id=id)
    for genre in genres[1:]:
        liked = liked | Movie.objects.filter(genre__icontains=genre.strip()).exclude(movie_id=id)
    print(current_date)
    params = {'movie': movie, 'liked': liked, 'comments':comments,'user':request.user,'rate':rate,'city':city,'date':current_date}
    return render(request, 'movie.html', params)

def search_movies(request, city):
    if request.method == "POST":
        search = request.POST['search_movies']
        try:
            movie = Movie.objects.get(movie_title__iexact=search)
            return redirect(f"/{city}/movie/{movie.movie_id}/")
        except Movie.DoesNotExist:
            movies = Movie.objects.filter(movie_title__contains=search)
            no = len(movies)
            if no == 0:
                messages.error(request, "No Movies are found!!")
                return redirect(f"/{city}/")
            params = {'movies': movies, 'nomovies': range(no),'city':city}
            return render(request, 'search.html', params)
    return render(request, 'search.html')

def postComment(request,city):
    if request.method =="POST":
        comment = request.POST.get("comment")
        user = request.user
        movie_id = request.POST.get("movie_id")
        movie = Movie.objects.get(movie_id=movie_id)
        
        comment = movieComment(comment=comment, user=user, movie=movie)
        comment.save()
        messages.success(request,"Your comment has been posted successfully!")
    return redirect(f"/{city}/movie/{movie.movie_id}/")

def ratenow(request,city):
    if request.method == "POST":
        user_rate = request.POST.get("user_rate")
        movie_id = request.POST.get("movie_id")
        movie = Movie.objects.get(movie_id=movie_id)
        print(user_rate)
        try:
            rating_obj = movie_rating.objects.get(movie=movie)
        except movie_rating.DoesNotExist:
            rating_obj = movie_rating(movie=movie, rating=0, numratings=0)
            rating_obj.save()

        rating_obj.numratings += 1
        rating_obj.rating = (rating_obj.rating * (rating_obj.numratings - 1) + 6-int(user_rate)) / rating_obj.numratings
        rating_obj.save()

        messages.success(request, "You rated successfully!")

    return redirect(f"/{city}/movie/{movie.movie_id}/")

def alltheatres(request, id, city,date):
    movie = Movie.objects.get(movie_id=id)
    loc = location.objects.get(location__iexact=city)
    theatres = theatre.objects.filter(movies=movie,location=loc)
    tomorrow = current_date + timezone.timedelta(days=1)
    dat = current_date + timezone.timedelta(days=2)
    time_now = timezone.localtime(timezone.now())
    first_show = datetime.strptime('11:00:00', '%H:%M:%S').time()
    second_show = datetime.strptime('14:30:00', '%H:%M:%S').time()
    third_show = datetime.strptime('18:00:00', '%H:%M:%S').time()
    last_show = datetime.strptime('21:00:00', '%H:%M:%S').time()
    c1=0
    c2=0
    c3=0
    c4=0
    date = datetime.strptime(date, '%b. %d, %Y')
    if date.date() == current_date:
        if current_time>first_show:
            c1=1
        if current_time>second_show:
            c2=1
        if current_time>third_show:
            c3=1
        if current_time>last_show:
            c4=1
    date = date.date()
    params = {'movie':movie, 'theatres':theatres,'city':city,'date':current_date,'tom':tomorrow,'dat':dat,'sel':date,'time':time_now,'c1':c1,'c2':c2,'c3':c3,'c4':c4}
    return render(request,'theatres.html', params)

def seats(request, id, show, tname, city, date):
    movie = Movie.objects.get(movie_id=id)
    t = theatre.objects.get(theatre_name=tname)
    show = show
    date = datetime.strptime(date, '%b. %d, %Y')
    bs = booked_seats.objects.filter(theatre=t, show=show, movie=movie,date=date.date()).values_list('seat_no', flat=True)
    bs = [item for sublist in [elem.split(',') if ',' in elem else [elem] for elem in bs] for item in sublist]
    params = {
        'movie': movie,
        'theatre': t,
        'date':date.date(),
        'show': show,
        'booked_seats':bs,
        'city':city,
    }
    return render(request, 'seats.html', params)

def reserve_seats(request, id, show, tname, city, date):
    if request.method == 'POST':
        result_list = request.POST.get('selected_seats')
        values = result_list.strip('[]').replace('"', '')
        print(len(values))
        if len(values)==2:
            price=25000
        else:
            price = (len(values)+1)/3*25000
        print(values)
        movie = Movie.objects.get(movie_id=id)
        t = theatre.objects.get(theatre_name=tname)
        user = request.user
        print(price)
        date = datetime.strptime(date, '%b. %d, %Y')
        client = razorpay.Client(auth=("rzp_test_v9sDWwBdexUf2L", "6r3HPNeTIbDKuRHVAGlL7Ywa"))
        DATA = {
            "amount": price,
            "currency": "INR",
        }
        pay = client.order.create(data=DATA)
        print(pay)
        booked_seat = booked_seats(seat_no=values,theatre=t,show=show,movie=movie,user=user,date=date.date())
        booked_seat.save()
        return render(request,'payment.html',{'city':city,'payment':pay,'c':0})

def generate_pdf(request,city,book):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="cinefare_booking.pdf"'
    print(book)
    bookk = book.split()
    print(bookk)
    booking = booked_seats.objects.get(seat_no=bookk[0])
    # Create a PDF object
    pdf = canvas.Canvas(response, pagesize=letter)
    # Create a paragraph style
    style = ParagraphStyle(
        'my_custom_style',
        fontSize=12,
        leading=16
    )
    text_content = [
        Paragraph(f"*Movie Tickect Details*", style),
        Paragraph(f"<b>Id:</b> 346323456", style),
        Paragraph(f"<b>Movie:</b> {booking.movie}", style),
        Paragraph(f"<b>Date:</b> {booking.date}", style),
        Paragraph(f"<b>Show:</b> {booking.show}", style),
        Paragraph(f"<b>Theatre:</b> {booking.theatre}", style),
        Paragraph(f"<b>Seats:</b> {bookk[0]}", style),
    ]
    # Draw the paragraphs on the PDF
    y_coordinate = 750
    for text_object in text_content:
        text_object.wrapOn(pdf, 400, 100)
        text_object.drawOn(pdf, 100, y_coordinate)
        y_coordinate -= 20
    # # Draw an image on the PDF
    image_path = 'static\images.png'
    image = ImageReader(image_path)
    pdf.drawImage(image, 100, 500, width=150, height=150)

    # Save the PDF content
    pdf.save()

    return response      

@csrf_exempt
def payment(request,city):
    c=1
    return render(request,'payment.html',{'c':c,'city':city})

# Authentiacation
def Signup(request, city):
    if request.method == "POST":
        # Get the parameters
        loc = city
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        mobileno = request.POST['mobileno']
        email = request.POST['email']
        pass1 = request.POST['pass0']
        pass2 = request.POST['pass2']
        user=User.objects.filter(username=username)
        if user.exists():
            messages.error(request,"Username already exists! Try another")
            return redirect(f'/{loc}/')
        if pass1!=pass2:
            messages.error(request,"Please enter same password in both!!")
            return redirect(f'/{loc}/')
        myuser = User.objects.create_user(username=username,email=email,password=pass1) 
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.mobileno = mobileno
        myuser.save()
        messages.success(request,"Your Cinefare account has been Successfully Created!!")
        return redirect(f'/{loc}/')
    return render(request,'signin.html')

def edit(request,city):
    if request.method == "POST":
        # Get the parameters
        loc = city
        fname = request.POST['fname']
        lname = request.POST['lname']
        mobileno = request.POST['mobileno']
        email = request.POST['email']
        myuser=request.user
        if fname!="":
            myuser.first_name = fname
        if lname!="":
            myuser.last_name = lname
        if mobileno!="":
            myuser.mobileno = mobileno
        if email!="":
            myuser.email = email
        myuser.save()
        messages.success(request,"Changes saved successfully!!")
        return redirect(f'/{loc}/')
    return redirect(f'/{loc}/')

def Login(request, city):
    if request.method == "POST":
        # Get the parameters
        loginusername = request.POST['username']
        loginpassword = request.POST['pass1']
        loc = city
        user = authenticate(username=loginusername,password=loginpassword)
        if user is not None:
            login(request,user)
            messages.success(request,"Succesfully logged in")
            return redirect(f'/{loc}/')
        else:
            messages.error(request,"Invalid Credentials!!")
            return redirect(f'/{loc}/')    
    return render(request,'signin.html',{'city':city})

def Logout(request,city):
    loc = city
    logout(request)
    messages.success(request,"Successfully Logged out!!")
    return redirect(f'/{loc}/')
