import logging
from bs4 import BeautifulSoup
import services.utils.data_processing as data_processing


class PersonnalInfoService:
    def __init__(self, oge_scraper):
        self.oge_scraper = oge_scraper
    
    def getStudentInfo(self):
        """
        This method is used to get the student information.

        Parameters:
            None

        Returns:
            dict: The student information.
        """
        studentInfoPage = self.oge_scraper.getPersonnalInfoPage()
        return data_processing.create_student_info(studentInfoPage)


    def getAllAbsences(self):
        """
        This method is used to get all absences.

        Parameters:
            None

        Returns:
            list: The list of absences.
        """
        return self._fetchAllAbsences()


    def _fetchAbsencesForSemester(self, semester):
        """
        This method is used to select the absences semester.

        Parameters:
            semester (int): The semester to select.

        Returns:
            str: The absences page.
        """
        try:
            return self.oge_scraper.postAbsencesForSemester(semester)
        except Exception as e:
            logging.error(f"Error in selecting absences semester: {e}")
            return None
    