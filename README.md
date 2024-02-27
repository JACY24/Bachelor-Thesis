# Bachelor-Thesis
A repo contianing my bachelor thesis

## Convenient tricks
- To start the virtual environment:

  On Linux:
  ```bash
  source venv/bin/activate
  ```
  On windows:
  ```PowerShell
  .\venv\Scripts\activate.bat
  ```

- To run a driving example from the Scenic examples:
  ```bash
  scenic examples/driving/badlyParkedCarPullingIn.scenic \
    --2d       \
    --simulate \
    --model scenic.simulators.newtonian.driving_model \
    --time 200
  ```
