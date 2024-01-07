from bp.data.serialisation import Serialisation
from bp.entity.ballot import DoubleMajorityBallot
from bp.train.bert import VoteResultPredictionModel


from tensorflow import Tensor
from typing import List
import asyncio


async def main():
    """Helper script to train our vote result prediction model using
    resources/bk.admin.ch/augmented-initiatives.json and save it in
    resources/tensorflow/vote-result-prediction.keras. The model is based on a
    multilingual BERT base model, extended by an input layer suitable for
    consuming our tokenized bills and an ouput layer producing the predicted
    vote results. Excluded from unit test coverage check, since this script is
    only executed manually during experiments.
    """
    ballots: List[DoubleMajorityBallot] = await Serialisation.load_augmented_initiatives()
    models: List[VoteResultPredictionModel] = [VoteResultPredictionModel.create_popular_majority_model(
    ), VoteResultPredictionModel.create_canton_majority_model()]
    for model in models:
        features: Tensor = model.create_bill_features(
            [ballot.bill for ballot in ballots])
        labels: Tensor = model.create_double_majority_labels(
            [ballot.result for ballot in ballots])
        model.train(features, labels, epochs=2)
        model.save()


if __name__ == "__main__":
    asyncio.run(main())
