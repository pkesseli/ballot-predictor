from bp.data.chronology import Chronology
from bp.data.serialisation import Serialisation
from bp.entity.ballot import DoubleMajorityBallot

from typing import List


def main():
    """Helper script to download all training data from www.bk.admin.ch.
    Updates src/python/bp/resources with most recent data. Excluded from unit
    test coverage check, since this script is only executed manually during
    experimental and training preparations.
    """
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

    Serialisation.write_initiatives(initiatives)


if __name__ == "__main__":
    main()
