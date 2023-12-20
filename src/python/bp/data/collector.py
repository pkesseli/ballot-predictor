from bp.data.chronology import Chronology
from bp.data.serialisation import BallotStatusHandler, DatetimeHandler
from bp.entity.ballot import BallotStatus, DoubleMajorityBallot

import jsonpickle
from datetime import datetime
from typing import List


def main():
    """Helper script to download all training data from www.bk.admin.ch.
    Updates src/python/bp/resources with most recent data. Excluded from unit
    test coverage check, since this script is only executed manually during
    experimental and training preparations.
    """
    jsonpickle.handlers.registry.register(datetime, DatetimeHandler)
    jsonpickle.handlers.registry.register(BallotStatus, BallotStatusHandler)
    jsonpickle.set_encoder_options('json', sort_keys=True, indent=4)
    initiatives: List[str] = Chronology.get_initiatives()
    for billDetailsUrl in initiatives:
        ballot: DoubleMajorityBallot = Chronology.get_initiative(
            billDetailsUrl)
        serialised = jsonpickle.encode(ballot)
        with open("bp/resources/initiatives.json", "w+") as file:
            file.write(serialised)
        break


if __name__ == "__main__":
    main()
