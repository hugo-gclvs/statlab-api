import datetime
from firebase_admin import firestore

# Initialize Firestore client
db = firestore.client()

def get_document_details(doc_ref):
    """
    Retrieve details of a document from a Firestore reference.
    """
    if not isinstance(doc_ref, firestore.DocumentReference):
        return doc_ref if doc_ref else None

    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    return None

def convert_document_to_dict(document):
    """
    Converts a Firestore DocumentSnapshot into a dictionary.
    """
    if not document.exists:
        return None

    dict_document = document.to_dict()
    dict_document['id'] = document.id

    # Handling referenced fields
    for field in ['username', 'subjectType']:
        if field in dict_document:
            dict_document[field] = get_document_details(dict_document[field])

    # Convert datetime objects to ISO format
    for key, value in dict_document.items():
        if isinstance(value, datetime.datetime):
            dict_document[key] = value.isoformat()

    return dict_document

def query_absences(user_id, teacher_name=None, classroom=None):
    """
    Query absences for a user, optionally filtered by teacher name and classroom.
    """
    try:
        user_ref = db.collection('users').document(user_id)
        query = db.collection('absences').where('username', '==', user_ref)

        if teacher_name:
            query = query.where('teacher', '==', teacher_name)
        if classroom:
            query = query.where('classroom', '==', classroom)

        absences_query = query.get()
        return [convert_document_to_dict(absence) for absence in absences_query if absence.exists]
    except Exception as e:
        print(f"Error querying absences: {e}")
        return []

# Renaming functions for backwards compatibility
get_user_absences = query_absences
get_filtered_user_absences = query_absences
