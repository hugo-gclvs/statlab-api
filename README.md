# OGEStatLab API

## Overview
This document outlines the endpoints provided by our OGE API, which is designed for managing and analyzing user absences in an educational setting.

## Authentication

### Login
- **Endpoint**: `POST /login/`
- **Purpose**: Authenticates a user and returns a JWT token along with user info.
- **Request Body Example**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Response Examples**:
  - **200 OK**: 
    ```json
    {
      "tokens": {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX...",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2Vy..."
      },
      "user": {
        "username": "username",
        "first_name": "first_name",
        "last_name": "last_name",
        "specialization": "specialization",
        "study_year": "study_year"
      }
    }
    ```
  - **400 Bad Request**: 
    ```json
    {
      "non_field_errors": [
        "Unable to log in with provided credentials."
      ]
    }
    ```

## User Absences

### User Absences Retrieval
- **Endpoint**: `GET /absences/`
- **Purpose**: Retrieves authenticated user's absences.
- **Headers**: Requires `Authorization` bearer token.
- **Response Examples**:
  - **200 OK**: 
    ```json
    {
      "absences": [
        {
          "id": "absence_id",
          "date": "2021-01-01",
          "teacher": "teacher_name",
          "classroom": "classroom_name",
          "subjectType": "subject_type",
          "subject": "subject_name",
          "justification": "justification",
          "username": "username",
          "start_date": "2023-09-19T10:15:00+00:00",
          "end_date": "2023-09-19T11:15:00+00:00"
        }
      ]
    }
    ```
  - **500 Internal Server Error**: 
    ```json
    {
      "error": "Error message"
    }
    ```

### Filtered User Absences
- **Endpoint**: `GET /absences/filtered/`
- **Purpose**: Returns filtered absences of the user.
- **Parameters**: Optional - `teacher`, `classroom`, `subjectType`, `subject`, `justification`.
- **Headers**: Requires `Authorization` bearer token.
- **Response Examples**:
  - **200 OK**: 
    ```json
    {
      "absences": [
        {
          "id": "absence_id",
          "date": "2021-01-01",
          "teacher": "teacher_name",
          "classroom": "classroom_name",
          "subjectType": "subject_type",
          "subject": "subject_name",
          "justification": "justification",
          "username": "username",
          "start_date": "2023-09-19T10:15:00+00:00",
          "end_date": "2023-09-19T11:15:00+00:00"
        }
      ]
    }
    ```
  - **500 Internal Server Error**: 
    ```json
    {
      "error": "Error message"
    }
    ```

## Top Absence Statistics

### Top Absence Statistics Retrieval
- **Endpoint**: `GET /absence/statistiques/top/`
- **Purpose**: Provides top n users with most absences based on criteria.
- **Parameters**: Required - `type`; Optional - `top_n`, `teacher`, `classroom`, `subject`, `subject_type`, `justification`.
- **Headers**: Requires `Authorization` bearer token.
- **Response Examples**:
  - **200 OK**: 
    ```json
    {
      "top_n_global_ranking": [
        {
          "username": "username",
          "first_name": "first_name",
          "last_name": "last_name",
          "specialization": "specialization",
          "study_year": "study_year",
          "absences_count": 10
        },
        {
          "username": "username2",
          "first_name": "first_name2",
          "last_name": "last_name2",
          "specialization": "specialization2",
          "study_year": "study_year2",
          "absences_count": 4
        }
      ]
    }
    ```
  - **400 Bad Request**: 
    ```json
    {
      "error": "Invalid type"
    }
    ```
  - **500 Internal Server Error**: 
    ```json
    {
      "error": "Error message"
    }
    ```

## All Absence Statistics

### All Absence Statistics Retrieval
- **Endpoint**: `GET /absence/statistiques/all/`
- **Purpose**: Provides the users with absences in a specific type of absences.
- **Parameters**: Required - `type`; Optional - `subject`.
- **Headers**: Requires `Authorization` bearer token.
- **Response Examples**:
  - **200 OK**: 
    ```json
    {
      "users_with_absences_in_specific_subject": [
        {
          "username": "username",
          "first_name": "first_name",
          "last_name": "last_name",
          "specialization": "specialization",
          "study_year": "study_year",
          "absences_count": 10
        },
        {
          "username": "username2",
          "first_name": "first_name2",
          "last_name": "last_name2",
          "specialization": "specialization2",
          "study_year": "study_year2",
          "absences_count": 4
        }
      ]
    }
    ```
  - **400 Bad Request**: 
    ```json
    {
      "error": "Invalid type"
    }
    ```
  - **500 Internal Server Error**: 
    ```json
    {
      "error": "Error message"
    }
    ```

## Additional Information
- **Error Handling**: Each endpoint incorporates error handling for reliability.
- **Security**: Secured with JWT-based authentication.
- **Logging**: Features systematic logging.

## Conclusion

This API is a comprehensive solution for managing and analyzing user absences in l'ESIREM, offering secure and efficient data handling.


## Credit:
* OGE Scraper Service: [MARTINEZ Roméo](https://github.com/Romeo-mz)
