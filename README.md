# Bachelor-Thesis
A repo contianing my bachelor thesis

# Setup

First download Scenic locally according to [the guide on the website](https://scenic-lang.readthedocs.io/en/latest/quickstart.html).

## Convenient tricks
- To start the virtual environment:

  > On Linux:
  ```bash
  source venv/bin/activate
  ```
  > On windows:
  ```powershell
  .\venv\Scripts\activate
  ```

- To run a driving example from the Scenic examples:
  ```bash
  scenic examples/driving/badlyParkedCarPullingIn.scenic \
    --2d       \
    --simulate \
    --model scenic.simulators.newtonian.driving_model \
    --time 200
  ```

- To Run the test
  > On Linux and windows
  ```bash
  python[version] ./simulation/test.py
  ```
