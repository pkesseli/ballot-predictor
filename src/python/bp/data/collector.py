from bp.data.chronology import Chronology
from bp.data.serialisation import BallotStatusHandler, DatetimeHandler, DecimalHandler
from bp.entity.ballot import BallotStatus, DoubleMajorityBallot

import jsonpickle
from datetime import datetime
from decimal import Decimal
from typing import List


def main():
    """Helper script to download all training data from www.bk.admin.ch.
    Updates src/python/bp/resources with most recent data. Excluded from unit
    test coverage check, since this script is only executed manually during
    experimental and training preparations.
    """
    jsonpickle.handlers.registry.register(BallotStatus, BallotStatusHandler)
    jsonpickle.handlers.registry.register(datetime, DatetimeHandler)
    jsonpickle.handlers.registry.register(Decimal, DecimalHandler)
    jsonpickle.set_encoder_options('json', sort_keys=True, indent=4)
    initiativeUrls: List[str] = Chronology.get_initiatives()
    initiatives: List[DoubleMajorityBallot] = []

    index: int = 1
    count: int = len(initiativeUrls)
    for billDetailsUrl in initiativeUrls:
        print(f"{index}/{count}: {billDetailsUrl}")
        index += 1
        ballot: DoubleMajorityBallot = Chronology.get_initiative(
            billDetailsUrl)
        initiatives.append(ballot)

    serialised = jsonpickle.encode(initiatives)
    serialised += "\n"
    with open("bp/resources/initiatives.json", "w+") as file:
        file.write(serialised)


if __name__ == "__main__":
    main()
