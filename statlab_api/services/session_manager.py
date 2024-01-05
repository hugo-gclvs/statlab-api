import logging
import re
import requests

logging.basicConfig(level=logging.INFO)

class SessionManager:
    def __init__(self, user, pwd):
        self.username = user
        self.password = pwd
        self.session = requests.Session()
        self.login_url = "https://casiut21.u-bourgogne.fr/cas-esirem/login?service=https%3A%2F%2Fiutdijon.u-bourgogne.fr%2Foge-esirem%2F"

    def login(self):
        """
        This method is used to login to the OGE.

        Parameters:
            None

        Returns:
            bool: True if the login was successful, False otherwise.
        """
        try:
            execution = self._get_execution_token(self.login_url)
            return self._perform_login(execution)
        except Exception as e:
            logging.error(f"Login failed: {e}")
            return False

    def _get_execution_token(self, url):
        """
        This method is used to get the execution token from the OGE login page.

        Parameters:
            url (str): The URL of the OGE login page.

        Returns:
            str: The execution token.
        """
        response = self.session.get(url, timeout=5)
        return re.search(r'name="execution" value="([^"]+)"', response.text).group(1)

    def _perform_login(self, execution):
            """
            This method is used to perform the login to the OGE.

            Parameters:
                execution (str): The execution token.

            Returns:
                bool: True if the login was successful, False otherwise.
            """
            payload = {
                'username': self.username,
                'password': self.password,
                'execution': execution,
                '_eventId': 'submit'
            }
            response = self.session.post(self.login_url, data=payload, timeout=5)
            if "Connexion - CAS" not in response.text:
                logging.info("Login successful")
                return True
            logging.error("Login failed")
            return False