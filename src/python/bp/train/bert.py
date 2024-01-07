from bp.entity.ballot import DoubleMajorityBallotResult
from bp.entity.bill import Bill

import os
import tensorflow as tf
from keras import Model
from keras.models import load_model
from keras.layers import Dense, Input, ReLU
from keras.losses import MeanSquaredError
from keras.optimizers import Adam
from tensorflow import Tensor
from transformers import BertTokenizer, TFBertForSequenceClassification
from transformers.modeling_tf_outputs import TFBaseModelOutputWithPoolingAndCrossAttentions
from typing import List, Tuple


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
"""int: Number of output label values produced by our output layer. This
matches the number of float values in a double majority ballot results, i.e.
the popular vote and the share of cantons voting yes."""


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
        model from get_persisted_model_file, if it exists. Otherwise a new,
        untrained model is created using __create_model.
        """
        self.tokenizer = BertTokenizer.from_pretrained(HUGGINGFACE_MODEL)

        persisted_model: str = VoteResultPredictionModel.get_persisted_model_file()
        if os.path.isfile(persisted_model):
            self.model = load_model(persisted_model)
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
        regression_layer = Dense(
            NUMBER_OF_LABELS, activation=ReLU(LABEL_MAX_VALUE))
        regression_layer_on_top_of_bert = regression_layer(
            bert_layers[POOLED_OUTPUT_LAYER_INDEX])
        model = Model(inputs=input_layer,
                      outputs=regression_layer_on_top_of_bert)
        model.compile(optimizer=Adam(), loss=MeanSquaredError())
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
        labels: List[Tuple[float, float]] = [(float(result.percentage_yes), float(
            result.accepting_cantons)) for result in results]
        return tf.convert_to_tensor(labels)

    def train(self, features: Tensor, labels: Tensor, epochs: int) -> None:
        """Trains self.model with dataset.

        Args:
            dataset (tf.data.Dataset): Training data to use.
        """
        self.model.fit(features, labels, epochs=epochs, batch_size=BATCH_SIZE)

    def save(self) -> None:
        """Saves the current state of the model to get_persisted_model_file.
        """
        self.model.save(
            VoteResultPredictionModel.get_persisted_model_file(), save_format="keras")

    @staticmethod
    def get_persisted_model_file() -> None:
        """Provides the absolute path to the file persisting this model."""
        module_location: str = os.path.dirname(__file__)
        return os.path.join(module_location, "../resources/tensorflow/vote-result-prediction.keras")
