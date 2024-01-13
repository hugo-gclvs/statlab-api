class OgeScraper:
    def __init__(self, session_manager):
        self.session_manager = session_manager
        
        # Initialisation des URLs
        self.initialize_urls()
        
    def initialize_urls(self):
        """
        This method is used to initialize the URLs of the OGE.

        Parameters:
            None

        Returns:
            None
        """
        self.home_url = "https://iutdijon.u-bourgogne.fr/oge-esirem/"
        self.login_url = "https://casiut21.u-bourgogne.fr/cas-esirem/login?service=https%3A%2F%2Fiutdijon.u-bourgogne.fr%2Foge-esirem%2F"
        self.absences_url = "https://iutdijon.u-bourgogne.fr/oge-esirem/stylesheets/etu/absencesEtu.xhtml"
        self.grades_url = "https://iutdijon.u-bourgogne.fr/oge-esirem/stylesheets/etu/bilanEtu.xhtml"
        self.personnal_info_url = "https://iutdijon.u-bourgogne.fr/oge-esirem/stylesheets/etu/dossierEtu.xhtml"
            

    def get(self, url):
        """
        This method is used to send a GET request to the OGE.
        
        Parameters:
            url (str): The URL of the request.
            
        Returns:
            requests.Response: The response of the request.
        """
        print(f"Get {url}")
        return self.session_manager.session.get(url)
    
    def getPersonnalInfoPage(self):
        """
        This method is used to get the personnal info page from the OGE.

        Parameters:
            None

        Returns:
            str: The personnal info page.
        """
        response = self.session_manager.session.get(self.personnal_info_url)
        return response.text

    def getAbsencesPage(self):
        """
        This method is used to get the absences page from the OGE.

        Parameters:
            None

        Returns:
            str: The absences page.
        """
        response = self.session_manager.session.get(self.absences_url)
        return response.text
    
    def getGradesPage(self):
        """
        This method is used to get the grades page from the OGE.

        Parameters:
            None
            
        Returns:
            str: The grades page.
        """
        response = self.session_manager.session.get(self.grades_url)
        return response.text
    
    def _get_headers(self):
        """
        This method is used to get the headers for the request.

        Parameters:
            None

        Returns:
            dict: The headers.
        """
        return {
            "Faces-Request": "partial/ajax",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
    
    def postAbsencesForSemester(self, semester):
        """
        This method is used to select the absences semester.

        Parameters:
            semester (int): The semester to select.

        Returns:
            str: The absences page.
        """
        data = self._get_absences_data(semester)
        response = self.session_manager.session.post(self.absences_url, data=data, headers=self._get_headers())
        return self._extract_content(response)

    def _extract_content(self, response):
        """
        This method is used to extract the content from the response.

        Parameters:
            response (requests.Response): The response to process.

        Returns:
            str: The content.
        """
        content = response.text.split("![CDATA[")[1].split("]]")[0]
        return content
    
    def _get_absences_data(self, semester):
        """
        This method is used to get the data for the request.

        Parameters:
            semester (int): The semester to select.

        Returns:
            dict: The data.
        """
        return {
            "javax.faces.partial.ajax": "true",
            "javax.faces.source": "ficheEtudiantForm:j_id_16_" + str(semester),
            "javax.faces.partial.execute": "@all",
            "javax.faces.partial.render": "ficheEtudiantForm:panel",
            "ficheEtudiantForm:j_id_16_" + str(semester): "ficheEtudiantForm:j_id_16_" + str(semester),
            "ficheEtudiantForm_SUBMIT": "1",
            "javax.faces.ViewState": "0"
        }