import pandas as pd

def monitor(trace: pd.DataFrame) -> bool:
    """A monitor for the simulation

    Parameters
    ----------
    trace : pd.DataFrame 
            a trace of a system execution

    Returns
    -------
    bool:
            True if the trace cannot be mapped to a trace of the system that violates the specification
            False otherwise
    """

    acceleration = 0
    speed = 0
    distance = 0

    for index, row in trace.iterrows():
        if index == 0:
            speed = row["speed"]
            distance = row["distance"]
            continue
        
        acceleration = row["speed"] - speed

        speed = row["speed"]
        distance = row["distance"]

        if distance - speed - acceleration < 0.2:
            print(f'timestep {index}, distance: {distance}, speed: {speed}, acceleration: {acceleration}')
            return False
        

    return True
