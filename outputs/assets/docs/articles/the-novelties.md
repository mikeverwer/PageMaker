# The Novelties

## Abstract

This program generates, what I call, the Novelties.  A member of the Novelties is called a *novelty*.

The Novelties use a non-positional number system where each novelty is represented as a concatenation of the primes it is composed of; however the primes are represented by the order in which they exist as primes.  

For example: the number $1176$, which has a prime factorization of $(2^3)(3)(7^2)$, would be written as a novelty as: ***1$\cdot$1$\cdot$1$\cdot$2$\cdot$4$\cdot$4***, since 2 is the first prime, 3 is the second, and 7 is the fourth.

### Introduction

Our understanding of quantities is based on an additive principle; where, to get from one number to the next, we add 1 (see the [Peano Axioms](https://youtu.be/3gBoP8jZ1Is?si=4pPOlf5IM-a0WDF2) for more details of this).  But this means that the essence of "one"-ness is found in having *one* thing, and "two"-ness is having *one* thing and then having another *one* thing, and "three-ness" is having *one* thing, having another *one* thing and then having **another** *one* thing, ... ad nauseam.  If that is the case, then each number is essentially just a different bundle of **ones**.  The idea of the novelties is to attribute **that** notion to our understanding of oneness.  In fact, it is such an obvious way to think of numbers, we give it the special name of "identity", which we denote with "***0***".  This implies that the natural number 1 is equal to ***0*** as a novelty, or \( 1 := ***0*** ).

The first *new* thing to encounter is having pairs of things, or equivalently, two copies of ***0***.  We could then learn everything there is to know about having different amounts of pairs.  How to add, subtract, multiply, divide, and every other conceivable thing there could be to know, we could learn it.  Since this is the **first** *novel* thing we have discovered, it would makes sense to consider this as our new notion of "oneness" and give it the symbol, ***1***.
The next new thing to encounter is having triples of things.  Here, again we could learn all there is to know about triples of things.  It being the second novel thing, we call this notion, "two" and give it the symbol ***2***.

See the image below for a visualization of the above.

![The first three novelties](/assets/images/first_three_novelties.png)

Now, it would seem that the next new thing would be to have quadruples. However, since a pair of pairs is 4 things, when we discovered pairs we also discovered quadruples. Since quintuples can not be reduced to pairs or triples, the next new thing will be: having quintuples of things. We call that "three" and give it the symbol, ***3***.

By the [Sieve of Eratosthenes](https://en.wikipedia.org/wiki/Sieve_of_Eratosthenes), we will only encounter new things when we encounter prime numbers, and so there will be **a unique novelty for each prime**.   In this expanded understanding of one-ness, two-ness, and so on, we are referencing the prime numbers by way of the [ordinal numbers](https://en.wikipedia.org/wiki/Ordinal_number).  

Before we describe the construction of an arbitrary novelty, let's point out that it still makes perfect sense for us to talk about all the quadruples, they just aren't *novel*.  They can, however, be broken down into **pieces** that are novel. Like we pointed out earlier, a quadruple is two copies of the novelty ***1***. We take the convention of writing this as 4 = ***1 $\cdot$  1***

## Definition

Let $O( n | S )$ denote the position of the element, $n$, in the set, $S$.  
Let $\mathbb{P}$ be the set of all prime numbers.  
> example: *O*( 5 | $\mathbb{P}$ ) = 3

1. For every natural number $n$, there is a unique novelty, ***N***
2. If $n$ is prime, ***N*** is a single "digit" novelty, and "digit" = *O*( $n$ | $\mathbb{P}$ )
3. If $n$ is composite: Find the prime factorization of $n$ and convert each prime to it's corresponding novelty digit. Concatenate the digits, separated by ' $\cdot$ ', adding as many copies of each digit as there are factors of the prime.

This definition implies that the Novelty number system has infinitely many digits.

### Remarks

In reality, what I have described here are the [residue classes](https://math.libretexts.org/Bookshelves/Combinatorics_and_Discrete_Mathematics/Elementary_Number_Theory_(Barrus_and_Clark)/01%3A_Chapters/1.21%3A_Residue_Classes_and_the_Integers_Modelo_m) of 0 mod *p* for all prime numbers, *p*.  The only difference is that I am choosing to enumerate them **not** by the prime *p*, but by the **position**  (or *ordinal*) of *p* in the list of all primes.

There is no real reason to do any of this, but I found it very interesting to think of a world in which the basic understanding of quantities was described **multiplicatively** instead of additively. In such a world, prime numbers would truly be considered the building blocks of numeracy, going so far as to say composite numbers don't even exist as unique entities. As another point of interest, the Novelties are an example of a non-positional numbering system where multiplication and division are trivial, while addition and subtraction are very hard.
  