# LearnifyX (COSC2430 Web Programming - Full-Stack Web Application)
This is a full-stack web application project for COSC2430 Web Programming course at RMIT University (Semester 2, 2024). The project is developed by Group 8, a team of 4 students. This web application concerns creating an online learning platform for learners and instructors called LearnifyX. The application is developed using Python Flask for the backend and HTML, CSS, and JavaScript for the frontend with Jinja2 templating engine. The database used is Google Cloud Datastore and for image storage, Google Cloud Storage is used.

## Contribution Scores
All team members have contributed to the project. The contribution scores are as follows:
- Duy Huynh Ngoc (s3924704) - 5 points
- Eduardo Salcedo Fuentes (s4118015) - 5 points
- Lisa Maria Huynh (s4110118) - 5 points
- Tu Tran Thanh (s3957386) - 5 points

In conclusion, all team members have contributed equally to the project.

## Instructions to run the application

### Prerequisites
- Python 3.11 or higher

### Steps
1. Open a terminal and change directory to the project folder.
2. Install virtualenv by running the following command:
   ```bash
   pip install virtualenv
   ```
3. Create a virtual python environment by running the following command:
   ```bash
   python3 -m venv venv
   ```
4. Activate the virtual environment by running the following command:

   On macOS and Linux:
   ```bash
   source venv/bin/activate
   ```
   On Windows:
   ```bash
   venv\Scripts\activate
   ```
5. Install the required packages by running the following command:
   ```bash
   pip install -r requirements.txt
   ```
6. Run the application by running the following command:
   ```bash
   python app.py
   ```
7. Open a web browser and go to `http://127.0.0.1:5000/` to view the application.

## Test users
To test the application, you can use the following test users:

### Admin
- Email: admin@admin.com
- Password: admin

### Instructor
- Email: brooze3@sun.com
- Password: password
  
### Learner
- Email: jdoe@example.com
- Password: hej

In case, the passwords do not work, you can reset the password by clicking on the "Forgot password" link on the login page.

## Link to the demo video
Here is the link to the demo video of the application: [Demo](https://youtu.be/CKkMY91C08Q).