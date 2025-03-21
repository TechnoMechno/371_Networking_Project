class Player:
    def __init__(self, name):
        self.name = name
        self.score = 0

    def grab_cookie(self, cookie):
        # Award points based on cookie type
        if cookie.type == "star":
            self.score += 2
        else:
            self.score += 1