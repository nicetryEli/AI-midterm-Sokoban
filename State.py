class State:
    def __init__(self, player_pos, boxes, g=0):
        self.player_pos = player_pos
        self.boxes = tuple(sorted(boxes))        
        self.g = g

    def __hash__(self):
        return hash((self.player_pos, self.boxes))

    def __eq__(self, other):
        if not isinstance(other, State):
            return False
        return (self.player_pos == other.player_pos and
                self.boxes == other.boxes)

    def __lt__(self, other):
        if self.f == other.f:
            return self.h < other.h
        return self.f < other.f

    def __repr__(self):
        return f"State(player={self.player_pos}, boxes={self.boxes}, f={self.f})"