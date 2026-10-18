import numpy as np


def attack_matrix(arguments, attacks):
    """Turn a graph into a matrix: M[i, j] = 1 if argument i attacks argument j."""
    # give each argument a number (its position in the list)
    index = {a: i for i, a in enumerate(arguments)}
    # start with no attacks
    M = np.zeros((len(arguments), len(arguments)))
    # put a 1 for each attack (row = attacker, column = target)
    for attacker, target in attacks:
        if attacker not in index or target not in index:
            raise ValueError(f"Attack ({attacker}, {target}) uses an unknown argument")
        M[index[attacker], index[target]] = 1
    return M


def weighted_h_categorizer(M, W, epsilon=1e-6, max_iter=10_000):
    """Compute the weighted h-categorizer degrees. W can be one weight vector or many (one per row)."""
    W = np.asarray(W, dtype=float)
    # check the inputs
    if epsilon <= 0:
        raise ValueError("epsilon must be > 0")
    if M.shape[0] != M.shape[1] or W.shape[-1] != M.shape[0]:
        raise ValueError("M must be n x n and W must have n weights per vector")
    if np.any(W < 0) or np.any(W > 1):
        raise ValueError("weights must be in [0, 1]")
    # empty graph: nothing to compute
    if W.size == 0:
        return W.copy(), 0

    # we start from the weights (HC_0 = w)
    HC = W.copy()
    for k in range(1, max_iter + 1):
        # sum of the degrees of the attackers of each argument
        attack_sum = HC @ M
        # h-categorizer formula
        HC_next = W / (1 + attack_sum)
        # stop when the degrees don't move anymore
        if np.max(np.abs(HC_next - HC)) < epsilon:
            return HC_next, k
        HC = HC_next
    raise RuntimeError("No convergence after max_iter iterations")