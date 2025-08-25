# Playing with Primes

This application has two major components.  One is a widget that performs and animates the Sieve of Eratosthenes, which
is an ancient algorithm used to find prime numbers without requiring any division. The other is a widget that generates
the Novelty numbers, which is a non-positional numbering system I came up with that is based on prime factorization.
Check the links in the right sidebar for articles explaining each concept.

The application is built entirely in Python, using the last FOSS version of PySimpleGUI.

## [Click here to find a downloadable executable from GitHub.](https://github.com/mikeverwer/novelties/releases/)

---

## The Sieve Widget

This widget lets users specify a maximum number, and the simulation will find all prime numbers less than or equal to
that value. The animation starts by displaying all numbers from 2 up to the input value. It then follows the algorithm:
identifying the first unmarked number, highlighting it with a color specific to the prime, and marking all of its
multiples with the same color. Refer to the article in the sidebar for a more detailed explanation of the algorithm.

![UI Screen Shot](/assets/images/sieve-ss.png)

### Features

You can pause the animation at any time by pressing the Pause button, or by using the spacebar. The speed of the
animation can also be adjusted with the slider, or by using the `<`,  `>` keys.

The numbers in the animation display canvas can be selected to view any information that has been found so far by the
algorithm. If the selected number is composite, it will display the prime factors of it that have been found so far and
if it is prime you can see which colour was selected to box itself and scratch-out its multiples.

---

## The Novelty Widget

In this widget, the user inputs a maximum value and the widget will build all of the Novelty numbers up to that point.

Essentially, a novelty is just a number written as its prime factorization; but there is a twist.  The prime numbers act
as the unique digits of the system, similar to how I, V, X, ... work in the Roman Numerals. We label each prime
corresponding to its position in the list of all primes. For example, the number $1176 = (2^3)\cdot 3\cdot (7^2)$ would
be written as a novelty like so:  

> ***1 $\cdot$  1 $\cdot$  1 $\cdot$  2 $\cdot$  4 $\cdot$  4***

because  $2$ is the *first* prime and has three factors, $3$ is the *second* prime with one factor, and $7$ is the 
*fourth* prime having two factors.  
See the corresponding link for information on them as well.

![UI Screen Shot](/assets/images/novelties-ss.png)

### Features

The chart is interactive, you can click any of the cells and its corresponding natural value and prime factorization
will be displayed. You can also change the ordering of the chart between the natural order of numbers and the novelty
ordering. Recall that a novelty representation of a number is the concatenation of all the primes it is composed of,
and each prime acts as a 'digit' in the representation. Therefore, the primes are all single digit values and so appear
first in the novelty ordering.

There is also a popup conversion chart between the primes and their ordinal value in the list of primes.
