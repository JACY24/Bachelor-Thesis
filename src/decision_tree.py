# import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.metrics import accuracy_score
from sklearn.model_selection import StratifiedKFold

from typing import List
from tqdm import tqdm


def format_training_data(traces: List, labels: np.array, window_size: int = 5, prediction_horizon: int = 1):
    """Format training data into sliding windows"""
    X_windows = []
    y_labels = []

    for i, trace in tqdm(enumerate(traces), desc='Processing traces', unit='traces'):
        n_steps = trace.shape[0]

        if trace.shape[1] == 6:
            features = trace[['dist_fl', 'dist_fr', 'closing_rate_fl', 'closing_rate_fr', 'steering_angle', 'same_lane']].to_numpy()
        elif trace.shape[1] == 5:
            features = trace[['dist_fl', 'dist_fr', 'closing_rate_fl', 'closing_rate_fr', 'steering_angle']].to_numpy()

        collision_labels = labels[i]

        # Create sliding windows of size 'window_size'
        for j in range(n_steps  - prediction_horizon + 1):
            if j < window_size:
                padding = np.tile(features[0], (window_size - j, 1))
                window_data = np.vstack((padding, features[1:j+1]))
            else:
                window_data = features[j:j + window_size]  # Flatten the window

            window = window_data.flatten()
            # Extract a window of time steps
            # The target label is whether a collision occurs after the window, at 'prediction_horizon' time steps ahead
            future_collision = collision_labels[j + prediction_horizon - 1]
            
            # Append the flattened window and the corresponding label
            X_windows.append(window)
            y_labels.append(future_collision)

    return np.array(X_windows), np.array(y_labels)

def train_classifier(traces: List, labels: List, windows_size: int = 5, prediction_horizon: int = 1):
    """Train a decision tree classifier"""
    
    X, y = format_training_data(traces, np.array(labels),  windows_size, prediction_horizon)

    # Split into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=21)

    # params = {'max_depth': np.arange(1, 20),
    #             'min_samples_split': np.arange(2, 11),
    #             'min_samples_leaf': np.arange(2, 11),}
    # random_search = RandomizedSearchCV(DecisionTreeClassifier(), params, n_iter=20, cv=5, scoring='accuracy', random_state=42, n_jobs=-1)
    # random_search.fit(X_train, y_train)

    # print("Best parameters:", random_search.best_params_)

    # Train a decision tree classifier
    clf = DecisionTreeClassifier(min_samples_split=5, min_samples_leaf=10, max_depth=8, random_state=24)
    clf.fit(X_train, y_train)

    return clf
    