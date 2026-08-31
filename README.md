# Research-bbr-congestion-control
This project implements and replicates Google’s BBR congestion control algorithm from the ACM paper in Python. It simulates and plots BBR’s bandwidth-delay product model vs. loss-based TCP (CUBIC), showing how BBR avoids bufferbloat and maintains high goodput under high packet loss.

## Contents
- `main.py` — experiment runner that replicates the paper's goodput-vs-loss, bufferbloat, and ProbeBW pacing-cycle figures
- `README_NOTES.md` — notes, math, and implementation breakdown of the BBR algorithm
- `paper/3009824.pdf` — original ACM Queue paper ("BBR: Congestion-Based Congestion Control", Cardwell et al.)
- `results/bbr_replication_results.png` — generated benchmark charts from running `main.py`

## Usage
```bash
pip install numpy matplotlib
python main.py
```
Output charts are saved to `results/bbr_replication_results.png`.
