# Scheduling Problem Solver

This project contains the implementation of different approaches to solve the **Multi-Mode Resource-Constrained Project Scheduling Problem (MRCPSP)** — a classic optimisation problem with applications in project management and production engineering.

## Purpose

The goal is to develop, test, and compare algorithms for solving the MRCPSP, including:
- **Simulated Annealing (SA)**
- **Hybrid Methods**
- **Simple Random Search (SR)**

The focus is on evaluating the performance of these approaches on instances of varying sizes.

## About the Problem

The **MRCPSP** involves scheduling project activities considering:
- Limited resources
- Alternative execution modes (with different durations and resource consumptions)
- Precedence constraints between activities

The objective is to minimise the overall project duration (makespan), while respecting all constraints.

## Project Structure

```
├── data/                  # Test instances (PSPLIB format)
├── results/               # Experimental results
├── src/                   # Algorithm implementations
│   ├── sa.py              # Simulated Annealing
│   ├── hybrid.py          # Hybrid approach
│   └── sr.py              # Simple Random Search
├── experiments/           # Experiment scripts and analysis
├── utils/                 # Utility functions
├── README.md
└── requirements.txt
```

## How to Run

1. **Clone the repository**
   ```bash
   git clone https://github.com/mqsantiago/scheduling-problem.git
   cd scheduling-problem
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the algorithms**
   Examples:
   ```bash
   python src/sa.py --instance data/instance1.mm
   python src/hybrid.py --instance data/instance1.mm
   python src/sr.py --instance data/instance1.mm
   ```

4. **Run experiments**
   ```bash
   python experiments/run_experiments.py
   ```

## Data Sets

The test instances follow the [PSPLIB](http://www.om-db.wi.tum.de/psplib/) standard — a benchmark library for project scheduling problems.

## Results

The results include:
- Obtained makespan
- Execution time
- Convergence over time

Plots and analysis can be found in the `results/` folder.

## Contributing

Contributions are welcome!  
Feel free to open issues, suggest improvements, or submit new algorithm implementations.

## Licence

This project is licensed under the MIT Licence.
