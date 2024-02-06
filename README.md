# Bachelor-Thesis
A repo contianing my bachelor thesis

## Convenient tricks
- To start the virtual environment, open a terminal in the folder containing your venv and run:
  `source venv/bin/activate`
- To run a driving example from the Scenic examples:
  ```bash
  scenic examples/driving/badlyParkedCarPullingIn.scenic \
    --2d       \
    --simulate \
    --model scenic.simulators.newtonian.driving_model \
    --time 200
  ```
