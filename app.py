from datetime import datetime
from flask import Flask, flash, render_template, request, session, redirect, url_for
from flask_session import Session
from database import Database
from storage import Storage
from uuid import uuid4
import random
import pytz
import csv

# create flask app
app = Flask(__name__)
app.secret_key = 'super secret' # used to encrypt session data, change later
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem' # store session data in the filesystem
Session(app)

# create database and storage object
db = Database()
storage = Storage()

# get country data from csv file    
countries = []
with open('country_data.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f) # do not include first row and read rows into a dictionary format
    for row in reader:
        countries.append({'code': row['Code'], 'name': row['Name']})

# set timezone
vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')

### HOME ROUTE ###
@app.route('/')
def root():
    """
    Retrieves all courses and instructors from the database, and saves their IDs. 
    It then selects the latest 5 courses and instructors as well as featured courses and instructors (by random) and saves them in session variables.
    @returns: the rendered 'home.html' template with the new and featured courses and instructors.
    """
    if not check_session_var('courses') or not check_session_var('instructors'):
        # get all courses and instructors
        courses = db.get_data('course')
        instructors = db.get_instructors()

        # save course ids in courses dict
        for course in courses:
            course['id'] = course.key.id
    
        # save instructor ids in instructors dict
        for instructor in instructors:
            instructor['id'] = instructor.key.id

        # get latest 5 courses and instructors
        new_courses = sorted(courses, key=lambda x: x['created_at'], reverse=True)[:5]
        new_instructors = sorted(instructors, key=lambda x: x['created_at'], reverse=True)[:5]

        # save courses and instructors in session
        save_session_var('courses', courses)
        save_session_var('instructors', instructors)

        # save latest courses and instructors in session
        save_session_var('new_courses', new_courses)
        save_session_var('new_instructors', new_instructors)
    else:
        # get latest courses and instructors from session
        new_courses = session.get('new_courses')
        new_instructors = session.get('new_instructors')

    # check if featured courses and instructors are in session
    if not session.get('featured_courses') or not session.get('featured_instructors'):
        # get the five featured courses and instructors (random)
        featured_courses = random.sample(courses, 5)
        featured_instructors = random.sample(instructors, 5)

        # save featured courses and instructors in session
        save_session_var('featured_courses', featured_courses)
        save_session_var('featured_instructors', featured_instructors)
    else:
        # get featured courses and instructors from session
        featured_courses = session.get('featured_courses')
        featured_instructors = session.get('featured_instructors')

    return render_template('home.html', new_courses=new_courses, new_instructors=new_instructors, featured_courses=session['featured_courses'], featured_instructors=session['featured_instructors'])

### PRIVACY ROUTE ###
@app.route('/privacy')
def privacy():
    """
    Renders the privacy.html template.
    @returns: privacy.html template.
    """
    return render_template('privacy.html')

### TERMS ROUTE ###
@app.route('/terms')
def terms():
    """
    Renders the terms.html template.
    @returns: terms.html template.
    """
    return render_template('terms.html')

### HEADER AND FOOTER ROUTES ###
@app.route('/header')
def header():
    """
    Renders the header.html.
    @returns: header.html.
    """
    return render_template('header.html')

@app.route('/footer')
def footer():
    """
    Renders the footer.html.
    @returns: footer.html.
    """
    return render_template('footer.html')

### LOGIN ROUTE ###
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles login functionality.
    @returns: if login is successful, it redirects the user to the '/account' page.
              if login fails, it renders the 'account.html' template no 'user_data'.
    """
    if request.method == 'POST':
        # get form data
        if '@' in request.form.get('username'):
            email = request.form.get('username')
        else:
            phone = int(request.form.get('username'))
            email = None
        password = request.form.get('password')

        if email:
            # check if email exists
            if not db.check_existing_user(email=email):
                flash('Email does not exist')
                
            # get user data
            user_data = db.get_data('user', email=email)

            if not user_data:
                flash('Email does not exist')
                return redirect('/login')

            # check if password is correct
            if not db.check_credentials(password, email=email):
                flash('Incorrect password')
                return redirect('/login')
        else:
            # check if phone number exists
            if not db.check_existing_user(phone=phone):
                flash('Phone does not exist')
            
            # get user data
            user_data = db.get_data('user', phone=phone)

            # check if password is correct
            if not db.check_credentials(password, phone=phone):
                flash('Incorrect password')
                return redirect('/login')

        # store user data in session
        if user_data:
            # save user id
            user_data['id'] = user_data.key.id
            save_session_var('user', user_data)
        
        # redirect to account page
        return redirect('/account')

    return render_template('account.html', user_data=None)

### ACCOUNT ROUTE ###
@app.route('/account', methods=['GET', 'POST'])
def account():
    """
    Renders the account page with user data if the user is logged in.
    @returns: if the user is logged in, renders 'account.html' with user data. 
              otherwise, redirects to the login page.
    """
    if check_session_var('user'):
        # get mapping of country code to name
        country_name = country_code_to_name(session['user']['country'])

        # get user data
        user_data = {
            'name': session['user']['name'],
            'image': session['user']['image'],
            'address': f"{session['user']['address']}, {session['user']['city']}, {session['user']['zipcode']}, {country_name}",
            'email': session['user']['email'],
            'phone': session['user']['phone'],
            'role': session['user']['role']
        }

        # get orders
        orders = db.get_orders(user_id=session['user']['id'])
        
        # get course name for each order
        for order in orders:
            order['course_name'] = db.get_data('course', id=int(order['course_id']))['name']

        return render_template('account.html', user=user_data, orders=orders)
    
    # redirect to login route if user is not logged in
    return redirect('/login')

### REGISTER ROUTE ###
@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handles the registration for a new user account. 
    It performs validations before inserting the data into the database. 
    @returns: a redirect response to the login page, if registration is successful.
              otherwise, it renders 'register_account.html' again.
    """
    if request.method == 'POST':
        # get form data
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        password_retype = request.form.get('retype-password')
        profile_picture = request.files.get('profile-picture')
        first_name = request.form.get('first-name')
        last_name = request.form.get('last-name')
        address = request.form.get('address')
        city = request.form.get('city')
        zipcode = request.form.get('zipcode')
        country = request.form.get('country')
        account_type = request.form.get('account-type')
        
        # get additional data if account type is instructor
        if account_type == 'instructor':
            school_name = request.form.get('school-name')
            job_title = request.form.get('job-title')
            specialization = request.form.get('specialization')
        
        # check if email is already in use
        if db.check_existing_user(email=email):
            flash('Email is already in use')
            return redirect('/register')
        
        # also check if phone is already in use
        if db.check_existing_user(phone=phone):
            flash('Phone is already in use')
            return redirect('/register')

        # check if passwords match
        if password != password_retype:
            flash('Passwords do not match')
            return redirect('/register')
        
        # upload profile picture to google storage
        if profile_picture:
            storage.upload_file(profile_picture, email=email)
            picture_url = storage.get_file(email=email)
        
        # create data dictionary
        data = {
            'name': first_name + ' ' + last_name,
            'email': email,
            'phone': int(phone),
            'password': password,
            'image': picture_url if profile_picture else None,
            'address': address,
            'city': city,
            'zipcode': int(zipcode),
            'country': country,
            'role': account_type,
            'created_at': datetime.now(vn_tz).strftime('%Y-%m-%d %H:%M:%S')
        }

        # add additional data if account type is instructor
        if account_type == 'instructor':
            data['school_name'] = school_name
            data['job_title'] = job_title
            data['specialization'] = specialization
        
        # insert data to database
        db.insert_data(kind='user', data=data)
        flash('Account successfully created')

        # redirect to login page
        return redirect('/account')
    
    return render_template('register_account.html', countries=countries)

### FORGOT PASSWORD ROUTE ###
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """
    Handles the forgot password functionality.
    @returns: if the email exists, it sends a password reset link to the email.
              otherwise, it renders the 'forgot_password.html' template.
    """
    reset_link = None
    if request.method == 'POST':
        email = request.form.get('email')
        
        # check if email exists
        if not db.check_existing_user(email=email):
            flash('Email does not exist', category='message')
            return redirect('/forgot-password')
        
        # generate reset token
        reset_token = str(uuid4())

        # create reset link
        reset_link = url_for('reset_password', reset_token=reset_token, _external=True)

        # save email and reset link in session
        save_session_var('reset_email', email)

        # flash reset link
        flash(reset_link, category='link')

        # redirect to same route to prevent form resubmission and to show the reset link
        return redirect('/forgot-password')

    return render_template('forgot_password.html')

### RESET PASSWORD ROUTE ###
@app.route('/reset-password/<reset_token>', methods=['GET', 'POST'])
def reset_password(reset_token):
    """
    Resets password.
    @returns: if the password is successfully reset, it redirects to the login page.
              Or it will render 'forgot_password.html'.
    """
    if request.method == 'POST':
        reset_token = request.form.get('reset-token')
        email = session.get('reset_email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')
        
        # check if passwords match
        if password != confirm_password:
            flash('Passwords do not match')
            return redirect('/reset-password/' + reset_token)
        
        # get the user
        user = db.get_data('user', email=email)
        
        # update password in database
        db.update_data('user', user.key.id, {'password': password})
        flash('Password successfully reset')

        # remove email from session 
        session.pop('reset_email', None)
        
        return redirect('/login')
    
    return render_template('reset_password.html', reset_token=reset_token)

### LOGOUT ROUTE ###
@app.route('/logout')
def logout():
    remove_session_var('user')
    remove_session_var('courses')
    return redirect('/')

### BROWSE BY NAME ROUTE ###
@app.route('/courses/browse/name')
def browse_by_name():
    # check if courses are in session
    if not session.get('courses'):
        # get all courses
        courses = db.get_data('course')

        # save ids
        for course in courses:
            course['id'] = course.key.id

        # save courses in session
        save_session_var('courses', courses)
    else:
        # get courses from session
        courses = session.get('courses')

    # sort courses by alphabetical order of id
    courses = sorted(courses, key=lambda x: x['name'])

    return render_template('browse_courses_name.html', courses=courses)

### BROWSE BY CATEGORY ROUTE ###
@app.route('/courses/browse/category')
def browse_by_category():
    # check if courses are in session
    if not session.get('courses'):
        # get all courses
        courses = db.get_data('course')

        # save ids
        for course in courses:
            course['id'] = course.key.id

        # save courses in session
        save_session_var('courses', courses)
    else:
        # get courses from session
        courses = session.get('courses')

    # sort courses by category
    courses = sorted(courses, key=lambda x: x['category'])

    # get unique categories
    categories = set([course['category'] for course in courses])

    # create dictionary with categories as keys and courses as values
    courses_by_categories = {}

    # add courses to categories
    for category in categories:
        courses_by_categories[category] = [course for course in courses if course['category'] == category]

    return render_template('browse_courses_category.html', courses=courses_by_categories)

### COURSE DETAILS ROUTE ###
@app.route('/courses/<id>')
def course_details(id):
    if not session.get('courses'):
        courses = db.get_data('course')
        save_session_var('courses', courses)
    else:
        courses = session.get('courses')
    
    # find the selected course
    selected_course = [course for course in courses if int(course['id']) == int(id)][0]

    # get user role - default is 'guest' if not logged in
    user = session.get('user')
    user_role = user.get('role') if user else 'guest'

    return render_template('course_details.html', course=selected_course, user_role=user_role)

@app.route('/instructor/<id>')
def instructor_profile(id):
    if not session.get('instructors'):
        # get all instructors
        instructors = db.get_instructors()
        save_session_var('instructors', instructors)
    else:
        instructors = session.get('instructors')

    instructor = [instructor for instructor in instructors if int(instructor['id']) == int(id)][0]
    
    # get instructor's country name
    instructor['country'] = country_code_to_name(instructor['country'])

    if not check_session_var('courses'):
        courses = db.get_data('course')
        save_session_var('courses', courses)
    else:
        courses = session.get('courses')

    courses = [course for course in courses if course['instructor'] == instructor['name']]

    # get latest 5 courses
    new_courses = sorted(courses, key=lambda x: x['created_at'], reverse=True)[:5]

    # get current user's role
    user = session.get('user')
    user_role = user.get('role') if user else 'guest'

    return render_template('instructor_profile.html', instructor=instructor, new_courses=new_courses, courses=courses, user_role=user_role)

## COURSE ORDER PLACEMENT ##
@app.route('/courses/order/<course_id>', methods=['GET', 'POST'])
def course_order_placement(course_id):
    if not session.get('courses'):
        courses = db.get_data('course')
        save_session_var('courses', courses)
    else:
        courses = session.get('courses')
    
    course = [course for course in courses if int(course['id']) == int(course_id)][0]
    
    return render_template('course_order_placement.html', course=course)

### THANK YOU ROUTE ###
@app.route('/order/confirmation/<course_id>', methods=['GET', 'POST'])
def order_confirmation(course_id):
    if request.method == 'POST':
        payment_method = request.form.get('payment-method')
        certification = request.form.get('certification-option')
        access_duration = request.form.get('access-duration')
        
        # save to database
        data = {
            'course_id': course_id,
            'user_id': session['user']['id'],
            'payment_method': payment_method,
            'certification': certification,
            'access_duration': access_duration,
            'created_at': datetime.now(vn_tz).strftime('%Y-%m-%d %H:%M:%S')
        }

        db.insert_data(kind='order', data=data)
    
    return render_template('thank_you.html')

### ADD COURSE ROUTE ###
@app.route('/courses/add', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        # get form data
        name = request.form.get('name')
        price = request.form.get('price')
        description = request.form.get('description')
        image = request.files.get('main-image')
        category = request.form.get('category')
        
        # get instructor from current user
        instructor = session['user']['name']
        
        # check if course name is already in use
        if db.check_existing_course(course_name=name):
            flash('Course name is already in use')
            return redirect('/courses/add')
        
        if image:
            # upload image to google storage
            storage.upload_file(image, course_name=name)
            image_url = storage.get_file(course_name=name) # get image url

        # create data dictionary
        data = {
            'name': name,
            'price': price,
            'description': description,
            'category': category,
            'instructor': instructor,
            'image': image_url if image else None,
            'created_at': datetime.now(vn_tz).strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # insert data to database
        db.insert_data(kind='course', data=data)
        
        # get the course id
        course = db.get_data(kind='course', course_name=name)
        course['id'] = course.key.id
        
        # get session courses
        courses = session.get('courses')

        if courses:
            courses.append(course)
        else:
            courses = [course]

        # update session courses
        session['courses'] = courses

        # redirect to course details page
        return redirect(f'/courses/{course["id"]}')
    
    return render_template('add_course.html')


#### session functionality ####
def check_session_var(var: str):
    if session.get(var):
        return True
    else:
        return False
    
def save_session_var(var: str, value):
    session[var] = value

def remove_session_var(var: str):
    session.pop(var, None)

### helper functions ###
def country_code_to_name(code):
    country = [country['name'] for country in countries if country['code'] == code]
    return country[0] if country else None

if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True)