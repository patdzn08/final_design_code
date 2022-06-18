from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, DateTime

base = declarative_base()

# Detected Node Class
class DetectedNode(base):
    
    # Name of the Table in the Database
    __tablename__ = "detected_node"

    # ID (Primary Key)
    detected_node_id = Column(Integer, primary_key=True)

    # Data Column
    data = Column(Integer)

    # Date and Time Column
    date_time = Column(DateTime(timezone=True))

    # Count threshold based on selected user preference
    count_thresh = Column(Integer)

    # Displays Columns' Value
    def __repr__(self):
        return f"DetectedNode(detected_node_id='{self.detected_node_id}')"