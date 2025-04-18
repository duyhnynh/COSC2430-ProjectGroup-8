from google.cloud import datastore
import os

class Database():
    """
    Connects to the online database Google Cloud Datastore and interacts with it. 
    """
    def __init__(self) -> None:
        """
        Initializes and connects to datastore database.
        @returns: None
        """
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'service-account-key.json'
        self.client = datastore.Client(project='cosc2430-projectgroup-8')
        # print('Database connected')
        # print('Project ID:', self.client.project)

    def get_data(self, kind, email=None, phone=None, course_name=None, id=None) -> str:
        """
        Retrieves data from the database based on the specified kind, email, phone number, course_name or id (unique integer).
        @returns: the whole data for the specified kind if no email/phone/course/id is specified, otherwise return one entity.
        """
        if all(var is None for var in [email, phone, course_name, id]):
            # get all data
            query = self.client.query(kind=kind)
            results = list(query.fetch())
            return results
        elif phone and kind == 'user':
            # get data by phone number
            query = self.client.query(kind=kind)
            query.add_filter('phone', '=', int(phone))
            results = list(query.fetch())
            return results[0] if len(results) > 0 else None
        elif email and kind == 'user':
            # get data by email
            query = self.client.query(kind=kind)
            query.add_filter('email', '=', email)
            results = list(query.fetch())
            return results[0] if len(results) > 0 else None
        elif course_name and kind == 'course':
            # get data by course name
            query = self.client.query(kind=kind)
            query.add_filter('name', '=', course_name)
            results = list(query.fetch())
            return results[0] if len(results) > 0 else None
        else:
            # get data by id
            key = self.client.key(kind, id)
            entity = self.client.get(key)
            return entity

    def insert_data(self, kind, data) -> None:
        """
        Inserts new data into the database.
        @returns: None
        """
        # create a key for the new entity
        key = self.client.key(kind)
        entity = datastore.Entity(key=key)
        # update the entity with the data
        entity.update(data)
        self.client.put(entity)

    def update_data(self, kind, id, data) -> None:
        """
        Updates existing data in the database based on the specified kind and id.
        @returns: None
        """
        key = self.client.key(kind, id)
        # get the entity
        entity = self.client.get(key)
        entity.update(data)
        self.client.put(entity)

    def check_existing_user(self, email=None, phone=None) -> bool:
        """
        Checks if a user with the specified email or phone number already exists in the database.
        @returns: True if the user exists, otherwise False.
        """
        query = self.client.query(kind='user')

        if email: 
            query.add_filter('email', '=', email)
            results = list(query.fetch())
        elif phone:
            query.add_filter('phone', '=', int(phone))
            results = list(query.fetch())
        
        if len(results) <= 0:
            return False
        
        return True
    
    def check_credentials(self, password, email=None, phone=None) -> bool:
        """
        Checks if the provided credentials (email/phone number and password) are valid in the database.
        @returns: True for valid credentials, otherwise False.
        """
        query = self.client.query(kind='user')

        if email:
            # get data by email
            query.add_filter('email', '=', email)
            results = list(query.fetch())
        elif phone:
            query.add_filter('phone', '=', int(phone))
            results = list(query.fetch())
        
        try:
            # check password match
            if results[0]['password'] != password:
                return False
        except:
            return False
        
        return True
    
    def check_existing_course(self, course_name) -> bool:
        """
        Checks if the specified course name is already in the database.
        @returns: True if the course exists, otherwise False.
        """
        query = self.client.query(kind='course')
        query.add_filter('name', '=', course_name)
        results = list(query.fetch())
        
        if len(results) <= 0:
            return False
        
        return True
    
    def get_instructors(self) -> list:
        """
        Retrieves all instructors from the database.
        @returns: a list of instructors.
        """
        query = self.client.query(kind='user')
        query.add_filter('role', '=', 'instructor')
        results = list(query.fetch())
        return results
    
    def get_instructor(self, instructor_name) -> dict:
        """
        Retrieves instructor from database based on the specified name.
        @returns: the instructor entity.
        """
        query = self.client.query(kind='user')
        query.add_filter('name', '=', instructor_name)
        results = list(query.fetch())
        return results[0] if len(results) > 0 else None
    
    def get_orders(self, user_id) -> list:
        """
        Retrieves all orders from the database for the specified user.
        @returns: a list of orders.
        """
        query = self.client.query(kind='order')
        query.add_filter('user_id', '=', user_id)
        results = list(query.fetch())
        return results