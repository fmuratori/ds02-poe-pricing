import numpy as np


def remove_empty_features(X):
    notempty = []
    for i in range(X.shape[1]):
        col = X.getcol(i)
        if np.std(col.toarray()) != 0:
            notempty.append(i)
    X = X[:, notempty]
    return X

def price_bounds_row_removal(X, y, lower, upper):
    indices = np.where((y>=lower) & (y<=upper))[0]
    return X[indices, :], y[indices] 