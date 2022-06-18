from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from .tables import *

# Database handler class
class NodesDB(object):

    # Constructor
    def __init__(self, db_name):
        self.engine = create_engine('sqlite:///{db_name}.db'.format(db_name=db_name))
        base.metadata.create_all(self.engine)
        self.session = Session(self.engine)

    # Insert a new row 
    def add(self, **kwargs):
        detected_node = DetectedNode(**kwargs)
        self.session.add(detected_node)
        self.session.commit()
        self.session.close()

    # Get all rows
    def getall(self):
        return self.session.query(DetectedNode).all()

    # Get the total number of rows
    def total(self):
        return self.session.query(DetectedNode).count()