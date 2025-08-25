# The Sieve of Eratosthenes

The Sieve of Eratosthenes (Air-Uh-Toss-The-Knees) is an ancient algorithm developed by the greek polymath, [Eratosthenes of Cyrene](https://en.wikipedia.org/wiki/Eratosthenes) (c. 276 BC – c. 195/194 BC).  The algorithm describes a very simple way to find all prime numbers up to a maximum value, $n$, and it does so without the use of multiplication or division.  This is notable since division, in particular, is [slow](https://en.wikipedia.org/wiki/Computational_complexity_of_mathematical_operations).  See the [wikipedia article](https://en.wikipedia.org/wiki/Division_algorithm#Fast_division_methods) on division algorithms for more information on slow vs. fast division methods.

The naive way to consider such a task is to simply check if each number, $x$,  up to $n$ is prime. Checking for primality is computationally difficult, although in 2002 (after *literally* **thousands** of years of thought) it *was* shown to be in the [complexity class P](https://en.wikipedia.org/wiki/P_(complexity)).  This difficult task needs to be done for every number $x$ less than $n$.  

The simple approach to testing some number, $x$, for primality is to divide $x$ by every number less than the square root of $x$.

> We can stop at the square root of $x$ since $\sqrt{x}$ is the multiplicative "half-way point".  That is, when I find a factor less than $\sqrt{x}$ I also find it's corresponding factor larger than $\sqrt{x}$.  For example, if I list out all the integers $a$, and $b$ such that $a \cdot b = 30$, I get the following:  
>
> | $a$ | $b$ |
> |-|-|
> | 1 | 30 |
> | 2 | 15 |
> | 3 | 10 |
> | 5 | 6 |
> | 6 | 5 |
> | 10 | 3 |
>
> At this point I have started to find redundant factors, this is because we have passed over $\sqrt{30} \approx 5.47$.

The process can be optimized a bit by only dividing by *prime* numbers less than $\sqrt{x}$.  The problem with this is the need for a list of primes up to $\sqrt{x}$, which makes the optimization ineffective for large $x$.

## The Algorithm

The Sieve does not require any primality testing and only involves the use of addition.  The steps of the algorithm can be outlined as follows:

1. Generate the full list of numbers from $2$ to $n$.  
    > We can start at 2 since 1 is not prime, by definition.
2. Find the first unmarked value, $p$. This number is prime.
3. Move through the list and scratch out every $p^{\text{th}}$ number, since it is a multiple of $p$ and therefore not prime.
4. Repeat from step 2 until $ p \geq n$.
    > We found the end of the list.

In other words, we begin by assuming every number is a candidate for being prime. Instead of finding the numbers that *are* prime, we eliminate numbers that *aren't*. Begin at the number $2$, it is prime. Every multiple of $2$ is therefore not prime; remove them from the pool. The next candidate is $3$.  Since it is not a multiple of anything before it, it must be prime. Now remove all multiples of $3$... and so on.  

I think it is important to recognize here that we are not exactly removing all multiples of the prime, $p$.  That is, of course, the effect; but it isn't really the action.  We never actually have to check if the number we scratch out is a multiple of $p$.  We simply move $p$ units to the right and scratch out whatever we land on. Even though checking for divisibility by $p$ is *one* division check, it is **still** a division check, and therefore slow. All we ever do is count to $p$ over and over again until we reach the end of the list.  This is what makes the algorithm so amazing; finding primes, which are **defined** by division, without having to divide.

We can optimize step 3 by starting our search for multiples at $p^2$ instead of $2p$.  This is because every multiple of $p$ less than $p^2$ is a multiple of a prime less than $p$. Therefore, we have already scratched them all out when we found the smaller primes.  As an example, consider the first three primes, $2$, $3$, and $5$.  
>$2$ is prime and so we scratch out all multiples of $2$ and we move on to the next prime, $3$.  
Now we move three units to the right and land on $6$, but $6=2\times3$ so we scratched it out when we found all the multiples of $2$.  The first thing we have no information on is $3\times3 = 9 = 3^2$.  Start from here and scratch out all multiples of 3.  
When we move on to $5$, we know that $2\times5 =10$ was scratched out during the $2$'s and $3\times5=15$ was scratched out during the $3$'s.  $4\times5$ was also scratched out during the $2$'s since $4=2\times2$.  Therefore, we can start at $5^2=25$.

With the above optimization, we can rewrite the full implementation as follows:

1. Generate the full list of numbers from $2$ to $n$.  
    > We can start at 2 since 1 is not prime, by definition.
2. Find the first unmarked value, $p$. This number is prime.
3. Move through the list and scratch out every $p^{\text{th}}$ number beginning with $p^2$, since it is a multiple of $p$ and therefore not prime.
4. Repeat from step 2 until $p^2 > n$. All remaining unmarked values are prime. Complete.
    > At a certain point $p^2$ will be bigger than our maximum value, meaning we have nothing to scratch out anymore.  This will occur after $\sqrt{n}$ iterations.
