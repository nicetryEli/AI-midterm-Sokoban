class Board:
    def __init__(self, walls, goals):
        self.walls = frozenset(walls)
        self.goals = frozenset(goals)