import src.simulation as sim
import src.decision_tree as dTree

from sklearn.utils import shuffle
from sklearn.tree import plot_tree
import matplotlib.pyplot as plt

import scenic
from tqdm import tqdm
import pickle


NUM_SIMULATIONS = 10
SCENARIO_RIGHTSIDE = scenic.scenarioFromFile('src/scenarios/parkedRight.scenic',
                                    model='scenic.simulators.newtonian.driving_model',
                                    mode2D=True)
SCENARIO_LEFTSIDE = scenic.scenarioFromFile('src/scenarios/parkedLeft.scenic',
                                    model='scenic.simulators.newtonian.driving_model',
                                    mode2D=True)

def main():
    print('test')
    traces = []
    labels = []

    # Run NUM_SIMULATIONS simulations of cars parked on the right side
    for _ in tqdm(range(NUM_SIMULATIONS), desc='Running right parked simulations', unit='sim'):
        simulation_result = sim.exec_simulation(SCENARIO_RIGHTSIDE)
        if simulation_result is not None:
            # When a simulation is succesful, we format the trace and add it to our list of traces
            formatted_trace = sim.format_trace(simulation_result)
            generated_labels = (sim.generate_labels(simulation_result['intersecting']))
            traces.append(formatted_trace)
            labels.append(generated_labels)
    
    # Run NUM_SIMULATIONS simulations of cars parked on the left side
    for _ in tqdm(range(NUM_SIMULATIONS), desc='Running left  parked simulations', unit='sim'):
        simulation_result = sim.exec_simulation(SCENARIO_LEFTSIDE)
        if simulation_result is not None:
            # When a simulation is succesful, we format the trace and add it to our list of traces
            formatted_trace = sim.format_trace(simulation_result)
            generated_labels = (sim.generate_labels(simulation_result['intersecting']))
            traces.append(formatted_trace)
            labels.append(generated_labels)

    traces, labels = shuffle(traces, labels, random_state=69)

    # learn a decision tree
    clf = dTree.train_classifier(traces, labels, 5, 5)
    
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