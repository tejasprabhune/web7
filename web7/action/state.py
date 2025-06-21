from dataclasses import dataclass


@dataclass
class Step:
    prompt: str


@dataclass
class Action: ...


class ActionDag:
    plan: list[Step]
    nodes: list[Action]


@dataclass
class State:
    action_dag: ActionDag


if __name__ == "__main__":
    pass
