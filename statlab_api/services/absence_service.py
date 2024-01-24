import logging
from bs4 import BeautifulSoup
import services.utils.data_processing as data_processing


class AbsenceService:
    def __init__(self, oge_scraper):
        self.oge_scraper = oge_scraper

    def _fetchAllAbsences(self):
        """
        This method is used to fetch all absences.

        Parameters:
            None

        Returns:
            list: The list of absences.
        """
        semesters = self._countSemesters()
        absences = []
        for semester in range(semesters, 0, -1):
            absencesAjaxPage = self._fetchAbsencesForSemester(semester)
            absencesPage = self.oge_scraper.getAbsencesPage()
            
            if absencesPage:
                absences.extend(data_processing.create_absences(absencesPage))
        return absences
    
    def getAllSubjectsAbsences(self):
        """
        This method is used to get all subjects absences.

        Parameters:
            None

        Returns:
            list: The list of subjects absences.
        """
        absences = self._fetchAllAbsences()
        return list({absence.subject for absence in absences})

    def getAllClassroomsAbsences(self):
        """
        This method is used to get all classrooms absences.

        Parameters:
            None

        Returns:
            list: The list of classrooms absences.
        """
        absences = self._fetchAllAbsences()
        return list({absence.classroom for absence in absences})

    def getAllTeachersAbsences(self):
        """
        This method is used to get all teachers absences.

        Parameters:
            None

        Returns:
            list: The list of teachers absences.
        """
        absences = self._fetchAllAbsences()
        return list({absence.teacher for absence in absences})

    def getAbsencesByPeriod(self, timestamp_start, timestamp_end):
        """
        This method is used to get absences by period.

        Parameters:
            timestamp_start (int): The start timestamp.
            timestamp_end (int): The end timestamp.

        Returns:
            list: The list of absences.
        """
        absences = self._fetchAllAbsences()
        return [absence for absence in absences if timestamp_start <= absence.start_date.timestamp() <= timestamp_end]

    def getAbsencesBySemester(self, semester):
        """
        This method is used to get absences by semester.

        Parameters:
            semester (int): The semester.

        Returns:
            list: The list of absences.
        """
        absencesPage = self._fetchAbsencesForSemester(semester)
        return data_processing.create_absences(absencesPage) if absencesPage else []
    
    def getAbsencesWithMultipleFilters(self, teacher=None, classroom=None, subjectType=None):
        """
        Get absences filtered by multiple criteria: teacher, classroom, and subject type.

        Parameters:
            teacher (str, optional): The teacher name.
            classroom (str, optional): The classroom name.
            subjectType (str, optional): The subject type.

        Returns:
            list: The list of filtered absences.
        """
        absences = self._fetchAllAbsences()

        if teacher:
            absences = [absence for absence in absences if absence.teacher == teacher]
        
        if classroom:
            absences = [absence for absence in absences if absence.classroom == classroom]

        if subjectType:
            absences = [absence for absence in absences if absence.subjectType == subjectType]

        return absences
    
    def getAllAbsencesByTeacher(self, teacher):
        """
        This method is used to get absences by teacher.

        Parameters:
            teacher (str): The teacher name.

        Returns:
            list: The list of absences.
        """
        absences = self._fetchAllAbsences()
        return [absence for absence in absences if absence.teacher == teacher]

    def getAllAbsencesByClassroom(self, classroom):
        """
        This method is used to get all absences by classroom.

        Parameters:
            classroom (str): The classroom name.

        Returns:
            list: The list of absences.
        """
        absences = self._fetchAllAbsences()
        return [absence for absence in absences if absence.classroom == classroom]

    def getAllAbsencesBySubjectType(self, subjectType):
        """
        This method is used to get all absences by subject type.

        Parameters:
            subjectType (str): The subject type.

        Returns:
            list: The list of absences.
        """
        absences = self._fetchAllAbsences()
        return [absence for absence in absences if absence.subjectType == subjectType]

    def getAllAbsences(self):
        """
        This method is used to get all absences.

        Parameters:
            None

        Returns:
            list: The list of absences.
        """
        return self._fetchAllAbsences()

    def _countSemesters(self):
        """
        This method is used to count the number of semesters.

        Parameters:
            None

        Returns:
            int: The number of semesters.
        """
        try:
            minSemester = self._getMinSemester()
            maxSemester = self._getMaxSemester()
            return maxSemester - minSemester + 1
        except Exception as e:
            logging.error(f"Error in counting semesters: {e}")
            return 0
        
    def _getMinSemester(self):
        """
        This method is used to get the minimum semester.

        Parameters:
            None

        Returns:
            int: The minimum semester.
        """
        try:
            absencesPage = self.oge_scraper.getAbsencesPage()
            soup = BeautifulSoup(absencesPage, 'html.parser')
            min_semester_text = soup.find('span', class_='ui-menuitem-text').get_text()
            min_semester = int(min_semester_text.split()[-1])
            return min_semester
        except Exception as e:
            logging.error(f"Error in getting min semester: {e}")
            return 0
        
    def _getMaxSemester(self):
        """
        This method is used to get the maximum semester.

        Parameters:
            None

        Returns:
            int: The maximum semester.
        """
        try:
            absencesPage = self.oge_scraper.getAbsencesPage()
            soup = BeautifulSoup(absencesPage, 'html.parser')
            max_semester_text = soup.find_all('span', class_='ui-menuitem-text')[-1].get_text()
            max_semester = int(max_semester_text.split()[-1])
            return max_semester
        except Exception as e:
            logging.error(f"Error in getting max semester: {e}")
            return 0

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
    