from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
import json
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    encoding = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    user_type = Column(String, default="default_user")

    def set_encoding(self, np_array):
        self.encoding = json.dumps(np_array.tolist())

    def get_encoding(self):
        import numpy as np
        return np.array(json.loads(self.encoding))
