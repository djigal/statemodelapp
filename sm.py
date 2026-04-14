from dataclasses import dataclass, field
from typing import Callable
from enum import Enum

class InvalidTransition(Exception):
    pass

type Action[C] = Callable[[C], None]

@dataclass
class StateMachine[S: Enum, E: Enum, C]:
    """Common interface for all state machines."""

    transitions: dict[tuple[S, E], tuple[S, Action[C]]] = field(
        default_factory=dict[tuple[S, E], tuple[S, Action[C]]]
    )
    
    def add_transition(self, from_state: S, event: E, to_state: S, func: Action[C]) -> None:
        self.transitions[(from_state, event)] = (to_state, func)

    def next_transition(self, state: S, event: E) -> tuple[S, Action[C]]:
        try:
            return self.transitions[(state, event)]
        except KeyError as e:
            raise InvalidTransition(f"can't {event.name} when {state.name}") from e

    def handle(self, state: S, event: E, ctx: C) -> S:
        next_state, action = self.next_transition(state, event)
        action(ctx)
        return next_state