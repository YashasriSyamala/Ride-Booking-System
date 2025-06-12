import gridfs
import io
from app.database import Database

class Gridfs:
    fs = None

    @staticmethod
    def initialize(app):
        if Gridfs.fs is None:
            Gridfs.fs = gridfs.GridFS(Database.get_db())
    
    @staticmethod
    def get_fs():
        return Gridfs.fs