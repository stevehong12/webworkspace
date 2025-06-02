from typing import Optional, Tuple
from collections import deque

from .agent_logging import AgentLogging
from dir import Dir
from world import SAFE_STARTS

class AgentNavigation(AgentLogging):
    def _best_unknown(self) -> Optional[Tuple[int, int]]:#아직 방문하지 않았고, 안전하지도 않고, 위험한 구덩이나 웜퍼스도 아닌 미지의 칸 중에서 가장 이동하기 좋은 칸
        best, score = None, -1.0
        for x in range(1, 5):
            for y in range(1, 5):
                pos = (x, y)
                if (
                    pos in self.visited
                    or pos in self.safe
                    or pos in self.definite_pit
                    or pos in self.definite_wumpus
                ):
                    continue
                    '''이미 방문했거나 안전한 칸, 확실한 구덩이나 웜퍼스 칸은 건너뜀
                        그 칸 주변(상하좌우 4칸) 중 안전한 칸 비율(safe_ratio)을 계산
                        그 칸 주변에 바람(breeze) 칸이 인접해 있으면 점수에 0.5 추가'''
                adj = [(x + d.dx, y + d.dy) for d in Dir]
                safe_ratio = sum(1 for a in adj if a in self.safe) / 4
                near_breeze = any(abs(x - bx) + abs(y - by) == 1 for bx, by in self.breeze_cells)
                s = safe_ratio + (0.5 if near_breeze else 0)
                if s > score:
                    score, best = s, pos
        return best

    def _nearest_safe(self) -> Optional[Tuple[int, int]]:#현재 위치에서 가장 가까운 (맨해튼 거리 기준) 안전한 칸 중 방문하지 않은 칸
        for pos in sorted(
            self.safe, key=lambda t: abs(t[0] - self.x) + abs(t[1] - self.y)
        ):
            if pos not in self.visited and pos != (self.x, self.y):
                return pos
        return None

    def _move(self, tgt: Optional[Tuple[int, int]]) -> str:
        if tgt is None:
            return "TurnLeft"
        if tgt != (1, 1) and (tgt in self.definite_pit or tgt in self.definite_wumpus):
            return "TurnLeft"
        if (self.x + self.dir.dx, self.y + self.dir.dy) == tgt:
            return "Forward"

        dx, dy = tgt[0] - self.x, tgt[1] - self.y
        desired = (
            Dir.E
            if dx > 0
            else Dir.W
            if dx < 0
            else Dir.N
            if dy > 0
            else Dir.S
        )
        if self.dir == desired:
            return "Forward"
        order = [Dir.N, Dir.E, Dir.S, Dir.W]
        return (
            "TurnRight"
            if (order.index(desired) - order.index(self.dir)) % 4 == 1
            else "TurnLeft"
        )

    def _plan(self, tgt: Optional[Tuple[int, int]]) -> str:
        if tgt and tgt != (self.x, self.y):
            return self._move(tgt)
        alt = self._nearest_safe()
        if alt:
            return self._move(alt)
        unk = self._best_unknown()
        return self._move(unk)
