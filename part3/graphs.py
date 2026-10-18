"""Argumentation frameworks used in Part 3."""

# Question 1: test graphs, with the degrees computed by hand.
# weights = None means all the weights are 1 (like in TD3).
TEST_GRAPHS = {
    # from TD3 (G1): p -> a
    "TD3 G1, one attack": {
        "arguments": ["p", "a"], "attacks": [("p", "a")], "weights": None,
        "expected": {"p": 1, "a": 1 / 2}},
    # from TD3 (G2): q, r, s -> b, so b = 1 / (1 + 3)
    "TD3 G2, three attackers": {
        "arguments": ["q", "r", "s", "b"], "attacks": [("q", "b"), ("r", "b"), ("s", "b")], "weights": None,
        "expected": {"q": 1, "r": 1, "s": 1, "b": 1 / 4}},
    # from TD3 (G4): t -> p, t -> q, p -> a, q -> a, so a = 1 / (1 + 0.5 + 0.5)
    "TD3 G4, defence": {
        "arguments": ["t", "p", "q", "a"], "attacks": [("t", "p"), ("t", "q"), ("p", "a"), ("q", "a")], "weights": None,
        "expected": {"t": 1, "p": 1 / 2, "q": 1 / 2, "a": 1 / 2}},
    # TD3 G3 with weights: p -> q -> a, b alone
    # q = 0.9 / (1 + 0.6) = 0.5625 ; a = 0.5 / (1 + 0.5625) = 0.32
    "TD3 G3 with weights": {
        "arguments": ["p", "q", "a", "b"], "attacks": [("p", "q"), ("q", "a")],
        "weights": {"p": 0.6, "q": 0.9, "a": 0.5, "b": 0.3},
        "expected": {"p": 0.6, "q": 0.5625, "a": 0.32, "b": 0.3}},
    # TD3 G4 with weights: p = 0.8 / 1.5 ; q = 0.4 / 1.5 ; a = 0.9 / (1 + 0.8/1.5 + 0.4/1.5) = 0.5
    "TD3 G4 with weights": {
        "arguments": ["t", "p", "q", "a"], "attacks": [("t", "p"), ("t", "q"), ("p", "a"), ("q", "a")],
        "weights": {"t": 0.5, "p": 0.8, "q": 0.4, "a": 0.9},
        "expected": {"t": 0.5, "p": 0.8 / 1.5, "q": 0.4 / 1.5, "a": 0.5}},
    # special case: no attack, so degree = weight
    "no attack": {
        "arguments": ["a", "b"], "attacks": [], "weights": {"a": 0.3, "b": 0.7},
        "expected": {"a": 0.3, "b": 0.7}},
    # special case: an attacker with weight 0 has no effect
    "attacker with weight 0": {
        "arguments": ["a", "b"], "attacks": [("b", "a")], "weights": {"a": 0.8, "b": 0.0},
        "expected": {"a": 0.8, "b": 0.0}},
    # special case: a attacks itself, so x = 1 / (1 + x), x = (sqrt(5) - 1) / 2
    "a attacks itself": {
        "arguments": ["a"], "attacks": [("a", "a")], "weights": None,
        "expected": {"a": (5 ** 0.5 - 1) / 2}},
}

# Question 2: graphs with 2 arguments, one kind of attack each
TWO_ARGUMENT_GRAPHS = {
    "no attack": [],
    "b attacks a": [("b", "a")],
    "a and b attack each other": [("a", "b"), ("b", "a")],
    "a attacks itself": [("a", "a")],
}

# Question 2: graphs with 3 arguments
THREE_ARGUMENT_GRAPHS = {
    "chain: c -> b -> a": [("c", "b"), ("b", "a")],
    "two attackers: b -> a, c -> a": [("b", "a"), ("c", "a")],
    "3-cycle: a -> b -> c -> a": [("a", "b"), ("b", "c"), ("c", "a")],
}

# Question 2: graph with 4 arguments
FOUR_ARGUMENT_GRAPH = {
    "d -> b -> a, c -> a": [("d", "b"), ("b", "a"), ("c", "a")],
}