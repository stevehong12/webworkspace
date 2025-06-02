from dataclasses import dataclass, field
from typing import Set, Tuple, List, Optional, Deque
from collections import deque

from dir import Dir  # 방향 enum
from world import World, SAFE_STARTS  # World 클래스와 상수

@dataclass
class AgentBase:
    world: World
    x: int = 1
    y: int = 1
    dir: Dir = Dir.E
    arrows: int = 3
    has_gold: bool = False
    performance: int = 0 #초기 상태 설정

    visited: Set[Tuple[int, int]] = field(default_factory=set)
    safe: Set[Tuple[int, int]] = field(default_factory=lambda: {(1, 1), (1, 2), (2, 1)})
    definite_pit: Set[Tuple[int, int]] = field(default_factory=set)
    definite_wumpus: Set[Tuple[int, int]] = field(default_factory=set)

    #위험 요소 타일들
    stench_dirs: Set[Dir] = field(default_factory=set)
    breeze_cells: List[Tuple[int, int]] = field(default_factory=list)

    initial_wait: bool = True # 초기행동 조정
    pending_shot: Optional[Dir] = None#..?
    prev: Tuple[int, int] = (1, 1) #이전 위치 좌표 저장
    #시작 영역에서 방문할 목표 위치를 순서대로 관리하는 큐
    start_targets: Deque[Tuple[int, int]] = field(default_factory=lambda: deque([(2, 1), (1, 2)]))
    #과거 행동에 대한 기억
    history: List[dict] = field(default_factory=list)
