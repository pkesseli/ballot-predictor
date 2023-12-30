from bp.augment.chat import Chat
from bp.entity.ballot import DoubleMajorityBallot, DoubleMajorityBallotResult
from bp.entity.bill import Bill

import jsonpickle
from decimal import Decimal
from numpy import float64
from numpy.random import Generator
from scipy.stats import truncnorm
from typing import List


class BillAugmenter:
    """Helper class to augment ballot result data.
    """

    def __init__(self, chat: Chat, generator: Generator, multiplier: int):
        """Initialses ballot result augmenter.

        Args:
            chat (Chat): Chat model used for generating alternative bill
            titles and wordings.
            generator (Generator): Random seed used to augment vote result and
            date information randomly.
            multiplier (int): Number of paraphrasing and contradicting bills to
            generate.
        """
        self.chat = chat
        self.generator = generator
        self.multiplier = multiplier

    def paraphrase_and_contradict(self, ballots: List[DoubleMajorityBallot]) -> List[DoubleMajorityBallot]:
        """Generates n new ballots for each ballot in ballots, with paraphrased
        or opposite meanings.

        Args:
            ballots (List[DoubleMajorityBallot]): Ballots to augment.

        Returns:
            List[DoubleMajorityBallot]: Augmented list of ballots.
        """
        responses: List[str] = []
        for ballot in ballots:
            responses.extend(self.chat.prompt([f"""Das nachfolgende JSON-Objekt enthält eine Volksinitiative zur Anpassung der schweizerischen Bundesverfassung mit Titel und Wortlaut:

```
{{
  "title": "{ballot.bill.title}",
  "wording": "{ballot.bill.wording}"
}}
```

Generiere {self.multiplier - 1} weitere Initiativen mit derselben Struktur. Diese neuen Initiativen sollen dieselbe inhaltliche Bedeutung haben wie das Original, aber sollen alle anders formuliert sein. Die neuen Texte dürfen signifikant vom Original abweichen, aber verändere keine Absatz- oder Paragraphennummern. Die Ausgabe soll nur ein generiertes JSON-Array mit den Initiativen beinhalten, keine weiteren Kommentare oder Text."""]))
            responses.extend(self.chat.prompt([f"""Das nachfolgende JSON-Objekt enthält eine Volksinitiative zur Anpassung der schweizerischen Bundesverfassung mit Titel und Wortlaut:

```
{{
  "title": "{ballot.bill.title}",
  "wording": "{ballot.bill.wording}"
}}
```

Generiere {self.multiplier} weitere Initiativen mit derselben Struktur. Diese neuen Initiativen sollen das Gegenteil der obigen Initiative fordern. Trotz der gegenteiligen Aussage soll der Text so ansprechend wie möglich für potentielle Wähler wirken. Die neuen Texte dürfen signifikant vom Original abweichen, aber verändere keine Absatz- oder Paragraphennummern. Die Ausgabe soll nur ein generiertes JSON-Array mit den Initiativen beinhalten, keine weiteren Kommentare oder Text."""]))

        new_ballots: List[DoubleMajorityBallot] = []
        response_index: int = 0
        for response in responses:
            parsed_response: List[dict[str]] = jsonpickle.decode(response)
            ballot: DoubleMajorityBallot = ballots[int(response_index / 2)]
            response_element_index: int = 0
            is_contradiction: bool = response_index % 2 == 1
            if not is_contradiction:
                new_ballots.append(ballot)

            while response_element_index < len(parsed_response):
                new_text_and_wording: dict[str] = parsed_response[response_element_index]
                new_ballots.append(DoubleMajorityBallot(
                    Bill(
                        new_text_and_wording["title"],
                        new_text_and_wording["wording"],
                        ballot.bill.date
                    ),
                    ballot.status,
                    self.__augment_vote(
                        ballot.result.percentage_yes,
                        ballot.result.accepting_cantons,
                        is_contradiction)
                ))
                response_element_index = response_element_index + 1
            response_index = response_index + 1

        return new_ballots

    def __augment_vote(self, percentage_yes: Decimal, accepting_cantons: Decimal, flip_result: bool) -> DoubleMajorityBallotResult:
        """Generates a new vote result randomly, while either maintaining the
        result or flipping it for contradictory bill texts.

        Args:
            percentage_yes (Decimal): Share of population accepting the bill.
            accepting_cantons (Decimal): Share of cantons accepting the bill.
            flip_result (bool): Whether to flip the result.

        Returns:
            DoubleMajorityBallotResult: New ballot result.
        """
        one_hundred = Decimal(100)
        if flip_result:
            percentage_yes = one_hundred - percentage_yes
            accepting_cantons = one_hundred - accepting_cantons

        new_percentage_yes: Decimal = self.truncated_normal_distribution(
            percentage_yes)
        new_accepting_cantons: Decimal = self.truncated_normal_distribution(
            accepting_cantons)
        return DoubleMajorityBallotResult(new_percentage_yes, new_accepting_cantons)

    def truncated_normal_distribution(self, value: Decimal) -> Decimal:
        """Helper random distribution to generate new vote results without
        changing the outcome, and with values closer to the original result
        more probable that significantly different results.

        Args:
            value (Decimal): Original result, either share of population
            accepting a bill or share of cantons accepting it.

        Returns:
            Decimal: New vote result with same outcome.
        """
        fifty = Decimal(50)
        min: Decimal = fifty if value >= fifty else Decimal(0)
        max: Decimal = Decimal(100) if value >= fifty else Decimal(49.99)
        std_dev: float = 2

        min_num_std_devs_diff: float = float((min - value) / std_dev)
        max_num_std_devs_diff: float = float((max - value) / std_dev)
        value: float64 = truncnorm.rvs(
            min_num_std_devs_diff,
            max_num_std_devs_diff,
            loc=float(value),
            scale=std_dev,
            random_state=self.generator)

        return Decimal(value).quantize(Decimal("0.01"))
