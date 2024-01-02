from bp.data.serialisation import Serialisation
from bp.entity.ballot import DoubleMajorityBallot
from bp.train.bert import VoteResultPredictionModel

import tensorflow as tf
from tensorflow import Tensor
from typing import List
import asyncio


async def main():
    """Helper script to train our vote result rediction model. The model is
    based on a multilingual BERT base model, extended by an input layer
    suitable for consuming our tokenized bills and an ouput layer producing the
    predicted vote results. Excluded from unit test coverage check, since this
    script is only executed manually during experimental and training
    preparations.
    """
    bert = VoteResultPredictionModel()

    ballots: List[DoubleMajorityBallot] = await Serialisation.load_augmented_initiatives()
    features: Tensor = bert.create_bill_features(
        [ballot.bill for ballot in ballots])
    labels: Tensor = bert.create_double_majority_labels(
        [ballot.result for ballot in ballots])
    training_dataset: tf.data.Dataset = tf.data.Dataset.from_tensor_slices(
        (features, labels))
    bert.train(training_dataset)


if __name__ == "__main__":
    asyncio.run(main())
