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
	