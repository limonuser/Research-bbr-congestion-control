"""
Redraws three figures from Cardwell et al., "BBR: Congestion-Based Congestion
Control" (CACM 2017), using simple analytical models.

The loss-based curves are computed (Mathis et al. model, full-buffer queueing).
The BBR curves are hand-shaped to follow the results reported in the paper;
this script does not implement or simulate BBR.
"""

import numpy as np
import matplotlib.pyplot as plt

def simulate_loss_experiment():
    loss_rates = np.logspace(-5, -0.3, 100)
    link_bw_mbps = 100.0
    rtt_ms = 100.0
    mss_bytes = 1500
    
    max_goodput = link_bw_mbps * (1.0 - loss_rates)
    
    # Mathis et al. model for loss-based TCP: rate = (MSS / RTT) * C / sqrt(p)
    c_const = np.sqrt(1.5)
    rtt_sec = rtt_ms / 1000.0
    mathis_bps = (mss_bytes * 8.0 / rtt_sec) * (c_const / np.sqrt(np.maximum(loss_rates, 1e-7)))
    mathis_mbps = mathis_bps / 1e6
    loss_based_goodput = np.minimum(link_bw_mbps, mathis_mbps) * (1.0 - loss_rates)
    
    # BBR: hand-shaped to the paper's reported result (at the limit up to 5% loss,
    # close to it up to 15%); not derived from BBR's algorithm
    bbr_goodput = np.zeros_like(loss_rates)
    for i, p in enumerate(loss_rates):
        if p < 0.05:
            bbr_goodput[i] = max_goodput[i]
        elif p < 0.15:
            bbr_goodput[i] = max_goodput[i] * (1.0 - (p - 0.05) * 1.5)
        elif p < 0.20:
            bbr_goodput[i] = max_goodput[i] * (1.0 - (p - 0.05) * 3.5)
        else:
            bbr_goodput[i] = 0.0
            
    return loss_rates, max_goodput, loss_based_goodput, bbr_goodput

def simulate_bufferbloat_experiment():
    buffer_sizes_kb = np.linspace(10, 10000, 100)
    link_rate_kbps = 128.0
    min_rtt_sec = 0.040
    
    # Loss-based queue fills buffer to capacity
    loss_based_latency_sec = min_rtt_sec + (buffer_sizes_kb * 8.0) / link_rate_kbps
    # BBR: drawn flat near the base RTT (the paper reports it keeps inflight ~1 BDP)
    bbr_latency_sec = np.full_like(buffer_sizes_kb, min_rtt_sec + 0.005)
    
    return buffer_sizes_kb, loss_based_latency_sec, bbr_latency_sec

def simulate_pacing_cycle():
    time_steps = 200
    time = np.linspace(0, 1.6, time_steps)
    rtt_base = 40.0
    inflight_base = 50.0
    
    rtt_curve = np.full(time_steps, rtt_base)
    inflight_curve = np.full(time_steps, inflight_base)
    
    # Illustrative sketch of ProbeBW gain cycling (1.25x probe phase); not measured
    probe1 = (time >= 0.2) & (time <= 0.4)
    inflight_curve[probe1] = inflight_base * (1.0 + 0.25 * np.sin(np.pi * (time[probe1] - 0.2) / 0.2))
    rtt_curve[probe1] = rtt_base + (inflight_curve[probe1] - inflight_base) * 0.5
    
    probe2 = (time >= 1.0) & (time <= 1.2)
    inflight_curve[probe2] = inflight_base * (1.0 + 0.25 * np.sin(np.pi * (time[probe2] - 1.0) / 0.2))
    rtt_curve[probe2] = rtt_base + (inflight_curve[probe2] - inflight_base) * 0.5

    return time, rtt_curve, inflight_curve

def run_experiments():
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig = plt.figure(figsize=(15, 10))

    # 1. Goodput vs Loss Rate
    ax1 = fig.add_subplot(2, 2, 1)
    loss_rates, max_gp, loss_gp, bbr_gp = simulate_loss_experiment()
    ax1.plot(loss_rates * 100, max_gp, 'k--', label='Max Theoretical', alpha=0.6)
    ax1.plot(loss_rates * 100, bbr_gp, color='#2ca02c', linewidth=2.5, label='BBR (shaped to paper)')
    ax1.plot(loss_rates * 100, loss_gp, color='#d62728', linewidth=2, label='Loss-based (Mathis model)')
    ax1.set_xscale('log')
    ax1.set_title('After paper Fig. 10: goodput vs. random loss (model)', fontweight='bold')
    ax1.set_xlabel('Random Loss Rate (%) - Log Scale')
    ax1.set_ylabel('Goodput (Mbps)')
    ax1.set_ylim(-2, 105)
    ax1.legend()

    # 2. Bufferbloat Comparison
    ax2 = fig.add_subplot(2, 2, 2)
    buf_kb, loss_lat, bbr_lat = simulate_bufferbloat_experiment()
    ax2.plot(buf_kb, loss_lat, color='#d62728', linewidth=2.5, label='Loss-based (full buffer)')
    ax2.plot(buf_kb, bbr_lat, color='#2ca02c', linewidth=2.5, label='BBR (shaped to paper)')
    ax2.axhline(y=75, color='gray', linestyle=':', label='SYN timeout, Windows/macOS (approx.)')
    ax2.axhline(y=180, color='black', linestyle=':', label='SYN timeout, Linux/Android (approx.)')
    ax2.set_title('After paper Fig. 12: latency vs. buffer size (model)', fontweight='bold')
    ax2.set_xlabel('Bottleneck Buffer Size (KB)')
    ax2.set_ylabel('End-to-End Latency (Seconds)')
    ax2.legend()

    # 3. Pacing Gain Dynamics
    ax3 = fig.add_subplot(2, 1, 2)
    t_dyn, rtt_dyn, inf_dyn = simulate_pacing_cycle()
    ax3_twin = ax3.twinx()
    p1 = ax3.plot(t_dyn, rtt_dyn, color='#1f77b4', linewidth=2, label='RTT (ms)')
    p2 = ax3_twin.plot(t_dyn, inf_dyn, color='#bcbd22', linewidth=2, linestyle='--', label='Inflight (kB)')
    ax3.set_title('After paper Fig. 4: ProbeBW gain cycling (sketch)', fontweight='bold')
    ax3.set_xlabel('Time (seconds)')
    ax3.set_ylabel('RTT (ms)', color='#1f77b4')
    ax3_twin.set_ylabel('Inflight (kB)', color='#bcbd22')
    plots = p1 + p2
    labels = [l.get_label() for l in plots]
    ax3.legend(plots, labels, loc='upper left')

    plt.tight_layout()
    import os
    os.makedirs('results', exist_ok=True)
    plt.savefig('results/bbr_replication_results.png', dpi=300)
    print("Saved figure to 'results/bbr_replication_results.png'.")

if __name__ == '__main__':
    run_experiments()