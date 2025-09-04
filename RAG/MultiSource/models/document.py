from dataclasses import dataclass
from datetime import datetime

@dataclass
class DocumentModel:
    def __init__(self, id, filename, filepath, modifieddate, createddate, size, uids):
        self.id = id
        self.filename = filename
        self.filepath = filepath
        self.modifieddate = modifieddate
        self.createddate = createddate
        self.size = size
        self.uids = uids