# The Central Limit Theorem

Suppose you are running an experiment in which the outcomes for the random variable have an arbitrary probability distribution. This means that the random variable of the experiment is **not** a **Normal** random variable. It could be completely uniform where every outcome is equally likely, or some wonky curve with a whole bunch of peaks and valleys.

Simply put, the Central Limit Theorem says; if you run this experiment $N$ times, then the ***sum***$^{[1]}$  of those $N$ outcomes is itself a new random variable. Furthermore, it will be normally distributed, as long as $N$ is large enough.  The mean of this sum distribution will be $N\cdot\mu$, where $\mu$ is the mean of the original random variable; and the standard deviation of the sum is $\sqrt{N}\cdot\sigma$, where $\sigma$ is the standard deviation of the original random variable.

Test it out with the app by making a very skewed die distribution and setting the number of dice (our $N$) to be small. Watch the theoretical probability distribution as you increase the number of die to roll, the graph will begin to look more and more *Normal* shaped.

---

$^{[1]}$: You can also consider the average outcome, but in this example we use the sum. If you use the average, then the average outcome $\overline{\text{X}}$ is normal with $\overline{\text{X}}\sim\mathcal{N}\left(\mu, \frac{\sigma}{\sqrt{N}}\right)$
