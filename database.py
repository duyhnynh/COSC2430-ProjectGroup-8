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

    def get_data(self, kind, id=None, phone=None) -> str:
        """
        Retrieves data from the database based on the specified kind, id (email), or phone number.
        @returns: a list of entities if no id and no phone number or phone number is specified, or one entity if id is specified.
        """
        if id is None and phone is None:
            # get all data
            query = self.client.query(kind=kind)
            results = list(query.fetch())
            if kind == 'user':
                for entity in results:
                    entity['email'] = entity.key.name
            elif kind == 'course':
                for entity in results:
                    entity['name'] = entity.key.name
            return results
        elif phone and kind == 'user':
            # get data by phone number
            query = self.client.query(kind=kind)
            query.add_filter('phone', '=', int(phone))
            results = list(query.fetch())
            return results[0]
        else:
            # get data by id
            key = self.client.key(kind, id)
            entity = self.client.get(key)
            if entity != None:
                if kind == 'user':
                    # add email to the elemnt
                    entity['email'] = entity.key.name
                elif kind == 'course':
                    # add course name to element
                    entity['name'] = entity.key.name
            return entity

    def insert_data(self, kind, id, data) -> None:
        """
        Inserts new data into the database.
        @returns: None
        """
        # create a key for the new entity
        key = self.client.key(kind, id)
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

    def check_existing_user(self, kind, email=None, phone=None) -> bool:
        """
        Checks if a user with the specified email or phone number already exists in the database.
        @returns: True if the user exists, otherwise False.
        """
        query = self.client.query(kind=kind)

        if email: 
            key = self.client.key(kind, email)
            entity = self.client.get(key)
            if entity != None:
                return True
        elif phone:
            query.add_filter('phone', '=', int(phone))
            results = list(query.fetch())
            if len(results) > 0:
                return True
        
        return False
    
    def check_credentials(self, kind, password, email=None, phone=None) -> bool:
        """
        Checks if the provided credentials (email/phone number and password) are valid in the database.
        @returns: True for valid credentials, otherwise False.
        """
        if email:
            # get data by id (email)
            key = self.client.key(kind, email)
            entity = self.client.get(key)
            # check if password matches
            if entity != None and entity['password'] == password:
                return True
        elif phone:
            query = self.client.query(kind=kind)
            query.add_filter('phone', '=', int(phone))
            results = list(query.fetch())
            # check if password matches the entered phone number
            if results[0]['password'] == password:
                return True
        
        return False