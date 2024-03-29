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

def query_absences(user_id, teacher_name=None, classroom=None, subject_type=None, subject=None, justification=None):
    """
    Query absences for a user with optional filters: teacher_name, classroom, subject_type, subject, and justification.
    """
    try:
        user_ref = db.collection('users').document(user_id)
        query = db.collection('absences').where('username', '==', user_ref)

        filters = {
            'teacher': teacher_name,
            'classroom': classroom,
            'subjectType': f"/subject_type/{subject_type}" if subject_type else None,
            'subject': subject,
            'justification': "Aucun" if justification == 'true' else None
        }

        for field, value in filters.items():
            if value:
                query = query.where(field, '==' if field != 'justification' else '!=', value)

        absences_query = query.get()
        absences = [convert_document_to_dict(absence) for absence in absences_query if absence.exists]

        # Simplify the username field and remove unnecessary fields
        for absence in absences:
            username = absence['username']
            username = { key: value for key, value in username.items() if key == 'username' }
            absence.update(username)

        return absences
    except Exception as e:
        print(f"Error querying absences: {e}")
        return []
    
def get_top_users_with_most_absences_from_firestore(top_n):
    """
    Retrieve the top n users with the highest number of absences from Firestore.
    """
    try:
        absences_count = defaultdict(int)
        absences = db.collection('absences').stream()

        for absence in absences:
            user_ref = absence.to_dict().get('username')
            if user_ref:
                absences_count[user_ref.id] += 1

        top_n_user_ids = sorted(absences_count, key=absences_count.get, reverse=True)[:top_n]

        top_users_with_absences = []
        for user_id in top_n_user_ids:
            user_doc = db.collection('users').document(user_id).get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
                user_data['absences_count'] = absences_count[user_id]
                top_users_with_absences.append(user_data)

        return top_users_with_absences
    except Exception as e:
        print(f"Error retrieving top n users with most absences: {e}")
        return []

def get_top_users_with_most_absences_by_teacher_from_firestore(teacher_name, top_n):
    """
    Retrieve the top n users with the highest number of absences by teacher from Firestore.
    """
    try:
        absences_count = defaultdict(int)
        absences = db.collection('absences').where(filter=FieldFilter('teacher', '==', teacher_name)).stream()

        for absence in absences:
            user_ref = absence.to_dict().get('username')
            if user_ref:
                absences_count[user_ref.id] += 1

        top_n_user_ids = sorted(absences_count, key=absences_count.get, reverse=True)[:top_n]

        return [
            db.collection('users').document(user_id).get().to_dict()
            for user_id in top_n_user_ids
            if db.collection('users').document(user_id).get().exists
        ]
    except Exception as e:
        print(f"Error retrieving top n users with most absences by teacher: {e}")

def get_top_users_with_most_absences_by_classroom_from_firestore(classroom, top_n):
    """
    Retrieve the top n users with the highest number of absences by classroom from Firestore.
    """
    try:
        absences_count = defaultdict(int)
        absences = db.collection('absences').where(filter=FieldFilter('classroom', '==', classroom)).stream()

        for absence in absences:
            user_ref = absence.to_dict().get('username')
            if user_ref:
                absences_count[user_ref.id] += 1

        top_n_user_ids = sorted(absences_count, key=absences_count.get, reverse=True)[:top_n]

        return [
            db.collection('users').document(user_id).get().to_dict()
            for user_id in top_n_user_ids
            if db.collection('users').document(user_id).get().exists
        ]
    except Exception as e:
        print(f"Error retrieving top n users with most absences by classroom: {e}")

def get_top_users_with_most_absences_by_subject_from_firestore(subject, top_n):
    """
    Retrieve the top n users with the highest number of absences by subject from Firestore.
    """
    try:
        absences_count = defaultdict(int)
        absences = db.collection('absences').where(filter=FieldFilter('subject', '==', subject)).stream()

        for absence in absences:
            user_ref = absence.to_dict().get('username')
            if user_ref:
                absences_count[user_ref.id] += 1

        top_n_user_ids = sorted(absences_count, key=absences_count.get, reverse=True)[:top_n]

        return [
            db.collection('users').document(user_id).get().to_dict()
            for user_id in top_n_user_ids
            if db.collection('users').document(user_id).get().exists
        ]
    except Exception as e:
        print(f"Error retrieving top n users with most absences by subject: {e}")

