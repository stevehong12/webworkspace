from typing import Optional
from world import World
from agent import Agent
import time

def main(seed: Optional[int] = None, limit: int = 120):
    """게임을 한 번 실행한다."""
    world = World(seed=seed)
    agent = Agent(world)
    deaths = 0

    for step in range(1, limit + 1):
        alive = agent.step(step)

        if alive:
            # 금을 갖고 (1,1)에 도착하면 즉시 승리
            if agent.has_gold and (agent.x, agent.y) == (1, 1):
                break
        else:
            deaths += 1
            agent.reset_position()          # 사망 → 리스폰

    # 결과 출력
    agent.print_history()
    status = "성공" if agent.has_gold and (agent.x, agent.y) == (1, 1) else "실패"

    print(f"\n총 이동  : {len(agent.history)}")
    print(f"죽은 횟수: {deaths}")
    print(f"최종 결과: {status}")
    print(f"점수     : {agent.performance}")

if __name__ == "__main__":
    main()
