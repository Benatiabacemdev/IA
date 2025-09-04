import msal
import requests
import os
from PyPDF2 import PdfReader

class SharePointHelper:    
    def __init__(self):
        self.access_token = None
        self.client_id = os.getenv("SP_CLIENT_ID")
        self.client_secret = os.getenv("SP_CLIENT_SECRET")
        self.tenant_id = os.getenv("SP_TENANT_ID")
        self.site_url = os.getenv("SP_SITE_URL")
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scope = ["https://graph.microsoft.com/.default"]
        self.authenticate()

    def authenticate(self):
        app = msal.ConfidentialClientApplication(
            self.client_id, authority=self.authority, client_credential=self.client_secret
        )
        result = app.acquire_token_for_client(scopes=self.scope)
        if "access_token" in result:
            self.access_token = result["access_token"]
        else:
            raise Exception(f"Authentication error: {result.get('error_description')}")

    def get_site_id(self):
        if not self.access_token:
            raise Exception("Not authenticated. Call authenticate() first.")
        if not self.site_url:
            raise Exception("SP_SITE_URL not set in environment variables.")
        url = f"https://graph.microsoft.com/v1.0/sites/{self.site_url}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            site = response.json()
            print("Site trouvé:", site["id"], site["name"], site["webUrl"])
            return site
        else:
            print("Erreur:", response.status_code, response.text)
            raise Exception(f"Erreur lors de la récupération du site: {response.text}")
        
    def get_library_files(self, library_name):
        """
        Récupère les fichiers d'une bibliothèque SharePoint par son nom.
        """
        if not self.access_token:
            raise Exception("Not authenticated. Call authenticate() first.")
        # Récupérer l'ID du site
        site = self.get_site_id()
        site_id = site["id"]
        # Récupérer toutes les bibliothèques (drives) du site
        drives_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        drives_resp = requests.get(drives_url, headers=headers)
        if drives_resp.status_code != 200:
            raise Exception(f"Erreur lors de la récupération des drives: {drives_resp.text}")
        drives = drives_resp.json()["value"]
        # Trouver la bibliothèque par son nom
        drive = next((d for d in drives if d["name"].lower() == library_name.lower()), None)
        if not drive:
            raise Exception(f"Bibliothèque '{library_name}' non trouvée sur le site.")
        drive_id = drive["id"]
        # Récupérer les fichiers à la racine de la bibliothèque
        files_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root/children"
        files_resp = requests.get(files_url, headers=headers)
        if files_resp.status_code != 200:
            raise Exception(f"Erreur lors de la récupération des fichiers: {files_resp.text}")
        files = files_resp.json()["value"]
        # Retourne la liste des fichiers (nom, id, webUrl, taille, date création, date modification)
        return [
            {
                "name": f["name"],
                "id": f["id"],
                "webUrl": f["webUrl"],
                "size": f.get("size"),
                "createdDateTime": f.get("createdDateTime"),
                "lastModifiedDateTime": f.get("lastModifiedDateTime"),
                "driveId": drive_id
            }
            for f in files
        ]

    def get_pdf_text(self, drive_id, item_id):
        """
        Télécharge le PDF et retourne le texte extrait avec PyPDF2.
        """
        import io
        if not self.access_token:
            raise Exception("Not authenticated. Call authenticate() first.")
        url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}/content"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            pdf_bytes = io.BytesIO(response.content)
            reader = PdfReader(pdf_bytes)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            return text
        else:
            raise Exception(f"Erreur lors de la récupération du PDF: {response.text}")