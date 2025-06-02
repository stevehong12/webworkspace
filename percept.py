from dataclasses import dataclass

@dataclass
class Percept:
    stench: bool = False
    breeze: bool = False
    glitter: bool = False
    bump: bool = False
    scream: bool = False

    def __ior__(self, o: "Percept"):
        self.stench |= o.stench
        self.breeze |= o.breeze
        self.glitter |= o.glitter
        self.bump |= o.bump
        self.scream |= o.scream
        return self
    #감각을 합치는 역할

    def __repr__(self):
        return f"S:{int(self.stench)} B:{int(self.breeze)} G:{int(self.glitter)} Bu:{int(self.bump)} Sc:{int(self.scream)}"
