from datetime import datetime
from services.model.absences import Absence
import time
import re

class AbsenceProcessor:

    id_counter = 0

    def __init__(self, data):
        self.data = data

    def process_all(self):
        absences = []
        for entry in self.data:
            if entry:
                parser = self._determine_parser(entry[0])
                if parser:
                    absences.append(parser(entry))
        return absences

    def _determine_parser(self, entry):
        if "ITC" in entry or "MDD" in entry:
            return self._parse_itc_format
        elif "CM" in entry or "TD" in entry or "TP" in entry or "Projets" in entry:
            return self._parse_standard_format
        # Add more conditions for different formats
        return None

    def _parse_standard_format(self, entry):
        parts = entry[0].split(' \n ')
        subject_details = parts[0]
        classroom_info = parts[1] if len(parts) > 1 else "Unknown"

        subject_parts = subject_details.split()

        subject_type_index = -1

        # Find the index where CM, TD, TP, Projects appears
        for i, part in enumerate(subject_parts):
            if part in ["CM", "TD", "TP", "Projets"]:
                subject_type_index = i
                break

        if subject_type_index == -1:
            subject = subject_details  # Fallback if no type found
            subject_type = "Unknown"
        else:
            subject = ' '.join(subject_parts[:subject_type_index])
            subject_type = subject_parts[subject_type_index]

        classroom = classroom_info.split(' (')[0]

        return self._create_absence_object(entry, subject, subject_type, classroom)



    def _parse_itc_format(self, entry):
        subject_details = entry[0].split(' \n ')
        subject_parts = subject_details[0].split('_')

        # Code du cours (ex : 'ITC316') et description supplémentaire, si elle existe
        subject_name = subject_parts[0]
        if len(subject_parts) > 2:
            subject_name += ' ' + ' '.join(subject_parts[2:])

        # Extraire uniquement les lettres pour le type de cours (ex : 'TP2' -> 'TP')
        subject_type_match = re.match(r"([A-Za-z]+)", subject_parts[1])
        subject_type = subject_type_match.group(0) if subject_type_match else "Unknown"

        # Informations sur la salle de classe
        classroom = subject_details[1].split(' (')[0]

        return self._create_absence_object(entry, subject_name, subject_type, classroom)


    def _create_absence_object(self, entry, subject, subjectType, classroom):
        teacher = entry[1]
        start_date, end_date = self.convert_to_timestamps(entry[2])
        justification = entry[3] if len(entry) > 3 else "Justifié"
        AbsenceProcessor.id_counter += 1
        return Absence(AbsenceProcessor.id_counter, subject, subjectType, classroom, teacher, start_date, end_date, justification)
    
    def convert_to_timestamps(self, date_str):
        # If date_str is "Aucun", then return fake timestamps
        if(date_str == "Aucun"):
            return 0, 0
        date_part, times_part = date_str.replace("Le ", "").split(' de ')
        start_time_str, end_time_str = times_part.split(' à ')

        # Combining date and start time, and converting to a timestamp
        start_datetime_str = f"{date_part} {start_time_str}"
        start_dt_obj = datetime.strptime(start_datetime_str, "%d/%m/%Y %H:%M")
        start_timestamp = int(time.mktime(start_dt_obj.timetuple()))

        # Combining date and end time, and converting to a timestamp
        end_datetime_str = f"{date_part} {end_time_str}"
        end_dt_obj = datetime.strptime(end_datetime_str, "%d/%m/%Y %H:%M")
        end_timestamp = int(time.mktime(end_dt_obj.timetuple()))

        return start_timestamp, end_timestamp