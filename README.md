#Cinema Ticket Booking Project

Welcome to the CineFare! This Django-based application allows users to browse movies, select seats, and book tickets for their favorite films.

## Features
 • User Selecting Location - Once the user selects a specific location, the available movies and showtimes are filtered based on that location.
 • User registration and authentication - Users can sign up by providing required information such as username, email address, and password.
     Registered users are required to log in with their credentials to access the system.
•	 Movie selection and information - Users can browse a list of available movies on the platform.Depending on the user's location, we display a few trending trailers, recommended movies.
     The user can view every film showing in all local theatres by selecting the ALL MOVIES option,where the users are allowed to filter search results based on language, genre of the movie.
     User can select the date and show times based on price, show time, and colour distinction filters of available seats for that specific show are offered.
     Google Maps can be used to find the theater's location.
•	Seat reservation and selection - User can interact with the seat selection interface which displays a visual representation of the auditorium layout, organized into rows and columns.
     Seats are color-coded or visually marked to indicate their status as selected, occupied seats. 
•	Secure payment processing - User can complete the payment through credit card and various payment methods to confirm their ticket.And user can download ticket in pdf form.

## Tech Stacks

- Frontend: HTML, CSS, JavaScript
- Backend: Django Framework
- Database: dbsqlite
- Payment Integration: RazorPay

## HOW TO RUN
Before you begin, ensure that you have the following installed on your machine:
Python (version 3.6 or higher)
pip
Django (a Python web framework)

 ## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/CineFare_Moviebooking.git
   cd cinefare
2. Create and activate a virtual environment:
    python -m venv venv
    source  `venv\Scripts\activate`  
3. Install dependencies:
    pip install -r requirements.txt
4. Run Migrations:
    python manage.py migrate  
5. Create a superuser:
    python manage.py createsuperuser
6. Run the development server:
    python manage.py runserver

Visit http://localhost:8000 in your browser to access the application.

## DataBase Schema
The project uses dbsqlite as the database. The Django models include User, Movie, MovieComment , MovieRating, Theatre, Booked_Seats.
Configure Database Settings in settings.py:
  DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / "db.sqlite3",
    }
}
One can manage the database by accessing the Django admin interface at http://localhost:8000/admin/ using the superuser credentials for login.

## Usage

•	Register or log in to your account.
• Browse the list of available movies.
•	Select a movie and choose your preferred seats.
•	Proceed to the payment page and complete the booking.
•	Now user can download the ticket.
