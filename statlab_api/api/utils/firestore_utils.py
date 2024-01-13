from collections import defaultdict
import datetime
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

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

def query_absences(user_id, teacher_name=None, classroom=None, subjectType=None, subject=None, justification=None):
    """
    Query absences for a user, optionally filtered by teacher name, classroom, subject type, subject and justification.
    """
    try:
        user_ref = db.collection('users').document(user_id)
        query = db.collection('absences').where(filter=FieldFilter('username', '==', user_ref))

        if teacher_name:
            query = query.where(filter=FieldFilter('teacher', '==', teacher_name))
        if classroom:
            query = query.where(filter=FieldFilter('classroom', '==', classroom))
        if subjectType:
            query = query.where(filter=FieldFilter('subjectType', '==', "/subject_type/"+subjectType))
        if subject:
            query = query.where(filter=FieldFilter('subject', '==', subject))
        if justification:
            query = query.where(filter=FieldFilter('justification', '!=' if justification == 'true' else '==', "Aucun"))

        absences_query = query.get()
        return [convert_document_to_dict(absence) for absence in absences_query if absence.exists]
    except Exception as e:
        print(f"Error querying absences: {e}")
        return []
    
def get_top_10_users_with_most_absences_from_firestore():
    """
    Retrieve the top 10 users with the highest number of absences from Firestore.
    """
    try:
        absences_count = defaultdict(int)
        absences = db.collection('absences').stream()

        for absence in absences:
            user_ref = absence.to_dict().get('username')
            if user_ref:
                absences_count[user_ref.id] += 1

        top_10_user_ids = sorted(absences_count, key=absences_count.get, reverse=True)[:10]

        return [
            db.collection('users').document(user_id).get().to_dict().get('username')
            for user_id in top_10_user_ids
            if db.collection('users').document(user_id).get().exists
        ]
    except Exception as e:
        print(f"Error retrieving top 10 users with most absences: {e}")


def get_top_10_users_with_most_absences_by_teacher_from_firestore(teacher_name):
    """
    Retrieve the top 10 users with the highest number of absences by teacher from Firestore.
    """
    try:
        absences_count = defaultdict(int)
        absences = db.collection('absences').where(filter=FieldFilter('teacher', '==', teacher_name)).stream()

        for absence in absences:
            user_ref = absence.to_dict().get('username')
            if user_ref:
                absences_count[user_ref.id] += 1

        top_10_user_ids = sorted(absences_count, key=absences_count.get, reverse=True)[:10]

        return [
            db.collection('users').document(user_id).get().to_dict().get('username')
            for user_id in top_10_user_ids
            if db.collection('users').document(user_id).get().exists
        ]
    except Exception as e:
        print(f"Error retrieving top 10 users with most absences by teacher: {e}")


def get_top_10_users_with_most_absences_by_classroom_from_firestore(classroom):
    """
    Retrieve the top 10 users with the highest number of absences by classroom from Firestore.
    """
    try:
        absences_count = defaultdict(int)
        absences = db.collection('absences').where(filter=FieldFilter('classroom', '==', classroom)).stream()

        for absence in absences:
            user_ref = absence.to_dict().get('username')
            if user_ref:
                absences_count[user_ref.id] += 1

        top_10_user_ids = sorted(absences_count, key=absences_count.get, reverse=True)[:10]

        return [
            db.collection('users').document(user_id).get().to_dict().get('username')
            for user_id in top_10_user_ids
            if db.collection('users').document(user_id).get().exists
        ]
    except Exception as e:
        print(f"Error retrieving top 10 users with most absences by classroom: {e}")


def get_top_10_users_with_most_absences_by_subject_from_firestore(subject):
    """
    Retrieve the top 10 users with the highest number of absences by subject from Firestore.
    """
    try:
        absences_count = defaultdict(int)
        absences = db.collection('absences').where(filter=FieldFilter('subject', '==', subject)).stream()

        for absence in absences:
            user_ref = absence.to_dict().get('username')
            if user_ref:
                absences_count[user_ref.id] += 1

        top_10_user_ids = sorted(absences_count, key=absences_count.get, reverse=True)[:10]

        return [
            db.collection('users').document(user_id).get().to_dict().get('username')
            for user_id in top_10_user_ids
            if db.collection('users').document(user_id).get().exists
        ]
    except Exception as e:
        print(f"Error retrieving top 10 users with most absences by subject: {e}")



# Renaming functions for backwards compatibility
get_user_absences = query_absences
get_filtered_user_absences = query_absences
