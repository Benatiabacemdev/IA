import msal
import requests
import os

class SharePointRestHelper:
    def __init__(self):
        self.access_token = None
        self.client_id = os.getenv("SP_CLIENT_ID")
        self.client_secret = os.getenv("SP_CLIENT_SECRET")
        self.tenant_id = os.getenv("SP_TENANT_ID")
        self.site_url = "devatia.sharepoint.com/sites/RAG" #os.getenv("SP_SITE_URL")  # ex: 'contoso.sharepoint.com/sites/demo'
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scope = ["https://{0}/.default".format(self.site_url)]
        self.authenticate()

    def authenticate(self):
        app = msal.ConfidentialClientApplication(
            self.client_id, authority=self.authority, client_credential=self.client_secret
        )
        # Pour SharePoint REST, le scope est https://{tenant}.sharepoint.com/.default
        sharepoint_scope = [f"https://{self.site_url.split('/')[0]}/.default"]
        result = app.acquire_token_for_client(scopes=sharepoint_scope)
        if "access_token" in result:
            self.access_token = result["access_token"]
        else:
            raise Exception(f"Authentication error: {result.get('error_description')}")

    def get_library_files(self, library_name, folder_path=None):
        """
        Récupère les fichiers d'une bibliothèque SharePoint via REST API.
        library_name: nom de la bibliothèque (ex: 'Documents')
        folder_path: chemin relatif du dossier (optionnel)
        """
        if not self.access_token:
            raise Exception("Not authenticated. Call authenticate() first.")
        if not self.site_url:
            raise Exception("SP_SITE_URL not set in environment variables.")
        # Construction du chemin relatif
        site_parts = self.site_url.split('/')
        # ex: 'contoso.sharepoint.com/sites/demo' => site_name = 'demo'
        site_name = site_parts[-1]
        if folder_path:
            relative_url = f"/sites/{site_name}/{library_name}/{folder_path}"
        else:
            relative_url = f"/sites/{site_name}/{library_name}"
        api_url = f"https://{site_parts[0]}/_api/web/GetFolderByServerRelativeUrl('{relative_url}')/Files"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json;odata=verbose"
        }
        response = requests.get(api_url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Erreur lors de la récupération des fichiers: {response.text}")
        files = response.json()["d"]["results"]
        # Retourne la liste des fichiers (nom, url, taille, date création, date modification)
        return [
            {
                "name": f["Name"],
                "url": f["ServerRelativeUrl"],
                "size": f["Length"],
                "createdDateTime": f["TimeCreated"],
                "lastModifiedDateTime": f["TimeLastModified"]
            }
            for f in files
        ]
