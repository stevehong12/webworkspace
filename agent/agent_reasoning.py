from typing import Optional
from .agent_navigation import AgentNavigation
from world import Percept,SAFE_STARTS
from dir import Dir

class AgentReasoning(AgentNavigation):
    def _update(self, p: Percept):
        self.visited.add((self.x, self.y))#방문 처리

        if not p.stench and not p.breeze:
            for d in Dir:
                ax, ay = self.x + d.dx, self.y + d.dy
                if 1 <= ax <= 4 and 1 <= ay <= 4:
                    self.safe.add((ax, ay))

        if p.stench:
            for d in Dir:
                nx, ny = self.x + d.dx, self.y + d.dy
                if 1 <= nx <= 4 and 1 <= ny <= 4:
                    self.stench_dirs.add(d)

        if p.breeze:
            self.breeze_cells.append((self.x, self.y))
            if len(self.breeze_cells) >= 2:
                inter = set.intersection(
                    *[
                        {
                            (bx + d.dx, by + d.dy)
                            for d in Dir
                            if 1 <= bx + d.dx <= 4 and 1 <= by + d.dy <= 4
                        }
                        for bx, by in self.breeze_cells
                    ]
                )
                for pt in inter:
                    if pt not in SAFE_STARTS:
                        self.definite_pit.add(pt)
                        self.safe.discard(pt)

        if p.scream:
            self.stench_dirs.clear()
            self.pending_shot = None

    def _decide(self, p: Percept) -> str:
        if self.initial_wait:
            self.initial_wait = False
            return "TurnLeft"

        if (self.x, self.y) == (1, 1) and p.breeze and self.start_targets:
            return self._plan(self.start_targets.popleft())

        if p.glitter:
            return "Grab"

        if self.has_gold:
            return "Climb" if (self.x, self.y) == (1, 1) else self._plan((1, 1))

        if p.breeze:
            if self.prev not in self.definite_pit | self.definite_wumpus and self.prev != (self.x, self.y):
                return self._plan(self.prev)
            return self._plan(self._nearest_safe())

        if p.stench and self.arrows > 0 and self.stench_dirs:
            if self.pending_shot is None:
                self.pending_shot = sorted(self.stench_dirs, key=lambda d: d.value)[0]
            return "Shoot"

        return self._plan(self._nearest_safe())

    def step(self, step: int) -> bool:
        p = self.world.get_percept(self.x, self.y)
        self._update(p)
        act = self._decide(p)

        if act == "Forward":
            self.x, self.y, newp = self.world.forward(self.x, self.y, self.dir)
            p |= newp
        elif act == "TurnLeft":
            self.dir = self.dir.left()
        elif act == "TurnRight":
            self.dir = self.dir.right()
        elif act == "Grab":
            self.has_gold = True
            self.performance += 100
            self.world.tile_state[self.y][self.x]["gold"] = False
        elif act == "Shoot" and self.pending_shot is not None:
            d = self.pending_shot
            self.pending_shot = None
            self.arrows -= 1
            p.scream = self.world.shoot(self.x, self.y, d)
            self.performance += 10 if p.scream else 0
            self.stench_dirs.discard(d)
        elif act == "Climb":
            self.performance += 1000
            self._log(step, act, p)
            return False

        dead = self.world.tile_has_pit(self.x, self.y) or self.world.tile_has_live_wumpus(self.x, self.y)
        if dead:
            self.performance -= 1000
            if self.world.tile_has_pit(self.x, self.y):
                self.definite_pit.add((self.x, self.y))
                self.safe.discard((self.x, self.y))
            if self.world.tile_has_live_wumpus(self.x, self.y):
                self.definite_wumpus.add((self.x, self.y))
                self.safe.discard((self.x, self.y))

        self._log(step, act if not dead else act + "(DEAD)", p)
        self.prev = (self.x, self.y)
        return not dead

    def reset_position(self):
        self.x, self.y, self.dir = 1, 1, Dir.E
        self.arrows = 3
        self.has_gold = False
        self.initial_wait = True
        self.pending_shot = None
        self.prev = (1, 1)
