from bp.augment.bill import BillAugmenter
from bp.augment.chat import CachedChat
from bp.augment.openai import ChatGpt
from bp.augment.seed import DEFAULT_SEED
from bp.data.serialisation import Serialisation
from bp.entity.ballot import DoubleMajorityBallot
from dotenv import load_dotenv

import asyncio
from numpy.random import default_rng
from typing import List


async def main():
    """Helper script to augment training data from www.bk.admin.ch. Uses prompt
    engineering on GPT as an off-the-shelf chat model to paraphrase bills and
    generate bills with opposite meaning. Excluded from unit test coverage
    check, since this script is only executed manually during experimental and
    training preparations.
    """
    load_dotenv()

    ballots: List[DoubleMajorityBallot] = await Serialisation.load_initiatives()
    ballots_with_result: List[DoubleMajorityBallot] = [
        ballot for ballot in ballots if ballot.result is not None]

    augmented_ballots: List[DoubleMajorityBallot] = []
    chat = ChatGpt()
    async with CachedChat(chat) as cached_chat:
        bill_augmenter = BillAugmenter(
            cached_chat, default_rng(DEFAULT_SEED), 5)
        count: int = 0
        for ballot in ballots_with_result:
            if count == 0:
                augmented_ballots.extend(
                    bill_augmenter.paraphrase_and_contradict([ballot]))
            else:
                augmented_ballots.append(ballot)

            count = count + 1

    await Serialisation.write_augmented_initiatives(augmented_ballots)


if __name__ == "__main__":
    asyncio.run(main())
