from dataclasses import dataclass
from datetime import datetime

@dataclass
class FolderModel:
    def __init__(self, id, folder_path, source_type, selected_date):
        self.id = id
        self.folder_path = folder_path
        self.source_type = source_type
        self.selected_date = selected_date
