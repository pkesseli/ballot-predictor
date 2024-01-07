from bp.entity.ballot import DoubleMajorityBallotResult
from bp.entity.bill import Bill

import os
import tensorflow as tf
from decimal import Decimal
from keras import Model
from keras.models import load_model
from keras.layers import Dense, Input, Softmax
from keras.losses import CategoricalCrossentropy
from keras.optimizers import Adam
from tensorflow import Tensor
from transformers import BertTokenizer, TFBertForSequenceClassification
from transformers.modeling_tf_outputs import TFBaseModelOutputWithPoolingAndCrossAttentions
from typing import Callable, List, Literal, Tuple


HUGGINGFACE_MODEL: str = "bert-base-multilingual-cased"
"""str: Name of the multilingual BERT base model in HuggingFace repository.
This model is automatically downloaded if not already cached in the local cache
maintained by HuggingFace's transformers library."""


VOTE_RESULT_PREDICTION_MODEL: str = "vote-result-prediction/model"
"""str: """


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


NUMBER_OF_LABELS: int = 2
"""int: Number of output label values produced by our output layer. We use a
one-hot encoding, where two floats represent a single percentage."""


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

    @staticmethod
    def create_popular_majority_model():
        """Creates a model to predict the popular majority voting result for a
        bill.

        Returns:
            VoteResultPredictionModel: Model predicting popular majority share.
        """
        return VoteResultPredictionModel("popular_majority", lambda result: result.percentage_yes)

    @staticmethod
    def create_canton_majority_model():
        """Creates a model to predict the canton majority voting result for a
        bill.

        Returns:
            VoteResultPredictionModel: Model predicting canton majority share.
        """
        return VoteResultPredictionModel("canton_majority", lambda result: result.accepting_cantons)

    def __init__(self, model_name: Literal["popular_majority", "canton_majority"], label_factory: Callable[[DoubleMajorityBallotResult], Decimal]) -> None:
        """Loads the last persisted multilingual ballot vote result prediction
        model from get_persisted_model_file, if it exists. Otherwise a new,
        untrained model is created using __create_model.

        Args:
            model_name (str): Name of the model to create. Used for persisting.
            label_factory (Callable[[DoubleMajorityBallotResult], Decimal]):
            Indicates which part of the vote result is modelled, i.e. popular
            or canton majority.
        """
        self.tokenizer = BertTokenizer.from_pretrained(HUGGINGFACE_MODEL)
        self.persisted_model_directory = VoteResultPredictionModel.get_persisted_model_directory(
            model_name)
        if os.listdir(self.persisted_model_directory):
            self.model = load_model(self.persisted_model_directory)
        else:
            self.model = self.__create_model()
        self.label_factory = label_factory

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
        regression_layer = Dense(NUMBER_OF_LABELS, activation=Softmax())
        regression_layer_on_top_of_bert = regression_layer(
            bert_layers[POOLED_OUTPUT_LAYER_INDEX])
        model = Model(inputs=input_layer,
                      outputs=regression_layer_on_top_of_bert)
        model.compile(optimizer=Adam(), loss=CategoricalCrossentropy())
        return model

    def create_bill_features(self, bills: List[Bill]) -> Tensor:
        """Converts bills to a tensor containing the tokenized bill title and
        text into a single batch Tensor. The layout of just the tokenized texts
        would be:
        [["first", "bill", "int", "tokens"], ["second", "bill", "int", "tokens"]]

        However, since BERT expects data also to be grouped in batches, we
        produce instead:
        [[["first", "bill", "int", "tokens"], ["second", "bill", "int", "tokens"]]]

        I.e. we wrap the tokenized data into yet another tensor dimension,
        effectively modelling a single batch.

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
        popular and canton share vote result. Similar to create_bill_features,
        these labels are wrapped into another batch dimension to match
        TFBertForSequenceClassification expectations.

        Args:
            results (List[DoubleMajorityBallotResult]): Results to convert to expected labels.

        Returns:
            Tensor: Label tensor suitable for use with
            TFBertForSequenceClassification.
        """
        labels: List[float] = [
            float(self.label_factory(result)) / 100.0 for result in results]
        one_hot_labels: List[Tuple[float, float]] = [
            (label, 1.0 - label) for label in labels]
        return tf.convert_to_tensor(one_hot_labels)

    def train(self, features: Tensor, labels: Tensor, epochs: int) -> None:
        """Trains self.model with dataset.

        Args:
            dataset (tf.data.Dataset): Training data to use.
        """
        self.model.fit(features, labels, epochs=epochs, batch_size=BATCH_SIZE)

    def save(self) -> None:
        """Saves the current state of the model to get_persisted_model_file.
        """
        self.model.save(self.persisted_model_directory)

    @staticmethod
    def get_persisted_model_directory(model_name: str) -> str:
        """Provides the absolute path to the directory persisting model_name.

        Args:
            model_name (str): Name of the model to persist.

        Returns:
            str: Path to directory containing the model.
        """
        module_location: str = os.path.dirname(__file__)
        return os.path.join(module_location, "../resources/tensorflow", model_name)
