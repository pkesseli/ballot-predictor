from bp.entity.ballot import DoubleMajorityBallotResult
from bp.entity.bill import Bill

import os
import tensorflow as tf
from keras import Model
from keras.models import load_model
from keras.layers import Dense, Input, Reshape, Softmax
from keras.losses import CategoricalCrossentropy
from keras.optimizers import Adam
from tensorflow import Tensor
from transformers import BertTokenizer, TFBertForSequenceClassification
from transformers.modeling_tf_outputs import TFBaseModelOutputWithPoolingAndCrossAttentions
from typing import List, Tuple


HUGGINGFACE_MODEL: str = "bert-base-multilingual-cased"
"""str: Name of the multilingual BERT base model in HuggingFace repository.
This model is automatically downloaded if not already cached in the local cache
maintained by HuggingFace's transformers library."""


INPUT_IDS: str = "input_ids"
"""str: Name of input tensor produced by BertTokenizer. Used to extract correct
tensor from tokenizatin output."""


TENSOR_FLOW_FORMAT: str = "tf"
"""str: Format specifier instructing BertTokenizer to produce TensorFlow
tensors, as opposed to pytorch ones."""


POOLED_OUTPUT_LAYER_INDEX: int = 1
"""int: Index of output layer produced by BERT model when an input layer is
applied. Used to extract the output layer to which we add additional transfer
learned layers."""


NUMBER_OF_LABELS: int = 4
"""int: Number of output label values produced by our output layer. We use a
one-hot encoding, where two floats represent a single percentage. This results
in four float labels, since we have two percentages for a double majority vote.
"""


LABEL_MAX_VALUE: float = 100.0
"""float: Maximum value in our output layer's activation function. We use this
to constrain the output of our output layer between [0.0, 100.0], modelling a
percentage."""


BATCH_SIZE: int = 8
"""int: Batch size used for training."""


class VoteResultPredictionModel:
    """Vote result prediction model based on multilingual BERT base model. This
    class is excluded from unit test coverage enforcement, since training
    processes are long-running processes. Only the results produced by the
    persisted model will be covered by tests in the future.
    """

    def __init__(self) -> None:
        """Loads the last persisted multilingual ballot vote result prediction
        model from get_persisted_model_directory(), if it exists. Otherwise a
        new, untrained model is created using __create_model.
        """
        self.tokenizer = BertTokenizer.from_pretrained(HUGGINGFACE_MODEL)
        persisted_model_directory: str = VoteResultPredictionModel.get_persisted_model_directory()
        if os.listdir(persisted_model_directory):
            self.model = load_model(persisted_model_directory)
        else:
            self.model = self.__create_model()

    def __create_model(self) -> Model:
        """Creates a new, untrained model from a HuggingFace multilingual BERT
        base model. We extend this base model with an input layer suitable for
        text data tokenized by BertTokenizer and currently a single additional
        output layer matching the features for a double majority vote result.
        """
        bert_base_model: TFBertForSequenceClassification = TFBertForSequenceClassification.from_pretrained(
            HUGGINGFACE_MODEL)
        input_layer = Input(
            # TODO: Determine shape automatically
            shape=(53,), dtype=tf.int32)
        bert_layers: TFBaseModelOutputWithPoolingAndCrossAttentions = bert_base_model.bert(
            input_layer)
        regression_layer = Dense(NUMBER_OF_LABELS, activation=Softmax())(
            bert_layers[POOLED_OUTPUT_LAYER_INDEX])
        two_one_hot_layer = Reshape((2, 2))(regression_layer)
        model = Model(inputs=input_layer, outputs=two_one_hot_layer)
        model.compile(optimizer=Adam(), loss=CategoricalCrossentropy())
        return model

    def create_bill_features(self, bills: List[Bill]) -> Tensor:
        """Converts bills to a tensor containing the tokenized bill title. The
        bill wording is currently ignored.

        Args:
            bills (List[Bill]): Bills to tokenize and convert to features.

        Returns:
            Tensor: Features suitable for use with
            TFBertForSequenceClassification.
        """
        formatted_bills: List[str] = [bill.title for bill in bills]
        tokenized_bills: Tensor = self.tokenizer(
            formatted_bills, padding=True, truncation=True, return_tensors=TENSOR_FLOW_FORMAT)
        return tokenized_bills[INPUT_IDS]

    def create_double_majority_labels(self, results: List[DoubleMajorityBallotResult]) -> Tensor:
        """Converts results to labels in the form of tuples containing the
        popular and canton share vote result, each in one-hot encoding.

        Args:
            results (List[DoubleMajorityBallotResult]): Results to convert to expected labels.

        Returns:
            Tensor: Label tensor suitable for use with
            TFBertForSequenceClassification.
        """
        labels: List[Tuple[float, float]] = [(float(
            result.percentage_yes) / 100.0, float(result.accepting_cantons) / 100.0) for result in results]
        one_hot_labels: List[Tuple[Tuple[float, float], Tuple[float, float]]] = [
            ((label[0], 1.0 - label[0]), (label[1], 1.0 - label[1])) for label in labels]
        return tf.convert_to_tensor(one_hot_labels)

    def train(self, features: Tensor, labels: Tensor, epochs: int) -> None:
        """Trains self.model with dataset.

        Args:
            dataset (tf.data.Dataset): Training data to use.
        """
        self.model.fit(features, labels, epochs=epochs, batch_size=BATCH_SIZE)

    def save(self) -> None:
        """Saves the current state of the model to
        get_persisted_model_directory()."""
        self.model.save(
            VoteResultPredictionModel.get_persisted_model_directory())

    @staticmethod
    def get_persisted_model_directory() -> str:
        """Provides the absolute path to the directory persisting the model.

        Returns:
            str: Path to directory containing the model.
        """
        module_location: str = os.path.dirname(__file__)
        return os.path.join(module_location, "../resources/tensorflow")
