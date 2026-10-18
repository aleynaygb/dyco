import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull
from q1_tools import attack_matrix, weighted_h_categorizer


def random_weights(n_arguments, n_samples=100_000, seed=0):
    """Draw random weights between 0 and 1: one row = one weight vector."""
    # random generator (the seed makes the results reproducible)
    rng = np.random.default_rng(seed)
    return rng.random((n_samples, n_arguments))


def degrees_for_random_weights(arguments, attacks, n_samples=100_000, seed=0):
    """Give the graph random weights n_samples times, and run the h-categorizer on each weighted graph."""
    # the graph (A, R)
    M = attack_matrix(arguments, attacks)
    # n_samples random weight vectors -> n_samples weighted graphs (A, R, w)
    W = random_weights(len(arguments), n_samples, seed)
    # weighted h-categorizer on every weighted graph (row i of X = degrees of graph i)
    X, _ = weighted_h_categorizer(M, W)
    return W, X


def show_samples(arguments, W, X, n=10):
    """Table of the first n samples: weights -> final degrees."""
    # one column per argument for the weights, then one per argument for the degrees
    table = pd.DataFrame(W[:n], columns=[f"w({a})" for a in arguments])
    for i, a in enumerate(arguments):
        table[f"Deg({a})"] = X[:n, i]
    return table.round(3)


def compute_hull(X):
    """Convex hull of the degree vectors (the "elastic band" around the cloud)."""
    # scipy computes the hull (Quickhull algorithm)
    return ConvexHull(X)


def draw_hull_2d(ax, X, hull, names=("a", "b")):
    """Draw the convex hull of a 2-argument graph."""
    # corners of the hull, + the first one again to close the shape
    v = np.append(hull.vertices, hull.vertices[0])
    ax.plot(X[v, 0], X[v, 1], color="#1f4e9c", lw=2, label="convex hull")
    # one axis per argument, degrees between 0 and 1
    ax.set_xlim(0, 1.02)
    ax.set_ylim(0, 1.02)
    ax.set_aspect("equal")
    ax.set_xlabel(f"degree of {names[0]}")
    ax.set_ylabel(f"degree of {names[1]}")


def draw_heatmap_2d(ax, X):
    """Heat-map of the points: count the points in small hexagons (dark = many points)."""
    # mincnt=1: empty hexagons stay white
    return ax.hexbin(X[:, 0], X[:, 1], gridsize=40, extent=(0, 1, 0, 1), mincnt=1, cmap="YlOrRd")


def density_grid(X, bins=40):
    """Cut the square (or cube) into small cells and give the share of points in each cell."""
    # count the points in each cell (works for 2 or 3 arguments)
    counts, _ = np.histogramdd(X, bins=bins, range=[[0, 1]] * X.shape[1])
    # turn counts into proportions (all cells sum to 1)
    return counts / counts.sum()


def heatmap_difference(P, Q):
    """Difference between two heat-maps: share of points that are not in the same place (0 = identical, 1 = completely different)."""
    # half of the sum of the differences, cell by cell
    return 0.5 * np.abs(P - Q).sum()



def draw_hull_3d(ax, X, hull, names=("a", "b", "c")):
    """Draw the convex hull of a 3-argument graph (a surface made of triangles)."""
    # each face of the hull is a triangle
    ax.plot_trisurf(X[:, 0], X[:, 1], X[:, 2], triangles=hull.simplices,
                    color="#1f4e9c", alpha=0.08, edgecolor="#1f4e9c", linewidth=0.2)
    # one axis per argument, degrees between 0 and 1
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_zlim(0, 1)
    ax.set_xlabel(f"degree of {names[0]}")
    ax.set_ylabel(f"degree of {names[1]}")
    ax.set_zlabel(f"degree of {names[2]}")


def draw_heatmap_3d(ax, X, bins=15, n_show=20_000):
    """3D heat-map: each point gets the colour of the density around it (dark = many points)."""
    # share of points in each small cube
    grid = density_grid(X, bins)
    # find the small cube of each point
    cells = np.minimum((X * bins).astype(int), bins - 1)
    density = grid[cells[:, 0], cells[:, 1], cells[:, 2]]
    # we only draw some of the points so the plot stays readable
    return ax.scatter(X[:n_show, 0], X[:n_show, 1], X[:n_show, 2],
                      c=density[:n_show], cmap="YlOrRd", s=2)

def real_space_volume(arguments, attacks, n_points=1_000_000, seed=0):
    """Share of the cube that is really reachable: pick random degrees and check that the weights they need are <= 1."""
    M = attack_matrix(arguments, attacks)
    rng = np.random.default_rng(seed)
    # random degree vectors in the cube
    Y = rng.random((n_points, len(arguments)))
    # weights needed to get these degrees (h-categorizer formula turned around)
    W_needed = Y * (1 + Y @ M)
    # a point is in the space if all its weights are <= 1
    return np.mean((W_needed <= 1).all(axis=1))


def draw_correlation_matrix(ax, X, names):
    """Colour the correlation between the degrees of every pair of arguments (red = attack, blue = defence)."""
    # correlation between the columns of X (one column = one argument)
    corr = np.corrcoef(X.T)
    # hide the diagonal (always 1, an argument with itself)
    np.fill_diagonal(corr, np.nan)
    image = ax.imshow(corr, cmap="RdBu", vmin=-0.35, vmax=0.35)
    # write the value in each cell
    for i in range(len(names)):
        for j in range(len(names)):
            if i != j:
                ax.text(j, i, f"{corr[i, j]:.2f}", ha="center", va="center", fontsize=8)
    ax.set_xticks(range(len(names)), names)
    ax.set_yticks(range(len(names)), names)
    return image