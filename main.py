import src.simulation as sim
import src.decision_tree as dTree

from sklearn.utils import shuffle
from sklearn.tree import plot_tree
import matplotlib.pyplot as plt

import scenic
import pickle

NUM_SIMULATIONS = 1000
SCENARIO_LEFTSIDE = scenic.scenarioFromFile('src/scenarios/parkedLeft.scenic',
                                    model='scenic.simulators.newtonian.driving_model',
                                    mode2D=True)
SCENARIO_RIGHTSIDE = scenic.scenarioFromFile('src/scenarios/parkedRight.scenic',
                                    model='scenic.simulators.newtonian.driving_model',
                                    mode2D=True)
SCENARIO_LEFTSIDE = scenic.scenarioFromFile('src/scenarios/testerLeft.scenic',
                                    model='scenic.simulators.newtonian.driving_model',
                                    mode2D=True)                                 
SCENARIO_RIGHTSIDE = scenic.scenarioFromFile('src/scenarios/testerRight.scenic',
                                    model='scenic.simulators.newtonian.driving_model',
                                    mode2D=True)

def main():

    # Run NUM_SIMULATIONS simulations of both scenarios
    traces_left, labels_left, intersections_left = sim.training_data_from_scenario(SCENARIO_LEFTSIDE, NUM_SIMULATIONS)
    traces_right, labels_right, intersections_right = sim.training_data_from_scenario(SCENARIO_RIGHTSIDE, NUM_SIMULATIONS)
    traces = traces_left + traces_right
    labels = labels_left + labels_right
    intersections_training = intersections_left + intersections_right

    traces, labels = shuffle(traces, labels, random_state=69)

    # learn a decision tree
    clf = dTree.train_classifier(traces, labels, 5, 6)
    
    # create a list of feature names to make the tree more human readable
    feature_names = []
    for i in range(5):  # Assuming window size of 5
        feature_names.extend([f'dist_fl_{i}', f'dist_fr_{i}', f'closing_rate_fl_{i}', f'closing_rate_fr_{i}', f'steering_angle_{i}'])

    # plot the learned decision tree
    plt.figure(figsize=(12, 8))
    plot_tree(clf, feature_names=feature_names, filled=True)
    plt.show()

    with open("test.pkl", 'wb') as f:
        pickle.dump(clf, f, protocol=5)
        f.close()
        
    traces_left, labels_left, intersections_left = sim.training_data_from_scenario(SCENARIO_LEFTSIDE, NUM_SIMULATIONS)
    traces_right, labels_right, intersections_right = sim.training_data_from_scenario(SCENARIO_RIGHTSIDE, NUM_SIMULATIONS)
    traces = traces_left + traces_right
    labels = labels_left + labels_right
    intersections_testing = intersections_left + intersections_right

    collisions_without_monitor = intersections_training.count(True) / (NUM_SIMULATIONS*2)
    collisions_with_monitor = intersections_testing.count(True) / (NUM_SIMULATIONS*2)

    print(f'collisions without monitor:\t{collisions_without_monitor:.2%}\ncollisions with monitor:\t{collisions_with_monitor:.2%}')
  
if __name__ == '__main__':
    main()

# TODO:

# Vragen
# Overfitting, hoe kan ik hier het beste mee omgaan?

# Balans in samples (dupliceren of geen botsing rejecten)
# hoe goed is de monitor: remmen na 0.3s bij piepje: botsing of niet?
# meer situaties qua parkeren

# wegrijden als parkeren ipv. followlane

# CARLA?traces = []