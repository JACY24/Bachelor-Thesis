# import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from typing import List
from tqdm import tqdm


def format_training_data(traces: List, labels: np.array, window_size: int = 5, prediction_horizon: int = 1):
    """Format training data into sliding windows"""
    X_windows = []
    y_labels = []

    for i, trace in tqdm(enumerate(traces), desc='Processing traces', unit='traces'):
        n_steps = trace.shape[0]
        features = trace[['dist_fl', 'dist_fr', 'closing_rate_fl', 'closing_rate_fr', 'steering_angle']].to_numpy()
        collision_labels = labels[i]

        # Create sliding windows of size 'window_size'
        for j in range(n_steps - window_size - prediction_horizon + 1):
            # Extract a window of time steps
            window = features[j:j + window_size].flatten()  # Flatten the window
            
            # The target label is whether a collision occurs after the window, at 'prediction_horizon' time steps ahead
            future_collision = collision_labels[j + window_size + prediction_horizon - 1]
            
            # Append the flattened window and the corresponding label
            X_windows.append(window)
            y_labels.append(future_collision)

    return np.array(X_windows), np.array(y_labels)

def train_classifier(traces: List, labels: List, windows_size: int = 5, prediction_horizon: int = 1):
    """Train a decision tree classifier"""
    
    X, y = format_training_data(traces, np.array(labels),  windows_size, prediction_horizon)

    # Split into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=21)

    # Train a decision tree classifier
    clf = DecisionTreeClassifier(class_weight='balanced', max_depth=4, min_samples_split=10, min_samples_leaf=5, random_state=21)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy:.2f}")

    return clf
    