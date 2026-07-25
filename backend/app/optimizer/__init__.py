"""Bid optimization: route matching and a deterministic recommendation engine.

The engine implements the real KAYAK Position #1 bidding strategy (see
``rules.py`` and ``recommendation.py``). It is fully deterministic — the same
input always yields the same output, with no AI, randomization, or heuristics
outside the defined strategy. Every threshold lives in ``config.py`` rather than
being hardcoded in the logic.
"""
