from bp.train.bert import VoteResultPredictionModel


from keras import Model
from pathlib import Path
from zipfile import ZIP_LZMA, ZipFile
import tensorflow_model_optimization as tfmot
import tensorflow as tf
import os


def main():
    """Helper script to export persisted model generated using bp.train.train
    in stripped and quantized `.tflite` format. The intent is to export the
    model in a format optimised for size and to be loaded in tensorflowjs.
    Excluded from unit test coverage check, since this script is only executed
    manually during experiments.
    """
    model = VoteResultPredictionModel()
    stripped_model: Model = tfmot.sparsity.keras.strip_pruning(model.model)
    converter: tf.lite.TFLiteConverter = tf.lite.TFLiteConverter.from_keras_model(
        stripped_model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    minimised_model: bytes = converter.convert()
    module_location: str = os.path.dirname(__file__)
    js_archive: str = os.path.join(
        module_location, f"../resources/js/vote-prediction.lzma")
    Path(js_archive).unlink(True)
    with ZipFile(js_archive, "w", ZIP_LZMA) as zip_file:
        zip_file.writestr("vote-prediction.tflite", minimised_model)


if __name__ == "__main__":
    main()
