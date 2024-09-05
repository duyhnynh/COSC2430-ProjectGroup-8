import datetime
from google.cloud import storage
import re

class Storage():
    def __init__(self) -> None:
        """
        Initializes and connects to the Google Cloud Storage.
        @returns: None
        """
        self.client = storage.Client.from_service_account_json('service-account-key.json')
        self.bucket = self.client.bucket('cosc2430-projectgroup-8')
    
    def upload_file(self, image, email=None, course_name=None) -> None:
        """
        Uploads a file to the Google Cloud Storage.
        @returns: None
        """
        # default extension and content type for simplification 
        extension = '.jpg' 
        content_type = 'image/jpeg' 

        if email:
            blob = self.bucket.blob('profile_pictures/' + email + extension)
        elif course_name:
            # remove slash or spaces from course name
            course_name = re.sub(r'[/\s]', '_', course_name).lower()
            blob = self.bucket.blob('course_images/' + course_name + extension)

        # upload the file to the bucket
        blob.upload_from_string(image.read(), content_type=content_type)

    def get_file(self, email=None, course_name=None) -> str:
        """
        Retrieves a file from the Google Cloud Storage.
        @returns: a string of the file's URL
        """
        if email:
            blob = self.bucket.blob('profile_pictures/' + email + '.jpg')
        elif course_name:
            # replace slash or space with underscore in course name
            course_name = re.sub(r'[/\s]', '_', course_name).lower()
            blob = self.bucket.blob('course_images/' + course_name + '.jpg')
        
        # generate a signed URL for the file
        signed_url = blob.generate_signed_url(expiration=datetime.timedelta(days=50), method='GET')

        return signed_url
    
    
    