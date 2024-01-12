import datetime
from firebase_admin import firestore

db = firestore.client()

def get_user_details(user_ref):
    user_doc = user_ref.get()
    if user_doc.exists:
        return user_doc.to_dict()
    return None

def get_subject_type_details(subject_type_ref):
    subject_type_doc = subject_type_ref.get()
    if subject_type_doc.exists:
        return subject_type_doc.to_dict()
    return None

def convert_document_to_dict(document):
    """ Converts a Firestore DocumentSnapshot into a dictionary. """
    dict_document = document.to_dict()
    dict_document['id'] = document.id

    # Handle the 'username' field
    user_ref = dict_document.get('username') or dict_document.get('users')
    if isinstance(user_ref, firestore.DocumentReference):
        user_details = get_user_details(user_ref)
        dict_document['username'] = user_details.get('username') if user_details else None
    else:
        dict_document['username'] = user_ref if user_ref else None

    # Handle the 'subjectType' field only if it exists
    if 'subjectType' in dict_document:
        subject_type_ref = dict_document.get('subjectType')
        if isinstance(subject_type_ref, firestore.DocumentReference):
            subject_type_details = get_subject_type_details(subject_type_ref)
            dict_document['subjectType'] = subject_type_details.get('type') if subject_type_details else None
        else:
            dict_document['subjectType'] = subject_type_ref if subject_type_ref else None

    # Convert datetime objects to ISO format
    for key, value in list(dict_document.items()):
        if isinstance(value, datetime.datetime):
            dict_document[key] = value.isoformat()

    return dict_document

def get_filtered_user_absences(user_id, teacher_name, classroom):
        """
        Get filtered absences for a user from Firestore based on query parameters.
        """
        user_ref = db.collection('users').document(user_id)
        query = db.collection('absences').where('username', '==', user_ref)

        if teacher_name:
            query = query.where('teacher', '==', teacher_name)
        if classroom:
            query = query.where('classroom', '==', classroom)

        absences_query = query.get()
        absences = [convert_document_to_dict(absence) for absence in absences_query]
        return absences

def get_user_absences(user_id):
        """
        Get absences for a user from Firestore.
        """
        user_ref = db.collection('users').document(user_id)
        absences_query = db.collection('absences').where('username', '==', user_ref).get()
        absences = [convert_document_to_dict(absence) for absence in absences_query]
        return absences