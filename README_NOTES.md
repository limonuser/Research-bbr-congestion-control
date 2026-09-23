# Reading notes: BBR (Cardwell et al., CACM 2017)

My notes on the core ideas of *BBR: Congestion-Based Congestion Control* ([doi:10.1145/3009824](https://doi.org/10.1145/3009824)).

## 1. Why loss-based TCP breaks

Reno and CUBIC treat **packet loss as the signal of congestion**. That worked when links were slow and router memory was expensive. On today's networks it causes two problems:

1. **Bufferbloat (large buffers).** Loss-based TCP keeps sending until a router drops a packet. When the bottleneck has a large buffer (home modems, cellular base stations), the queue fills completely. Few packets are lost, but RTT grows from milliseconds to seconds.
2. **Low throughput on lossy links (small buffers).** On wireless or shallow-buffered paths, many losses are random rather than caused by congestion. Loss-based TCP still cuts its sending rate and leaves bandwidth unused. The paper's Figure 10 shows CUBIC's throughput dropping 10× at 0.1% loss and stalling above 1%.

## 2. Kleinrock's optimal operating point

A path can be described by two numbers:

- **RTprop**: the round-trip propagation time, i.e. the RTT with empty queues.
- **BtlBw**: the bottleneck bandwidth, the rate of the slowest link on the path.

Their product is the **bandwidth-delay product**, the amount of data the path holds with no queue:

$$\text{BDP} = \text{BtlBw} \times \text{RTprop}$$

```text
    App-limited          Bandwidth-limited           Buffer-limited
|<----------------->|<------------------------>|<---------------------->|
                    ▲
             Optimal operating point (inflight = BDP)
             * maximum delivery rate (link fully used)
             * minimum RTT (no standing queue)
```

Loss-based TCP operates at the right-hand edge, where the buffer is full and a packet is lost. BBR tries to operate at the left edge of the bandwidth-limited region, with inflight ≈ BDP.

## 3. How BBR estimates the two numbers

- RTprop and BtlBw can't be measured at the same moment. Measuring BtlBw needs enough inflight to fill the pipe, which creates a queue. Measuring RTprop needs the queue to be empty.
- BBR therefore tracks **RTprop as a windowed minimum of RTT** and **BtlBw as a windowed maximum of delivery rate**.
- **ProbeBW:** most of the time BBR paces at BtlBw, cycling the pacing gain through 1.25 → 0.75 → 1 → … One phase probes for more bandwidth, the next drains any queue the probe created (paper, Figure 4).
- **ProbeRTT:** if RTprop hasn't been refreshed for many seconds (10 s in the Linux implementation), BBR cuts inflight to four packets for at least one round trip, so the queue drains and a fresh minimum RTT can be measured.
