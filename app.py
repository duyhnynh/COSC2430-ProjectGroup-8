from datetime import datetime
from flask import Flask, flash, render_template, request, session, redirect
from database import Database
from storage import Storage
import pytz

# create flask app
app = Flask(__name__)
app.secret_key = 'super secret' # used to encrypt session data, change later

# create database and storage object
db = Database()
storage = Storage()

# set timezone
vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')

### HOME ROUTE ###
@app.route('/')
def root():
    """
    Renders the home page.
    @returns: renders 'home.html'.
    """
    instructors = db.get_instructors()

    return render_template('home.html', instructors=instructors)

### PRIVACY ROUTE ###
@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

### HEADER AND FOOTER ROUTES ###
@app.route('/header')
def header():
    return render_template('header.html')

@app.route('/footer')
def footer():
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
            if not db.check_credentials('user', password, phone=phone):
                flash('Incorrect password')
                return redirect('/login')

        # store user data in session
        if user_data:
            session['user'] = user_data
        
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
    if session.get('user'):
        # get user data
        user_data = {
            'name': session['user']['name'],
            'image': session['user']['image'],
            'address': f"{session['user']['address']}, {session['user']['city']}, {session['user']['zipcode']}, {session['user']['country']}",
            'email': session['user']['email'],
            'phone': session['user']['phone'],
        }
        
        return render_template('account.html', user=user_data)
    
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
        if db.check_existing_user('user', email=email):
            flash('Email is already in use')
            return redirect('/register')
        
        # also check if phone is already in use
        if db.check_existing_user('user', phone=phone):
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
            print(picture_url)
        
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
    
    return render_template('register_account.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """
    Handles the forgot password functionality.
    @returns: if the email exists, it sends a password reset link to the email.
              otherwise, it renders the 'forgot_password.html' template.
    """
    reset_link = False
    if request.method == 'POST':
        email = request.form.get('email')
        
        # check if email exists
        if not db.check_existing_user(email=email):
            flash('Email does not exist')
            return redirect('/forgot_password')
        
        # TODO: make a password reset link to reset password
        # temporary solution: show reset input field
        reset_link = True
        session['reset_email'] = email
    
    return render_template('forgot_password.html', reset_link=reset_link)

@app.route('/reset_password', methods=['POST'])
def reset_password():
    """
    Resets password.
    @returns: if the password is successfully reset, it redirects to the login page.
              Or it will render 'forgot_password.html'.
    """
    if request.method == 'POST':
        email = session.get('reset_email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')
        
        # check if passwords match
        if password != confirm_password:
            flash('Passwords do not match')
            return redirect('/reset_password')
        
        # get the user
        user = db.get_data('user', email=email)
        
        # update password in database
        db.update_data('user', user.key.id, {'password': password})
        flash('Password successfully reset')
        
        return redirect('/login')
    
    return render_template('reset_password.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/courses/browse/name')
def browse_by_name():
    # get all courses
    courses = db.get_data('course')

    # save ids
    for course in courses:
        course['id'] = course.key.id

    # sort courses by alphabetical order of id
    courses = sorted(courses, key=lambda x: x['name'])

    # # create slug for course names
    # for course in courses:
    #     course['slug'] = generate_slug(course['name'])

    session['courses'] = courses

    return render_template('browse_courses_name.html', courses=courses)

@app.route('/courses/browse/category')
def browse_by_category():
    # get all courses
    courses = db.get_data('course')

    # save ids
    for course in courses:
        course['id'] = course.key.id

    # sort courses by category
    courses = sorted(courses, key=lambda x: x['category'])
    # save courses by categories in session

    # # create slug for course names
    # for course in courses:
    #     course['slug'] = generate_slug(course.key.name)

    # get unique categories
    categories = set([course['category'] for course in courses])

    # create dictionary with categories as keys and courses as values
    courses_by_categories = {}

    # add courses to categories
    for category in categories:
        courses_by_categories[category] = [course for course in courses if course['category'] == category]

    return render_template('browse_courses_category.html', courses=courses_by_categories)

def generate_slug(name):
    return name.replace(' ', '-').lower()

@app.route('/courses/<id>')
def course_details(id):
    # get courses by categories from session
    courses = session.get('courses')
    
    course = [course for course in courses if int(course['id']) == int(id)][0]

    # get user role - default is 'guest' if not logged in
    user = session.get('user')
    user_role = user.get('role') if user else 'guest'

    return render_template('course_details.html', course=course, user_role=user_role)

@app.route('/instructor/<id>')
def instructor_profile(id):
    # get instructor data
    instructor = db.get_data('user', id=int(id))
    
    if instructor is not None:
        # get courses by instructor
        courses = db.get_data('course')
        courses = [course for course in courses if course['instructor'] == instructor['name']]

        # save courses in session
        session['courses'] = courses

        # get latest 5 courses
        new_courses = sorted(courses, key=lambda x: x['created_at'], reverse=True)[:5]

        return render_template('instructor_profile.html', instructor=instructor, new_courses=new_courses, courses=courses)

    return redirect('/') # redirect to home page if instructor does not exist

if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True)