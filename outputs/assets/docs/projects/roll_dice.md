# Roll Dice

This program was made to showcase the Central Limit Theorem, which is a seminal theorem in Statistics.  In very simple terms, the theorem states that any arbitrary probability distribution can produce a **normal** distribution if you run the procedure enough times and consider the averages (or sums, in our case) of the outcomes.

The program uses rolling dice and taking the **sum of the roll** as an example.  

## [Click here to find a downloadable executable from GitHub.](https://github.com/mikeverwer/roll-dice/releases)

---

## Description

The user can choose an arbitrary probability distribution for the faces of a six sided die by using auto-adjusting sliders.  There are also some useful presets and a randomizer.  The user also enters the number of dice to roll per trial, $n$, and the number of trials to simulate, *T*.  

As you change the number of dice or the distribution of the die, a graph displaying the *theoretical probability distribution* for throwing that many dice is updated.  This graph is called the **convolution** of the die distribution.  You can interact with it by clicking the bars, which will display the outcome and its likelihood.  

As the theorem proposes, the theoretical prediction becomes more and more *Normal* shaped as the number of dice to be rolled increases.  Even the most skewed starting die distributions become *Normal* by 30 dice per roll.

Press `Roll!` to begin the simulation.  The outcome of each die is displayed as the rolls occur, and each roll is place as a block on an axis of all the possible outcomes$^{[1]}$.  This builds a dot-plot of all the rolls.  Each roll is remembered and can be displayed by selecting its block.

Selecting a bar on the convolution graph, or clicking on one of the bins below the x-axis of the simulation, will highlight that column on both graphs.  This is useful to keep track of a specific outcome as the rolls occur, and compare the predicted outcomes to the actual ones.

![UI Screen Shot](/assets/images/roll-dice-ss.png)

I find this to be a very useful tool to watch the CLT in action, and 'prove' the theorem to students in a purely visual way.  It is also an excellent way to reinforce the idea that theoretical outcomes for stochastic procedures are inherently unreliable for small sample sizes. The best way to show this is by setting the distribution to the `Fair` preset and rolling 1 die. Even with 200 rolls, the resulting outcomes will usually be wildly imbalanced.  However, if you increase it to 1000 or 2000 rolls, the results will still be imbalanced ***but***, relative to how many outcomes there were in each bin, they are actually quite close.

---

$^{[1]}$: Starting at 15 dice per roll, the outcomes get trimmed since the extremes of possible outcomes become highly improbable.  This has the unfortunate side effect of 'centering' the convolution graph on the axis, which takes away some of the visual impact of adjusting the sliders and watching the graph morph and move from side to side.