def get_top_users_with_most_absences_by_subject_type_from_firestore(subject_type, top_n):
    """
    Retrieve the top n users with the highest number of absences by subject type from Firestore.
    """
    try:
        absences_count = defaultdict(int)
        absences = db.collection('absences').where(filter=FieldFilter('subjectType', '==', "/subject_type/"+subject_type)).stream()

        for absence in absences:
            user_ref = absence.to_dict().get('username')
            if user_ref:
                absences_count[user_ref.id] += 1

        top_n_user_ids = sorted(absences_count, key=absences_count.get, reverse=True)[:top_n]

        return [
            db.collection('users').document(user_id).get().to_dict()
            for user_id in top_n_user_ids
            if db.collection('users').document(user_id).get().exists
        ]
    except Exception as e:
        print(f"Error retrieving top n users with most absences by subject type: {e}")

def get_top_users_with_most_absences_by_justification_from_firestore(justification, top_n):
    """
    Retrieve the top n users with the highest number of absences by justification from Firestore.
    """
    try:
        absences_count = defaultdict(int)
        absences = db.collection('absences').where(filter=FieldFilter('justification', '!=' if justification == 'true' else '==', "Aucun")).stream()

        for absence in absences:
            user_ref = absence.to_dict().get('username')
            if user_ref:
                absences_count[user_ref.id] += 1

        top_n_user_ids = sorted(absences_count, key=absences_count.get, reverse=True)[:top_n]

        return [
            db.collection('users').document(user_id).get().to_dict()
            for user_id in top_n_user_ids
            if db.collection('users').document(user_id).get().exists
        ]
    except Exception as e:
        print(f"Error retrieving top n users with most absences by justification: {e}")


def get_all_users_by_subject_absences_from_firestore(subject):
    """
    Retrieve all users with absences by subject from Firestore.
    """
    try:
        absences_count = defaultdict(int)
        absences = db.collection('absences').where(filter=FieldFilter('subject', '==', subject)).stream()

        # count absences for each user by subject and add to the users returned

        for absence in absences:
            user_ref = absence.to_dict().get('username')
            if user_ref:
                absences_count[user_ref.id] += 1

        # return all users with absences by subject and the number of absences
        return [
            {**db.collection('users').document(user_id).get().to_dict(), 'absences_count': absences_count[user_id]}
            for user_id in absences_count
            if db.collection('users').document(user_id).get().exists
        ]

    
    except Exception as e:
        print(f"Error retrieving all users with absences by subject: {e}")

def get_all_users_by_classroom_absences_from_firestore(classroom):
    """
    Retrieve all users with absences by classroom from Firestore.
    """
    try:
        absences_count = defaultdict(int)
        absences = db.collection('absences').where(filter=FieldFilter('classroom', '==', classroom)).stream()

        # count absences for each user by classroom and add to the users returned
        for absence in absences:
            user_ref = absence.to_dict().get('username')
            if user_ref:
                absences_count[user_ref.id] += 1

        # return all users with absences by classroom and the number of absences
        return [
            {**db.collection('users').document(user_id).get().to_dict(), 'absences_count': absences_count[user_id]}
            for user_id in absences_count
            if db.collection('users').document(user_id).get().exists
        ]
    except Exception as e:
        print(f"Error retrieving all users with absences by classroom: {e}")

def get_all_users_by_subject_type_absences_from_firestore(subject_type):
    """
    Retrieve all users with absences by subject type from Firestore.
    """
    try:
        absences_count = defaultdict(int)
        absences = db.collection('absences').where(filter=FieldFilter('subjectType', '==', "/subject_type/"+subject_type)).stream()

        # count absences for each user by subject type and add to the users returned
        for absence in absences:
            user_ref = absence.to_dict().get('username')
            if user_ref:
                absences_count[user_ref.id] += 1

        # return all users with absences by subject type and the number of absences
        return [
            {**db.collection('users').document(user_id).get().to_dict(), 'absences_count': absences_count[user_id]}
            for user_id in absences_count
            if db.collection('users').document(user_id).get().exists
        ]
    except Exception as e:
        print(f"Error retrieving all users with absences by subject type: {e}")

def get_all_users_by_teacher_absences_from_firestore(teacher_name):
    """
    Retrieve all users with absences by teacher from Firestore.
    """
    try:
        absences_count = defaultdict(int)
        absences = db.collection('absences').where(filter=FieldFilter('teacher', '==', teacher_name)).stream()

        # count absences for each user by teacher and add to the users returned
        for absence in absences:
            user_ref = absence.to_dict().get('username')
            if user_ref:
                absences_count[user_ref.id] += 1

        # return all users with absences by teacher and the number of absences
        return [
            {**db.collection('users').document(user_id).get().to_dict(), 'absences_count': absences_count[user_id]}
            for user_id in absences_count
            if db.collection('users').document(user_id).get().exists
        ]
    except Exception as e:
        print(f"Error retrieving all users with absences by teacher: {e}")

# Renaming functions for backwards compatibility
get_user_absences = query_absences
get_filtered_user_absences = query_absences
