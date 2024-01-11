class FirestoreUser:
    def __init__(self, user_data):
        self.user_data = user_data

    @property
    def is_authenticated(self):
        return True