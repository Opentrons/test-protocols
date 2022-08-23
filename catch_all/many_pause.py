"""Pause counter example."""
import itertools
from dataclasses import dataclass

from opentrons import protocol_api

metadata = {
    "protocolName": "Pause Counter",
    "author": "Opentrons <protocols@opentrons.com>",
    "source": "Example",
    "apiLevel": "2.12",
}


@dataclass
class Counter:
    """Count things during a run."""

    pauses: int

    def increment_pauses(self) -> int:
        """Increment pauses."""
        self.pauses += 1
        return self.pauses


def run(ctx: protocol_api.ProtocolContext) -> None:
    """This method is run by the protocol engine."""
    counter = Counter(pauses=0)

    # Remember about the pause function from the docs
    # https://docs.opentrons.com/v2/new_atomic_commands.html#pause-until-resumed
    # This function returns immediately, but the next function call that
    # is blocked by a paused robot (anything that involves moving) will
    # not return until the protocol is resumed.

    # increment the count of pauses inline with the pause
    ctx.pause(f"This is pause {counter.increment_pauses()}")
    ctx.home()
    # use the current count of pauses
    ctx.comment(f"My comment about pause {counter.pauses}")
    # increment before the pause
    counter.increment_pauses()
    ctx.pause(f"This is pause {counter.pauses}")
    ctx.home()
    ctx.comment(f"My comment about pause {counter.pauses}")
