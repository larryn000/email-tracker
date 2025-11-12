from app import db

class TemplateService:
    def __init__(self, db_session=None):
        self._db_session = db_session

    @property
    def db(self):
        return self._db_session if self._db_session is not None else db.session
    
    def create_template(self, template_id, template_name, subject, body):
        
        