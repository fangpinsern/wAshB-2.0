
class Session:

    sessions = []

    # Session constuctor
    def __init__(self):
        self.sessions = []

    # Check if the session exists
    def session_exist(self, username):
        exist = False
        for session in self.sessions:
            if session[0] == username:
                exist = True
                break
        return exist

    # Starts a session for the user with the input value

    def start_session(self, username, last_input):
        # check is session exist
        if (not self.session_exist(username)):
            self.sessions.append([username, last_input])

    # Get last input of the user from the session

    def get_last_input(self, username):
        lastInput = ""
        for session in self.sessions:
            if session[0] == username:
                lastInput = session[1]
                break

        return lastInput

    def end_session(self, username):
        index = 0
        for session in self.sessions:
            if session[0] == username:
                self.sessions.pop(index)
                break
            index = index + 1

    def to_string(self):
        str1 = ""

        for session in self.sessions:
            str1 = str1 + session[0] + session[1] + "\n"

        return str1
