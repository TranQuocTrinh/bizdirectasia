import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import Normalizer
from sklearn.cross_validation import cross_val_score
from sklearn.preprocessing import Imputer

from scipy.stats import skew

def is_outlier(points, thresh = 3.5):
    if len(points.shape) == 1:
        points = points[:,None]
    median = np.median(points, axis=0)
    diff = np.sum((points - median)**2, axis=-1)
    diff = np.sqrt(diff)
    med_abs_deviation = np.median(diff)

    modified_z_score = 0.6745 * diff / med_abs_deviation

    return modified_z_score > thresh

def main():
    target = df_train[df_train.columns.values[-1]]
    target_log = np.log(target)

    plt.figure(figsize=(10,5))
    plt.subplot(1,2,1)
    sns.distplot(target, bins=50)
    plt.title('Original Data')
    plt.xlabel('Revenue')

    plt.subplot(1,2,2)
    sns.distplot(target_log, bins=50)
    plt.title('Natural Log of Data')
    plt.xlabel('Natural Log of Revenue')
    plt.tight_layout()
    plt.savefig('revenue_dist.png')
    # Merge Train and Test to evaluate ranges and missing values
    df_train = df_train[df_train.columns.values[:-1]]
    df = df_train.append(df_test, ignore_index = True)


def train():
    from sklearn.metrics import make_scorer, mean_squared_error
    scorer = make_scorer(mean_squared_error, False)

    clf = RandomForestRegressor(n_estimators=500, n_jobs=-1)
    cv_score = np.sqrt(-cross_val_score(estimator=clf, X=X_train, y=y_train, cv=15, scoring = scorer))

    plt.figure(figsize=(10,5))
    plt.bar(range(len(cv_score)), cv_score)
    plt.title('Cross Validation Score')
    plt.ylabel('RMSE')
    plt.xlabel('Iteration')

    plt.plot(range(len(cv_score) + 1), [cv_score.mean()] * (len(cv_score) + 1))
    plt.tight_layout()
    plt.savefig('cv_score.png')