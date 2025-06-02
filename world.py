import random, time
from dataclasses import dataclass, field
from typing import Set, Tuple, Optional, List, Dict
from dir import Dir
from percept import Percept

WALL, PIT, WUMPUS, GOLD, EMPTY = "W", "P", "U", "G", "."
SAFE_STARTS = {(1, 1)}

@dataclass
class World:
    seed: Optional[int] = None
    size: int = field(init=False, default=6)
    pits: Set[Tuple[int, int]] = field(init=False, default_factory=set)
    wumpi: Set[Tuple[int, int]] = field(init=False, default_factory=set)
    gold: Tuple[int, int] = field(init=False)
    tile_state: List[List[Dict[str, int | bool]]] = field(init=False)
    wumpus_alive: bool = field(init=False, default=True)

    def __post_init__(self):# 수정한 부분 난수를 이용해서 시드 생성
        if self.seed is not None:
            random.seed(self.seed)
        else:
            random.seed()

        self._generate()
        self.print_map()

    def _generate(self):
        self.grid = [[WALL] * self.size for _ in range(self.size)]#맵 생성 모든 칸을 벽으로
        for y in range(1, 5):
            for x in range(1, 5):
                self.grid[y][x] = EMPTY#내부는 비게 만들기
        for x in range(1, 5):
            for y in range(1, 5):
                if (x, y) in SAFE_STARTS:#안전한 칸들에 대해서는 몬스터와 구덩이 안 넣기
                    continue
                if random.random() < 0.1 and len(self.wumpi) < 2: # 0.1 확률로 몬스터와 구멍 추가 2개 이상 되지 않도록
                    self.wumpi.add((x, y))
                if random.random() < 0.1 and len(self.pits) < 2:
                    self.pits.add((x, y))
        self.gold = random.choice([(x, y) for x in range(1, 5) for y in range(1, 5) if (x, y) not in SAFE_STARTS])#금 생성 위치는 시작위치를 제외 4*4 안에서 생성
        self.tile_state = [[{'stench': 0, 'breeze': 0, 'pit': (x, y) in self.pits, 'wumpus': (x, y) in self.wumpi, 'gold': (x, y) == self.gold} for x in range(self.size)] for y in range(self.size)] #각 칸의 상태를 저장

        for wx, wy in self.wumpi:
            for d in Dir:#상하좌우 칸들의 값에 대해서 s값
                ax, ay = wx + d.dx, wy + d.dy
                if 1 <= ax <= 4 and 1 <= ay <= 4:
                    self.tile_state[ay][ax]['stench'] += 1#(ax, ay)가 지도 안에 있을 때만, 그 칸에 냄새 표시를 하나 더 추가
        for px, py in self.pits:
            for d in Dir:
                ax, ay = px + d.dx, py + d.dy
                if 1 <= ax <= 4 and 1 <= ay <= 4:
                    self.tile_state[ay][ax]['breeze'] += 1

    def get_percept(self, x, y):
        ts = self.tile_state[y][x]#냄새 바람 금 유무를 저장
        return Percept(ts['stench'] > 0, ts['breeze'] > 0, ts['gold'])

    def forward(self, x, y, d):
        nx, ny = x + d.dx, y + d.dy#앞으로 한 칸
        if self.grid[ny][nx] == WALL:# wall이라면 다음 칸이 벽인지 저장
            p = self.get_percept(x, y)
            p.bump = True
            return x, y, p
        return nx, ny, self.get_percept(nx, ny)

    def shoot(self, x, y, d):#화살을 쏴서
        cx, cy = x + d.dx, y + d.dy
        while self.grid[cy][cx] != WALL:# 벽을 만나기 전까지 쭉 간다
            if (cx, cy) in self.wumpi and self.wumpus_alive:
                self.wumpus_alive = False#살아 있는 상태라면 죽음으로 표시
                self.wumpi.remove((cx, cy))
                return True
            cx += d.dx
            cy += d.dy
        return False

    def print_map(self, agent_x=None, agent_y=None, agent_dir=None):
        print("Map (W: Wall, P: Pit, U: Wumpus, G: Gold, .: Empty)")

        size = 6
        dir_symbols = {
            'N': '↑',
            'E': '→',
            'S': '↓',
            'W': '←',
        }

        print("   " + " ".join(f"{x:2}" for x in range(size)))

        for y in range(size):
            row = f"{y:2} "
            for x in range(size):
                if (x, y) == (agent_x, agent_y) and agent_dir in dir_symbols:
                    row += dir_symbols[agent_dir] + "  "
                elif self.grid[y][x] == WALL:
                    row += "W  "
                elif (x, y) == self.gold:
                    row += "G  "
                elif (x, y) in self.wumpi:
                    row += "U  "
                elif (x, y) in self.pits:
                    row += "P  "
                else:
                    row += ".  "
            print(row)

    def tile_has_pit(self, x, y): return (x, y) in self.pits #구덩이가 있는지? 괴물이 있는지?
    def tile_has_live_wumpus(self, x, y): return (x, y) in self.wumpi and self.wumpus_alive
