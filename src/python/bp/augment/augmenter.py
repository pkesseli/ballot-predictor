from bp.augment.bill import BillAugmenter
from bp.augment.chat import CachedChat
from bp.augment.openai import ChatGpt
from bp.augment.seed import DEFAULT_SEED
from bp.data.serialisation import BallotStatusHandler, DatetimeHandler, DecimalHandler, DoubleMajorityBallotResultHandler
from bp.entity.ballot import BallotStatus, DoubleMajorityBallot, DoubleMajorityBallotResult
from dotenv import load_dotenv

import aiofiles
import asyncio
import jsonpickle
from datetime import datetime
from decimal import Decimal
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
    jsonpickle.handlers.registry.register(BallotStatus, BallotStatusHandler)
    jsonpickle.handlers.registry.register(datetime, DatetimeHandler)
    jsonpickle.handlers.registry.register(Decimal, DecimalHandler)
    jsonpickle.handlers.registry.register(
        DoubleMajorityBallotResult, DoubleMajorityBallotResultHandler)
    jsonpickle.set_decoder_options("json", strict=False)
    jsonpickle.set_encoder_options("json", sort_keys=True, indent=4)
    serialised: str
    async with aiofiles.open("bp/resources/bk.admin.ch/initiatives.json") as file:
        serialised = await file.read()

    ballots: List[DoubleMajorityBallot] = jsonpickle.decode(serialised)
    ballots_with_result: List[DoubleMajorityBallot] = [
        ballot for ballot in ballots if ballot.result is not None]

    augmented_ballots: List[DoubleMajorityBallot] = []
    chat = ChatGpt()
    async with CachedChat(chat) as cached_chat:
        bill_augmenter = BillAugmenter(
            cached_chat, default_rng(DEFAULT_SEED), 5)
        for ballot in ballots_with_result:
            augmented_ballots.extend(
                bill_augmenter.paraphrase_and_contradict([ballot]))
            break

    serialised = jsonpickle.encode(augmented_ballots)
    async with aiofiles.open("bp/resources/bk.admin.ch/augmented-initiatives.json", "w") as file:
        await file.write(serialised)


if __name__ == "__main__":
    asyncio.run(main())
