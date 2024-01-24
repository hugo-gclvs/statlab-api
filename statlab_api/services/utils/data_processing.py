import re
from bs4 import BeautifulSoup
from services.processors.absence_processor import AbsenceProcessor

def create_absences(absencesPage):
	soup = BeautifulSoup(absencesPage, 'html.parser')

	specific_table = soup.find('table', id='ficheEtudiantForm:j_id_1a')
	absences_table = specific_table.find_all('tr', class_='ui-widget-content')

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

	student_info_table = soup.find('table', {"id": "pageDossierForm:EtuInfoPanelGrid"})

	name_line = student_info_table.find('span', style=lambda value: value and 'font-size:1.6em' in value)
	if name_line:
			full_name = name_line.get_text().strip()
			last_name, first_name = full_name.split()[:2] 

	# Extraire le groupe
	group_line = student_info_table.find_all('td')[-2]
	if group_line:
			group_text = group_line.get_text().strip()
			group = group_text.split()[0]

			match = re.match(r"([a-zA-Z]+)([0-9]+)", group)
			if match:
					specialization, study_year = match.groups()

	return {
		"last_name": last_name,
		"first_name": first_name,
		"specialization": specialization,
		"study_year": study_year,
	}
