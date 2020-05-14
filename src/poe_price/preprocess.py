
def remove_empty_features(X, y):
    return X, y

def price_bounds(X, y, lower, upper):
    temp = [lowest < y < highest]
    return X[temp], y[temp]

def remove_price_outliers(X, y):
    return X, y
