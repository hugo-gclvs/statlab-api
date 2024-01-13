from bs4 import BeautifulSoup
from services.processors.absence_processor import AbsenceProcessor

def create_absences(absencesPage):
	soup = BeautifulSoup(absencesPage, 'html.parser')

	absences_table = soup.find_all('tr', class_='ui-widget-content')

	absences_data = []
	for row in absences_table:
		columns = row.find_all('td', class_='ui-panelgrid-cell')
		absence_data = [column.get_text(strip=True) for column in columns]
		absences_data.append(absence_data)

	absences = []

	processor = AbsenceProcessor(absences_data)
	absences = processor.process_all()

	return absences
	

def create_student_info(studentInfoPage):
	soup = BeautifulSoup(studentInfoPage, 'html.parser')

	student_info_table = soup.find('table', id_='pageDossierForm:EtuInfoPanelGrid')

	print(student_info_table)
	# student_info_data = []
	# for row in student_info_table.find_all('tr'):
	# 	columns = row.find_all('td')
	# 	student_info_data.append([column.get_text(strip=True) for column in columns])

	# student_info = {}

	# for row in student_info_data:
	# 	student_info[row[0]] = row[1]

	return "student_info", "student_info", "student_info"
