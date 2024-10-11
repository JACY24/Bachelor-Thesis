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

    a = 0
    v = 0
    d = 0

    for index, row in trace.iterrows():
        if index == 0:
            v = row["speed"] / 10
            d = row["distance"]
            continue
        
        a = row["speed"] / 10 - v

        v = row["speed"] / 10
        d = row["distance"]
        # print(f'timestep {index}, distance: {d}, speed: {v}, acceleration: {a}')

        d_travelled = v * 2 + 0.5*a*2*2
        print(trace)
        if d - d_travelled < 0.15:
            print(f'timestep {index}, distance: {d}, speed: {v}, acceleration: {a}')
            return False
        
    return True
