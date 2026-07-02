from modules.probability_base import true_probability_base


def normalize_probabilities(probabilities):
    total = sum(probabilities.values())
    return {key: value / total for key, value in probabilities.items()}


def odds_to_probabilities(odds):
    return true_probability_base(odds).get("probabilities")


def combine_probabilities(odds, polymarket, news, config):
    return odds_to_probabilities(odds) or {}
