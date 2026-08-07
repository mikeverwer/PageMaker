# Coin Flip Simulator

This applet simulates flipping a set of coins many times and counts the number of heads in each trial,
which then gets compared to the theoretical binomial distribution.

## How To Use

- **Number of Coins $n$:** The number of coins flipped during each trial.  
  For a single trial, the result is the total number of heads observed across all $n$ flips.

- **Number of Trials $T$:** The number otf time the experiment is repeated.  
  Each batch of trials contributes one dot to the plot. Batches are of size $\lceil T / 200 \rceil$.

- **Probability of Heads $p$:** The probability that any single coin winds heads.  
  Set to 0.5 for a fair coin.

- Press **Run Simulation** to Start. Dots accumulate as trials complete, stacking above the value of heads observed. Once the simulation finishes, the theoretical curve is drawn.

## Reading the Plot

The horizontal axis shows the number of heads observed in a trial, ranging from $0$ to $n$.
The left vertical axis shows probability and the right shows frequency (count). The two are linked:
a probability of $p$ corresponds to $p \times \text{number of trials}$ on the frequency axis.

The grey curve is the binomial probability mass function, which describes the theoretical probability of
observing each possible number of heads. The dashed vertical line marks the expected value
$E[X] = np$, along with the probability of that exact outcome. Notice that even the
most likely value usually has a fairly low probability: with 50 fair coins, the chance of
getting exactly 25 heads is only about 11%.

For large numbers of trials, each dot represents multiple trials rather than one; this keeps
tall columns from overflowing the plot. The exact ratio is shown beneath the horizontal axis.