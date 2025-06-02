from .agent_base import AgentBase
from world import Percept  # Percept 타입 임포트

class AgentLogging(AgentBase):
    def _log(self, step: int, act: str, p: Percept):
        self.history.append(
            dict(step=step, act=act, pos=(self.x, self.y), dir=self.dir.name, percept=repr(p))
        )

    def print_history(self):
        print("\n===== Trace =====")
        for h in self.history:
            print(
                f"{h['step']:03d} | {h['act']:<12} | Pos{h['pos']} | "
                f"Dir {h['dir']:<5} | {h['percept']}"
            )
        print("=================")
