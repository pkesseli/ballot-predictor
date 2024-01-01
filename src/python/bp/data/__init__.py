from bp.entity.ballot import BallotStatus, Bill, DoubleMajorityBallot, DoubleMajorityBallotResult
from bp.data.serialisation import BallotStatusHandler, BillHandler, DatetimeHandler, DecimalHandler, DoubleMajorityBallotHandler, DoubleMajorityBallotResultHandler

import jsonpickle
from datetime import datetime
from decimal import Decimal

jsonpickle.handlers.registry.register(BallotStatus, BallotStatusHandler)
jsonpickle.handlers.registry.register(Bill, BillHandler)
jsonpickle.handlers.registry.register(datetime, DatetimeHandler)
jsonpickle.handlers.registry.register(Decimal, DecimalHandler)
jsonpickle.handlers.registry.register(
    DoubleMajorityBallot, DoubleMajorityBallotHandler)
jsonpickle.handlers.registry.register(
    DoubleMajorityBallotResult, DoubleMajorityBallotResultHandler)
jsonpickle.set_decoder_options("json", strict=False)
jsonpickle.set_encoder_options("json", sort_keys=True, indent=4)
