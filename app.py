from flask import Flask, flash, render_template, request, session, redirect
from database import Database
import os

# create flask app
app = Flask(__name__)
app.secret_key = 'super secret' # used to encrypt session data, change later

# create database object
db = Database()

### HOME ROUTE ###
@app.route('/')
def root():
    """
    Renders the home page.
    @returns: renders 'home.html'.
    """
    return render_template('home.html')

### LOGIN ROUTES ###
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
        password = request.form.get('password')

        if email:
            # check if email exists
            if not db.check_existing_user('user', email=email):
                flash('Email does not exist')
            # get user data
            user_data = db.get_data('user', email)
            # check if password is correct
            if user_data['password'] != password:
                flash('Incorrect password')
        else:
            # check if phone number exists
            if not db.check_existing_user('user', phone=phone):
                flash('Phone does not exist')
            
            # get user data
            user_data = db.get_data('user', phone=phone)
            # check if password is correct
            if user_data['password'] != password:
                # flash message if password is incorrect
                flash('Incorrect password')

        user_data['email'] = user_data.key.name

        # store user data in session
        if user_data:
            session['user'] = user_data
            
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
        print(session['user'])
        user_data = {
            'full_name': f"{session['user']['first_name']} {session['user']['last_name']}",
            'address': f"{session['user']['address']}, {session['user']['city']}, {session['user']['zipcode']}, {session['user']['country']}",
            'email': session['user']['email'],
            'phone': session['user']['phone'],
        }

        return render_template('account.html', user_data=user_data)
    
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
        profile_picture = request.form.get('profile-picture') ## TODO: connect til google storage - MANGLER!!!!!
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
        
        # create data dictionary
        data = {
            'phone': phone,
            'password': password,
            # 'profile_picture': profile_picture,  TODO: connect til google storage - MANGLER!!!!!
            'first_name': first_name,
            'last_name': last_name,
            'address': address,
            'city': city,
            'zipcode': zipcode,
            'country': country,
            'role': account_type
        }

        # add additional data if account type is instructor
        if account_type == 'instructor':
            data['school_name'] = school_name
            data['job_title'] = job_title
            data['specialization'] = specialization
        
        # insert data to database
        db.insert_data(kind='user', id=email, data=data)
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
        if not db.check_existing_user('user', email=email):
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
        
        # update password in database
        db.update_data('user', email, {'password': password})
        flash('Password successfully reset')
        
        return redirect('/login')
    
    return render_template('reset_password.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True)