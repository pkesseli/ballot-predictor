from bp.train.bert import VoteResultPredictionModel


from keras import Model
from typing import List
import aiofiles
import asyncio
import tensorflow_model_optimization as tfmot
import tensorflow as tf
import os


async def main():
    """Helper script to export persisted models generated using bp.train.train
    in stripped and quantized `.tflite` format. The intent is to export the
    model in a format optimised for size and to be loaded in tensorflowjs.
    Excluded from unit test coverage check, since this script is only executed
    manually during experiments.
    """
    models: List[VoteResultPredictionModel] = [VoteResultPredictionModel.create_popular_majority_model(
    ), VoteResultPredictionModel.create_canton_majority_model()]
    for model in models:
        stripped_model: Model = tfmot.sparsity.keras.strip_pruning(model.model)
        converter: tf.lite.TFLiteConverter = tf.lite.TFLiteConverter.from_keras_model(
            stripped_model)
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        minimised_model: Model = converter.convert()

        module_location: str = os.path.dirname(__file__)
        js_dir: str = os.path.join(
            module_location, f"../resources/js/{model.name}.tflite")
        async with aiofiles.open(js_dir, "wb") as persisted_model:
            await persisted_model.write(minimised_model)
        break


if __name__ == "__main__":
    asyncio.run(main())
