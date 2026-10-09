# Entropy: the Bulls and Cows game

My goal with this project is to understand entropy and how to use it to solve
the Bulls and Cows game.

## What is entropy?
The simplest way I think about it: entropy measures how many yes/no questions
you need, on average, to solve the game.

For example, in Bulls and Cows there are 9000 possible secrets (1000 to 9999).
If we suppose that each is equally likely, each one has probability
p = 1/9000 of being the answer.

How many yes/no questions would you need to find the secret?

    -sum(p * log2(p)) = -9000 * (1/9000) * log2(1/9000) = log2(9000) = 13.14

This gives us 13.14 bits of uncertainty.

2^~13.14 = 9000

## Information from one guess
Suppose you make a guess, and the guess results in a pattern that reduces the
number of remaining possibilities to 4500. How many bits of uncertainty are we
left with?

    -log2(1/4500) = 12.14

We started with 13.14 and ended up with 12.14 after the guess: we gained
1 bit of information. This makes sense because we just cut the remaining
possibilities in half, i.e. we answered 1 yes/no question (got 1 bit of
information).

Let's view this from the perspective of this single guess. The guess gives you
a bulls and cows pattern. What is the probability of getting that pattern? It
is 1/2, because it left us with half of the numbers: it reduced the possible
secrets by half, from 9000 to 4500. So when we made that guess and got the
feedback (or in general, when we made that observation), we got -log2(p) bits
of information:

    -log2(1/2) = 1

This also makes sense because an event that has a 50% probability of occurring
"cuts" the possibilities in half.

What if we made a guess whose pattern left us with 8 possibilities? The
probability of getting such a pattern is 8/9000. The information we gained is
-log2(8/9000) = 10.14. And if we subtract, 13.14 - 10.14 = 3: there are 3 bits
of uncertainty left in the 8 possible secrets. Again, we need 3 yes/no
questions to be sure of the answer.

## The main concepts
Before discussing how to use this to select the next guess, let me reiterate.

- **Initial entropy:** E[I] = -sum(p * log2(p))
- **Information of an observation:** an observation with probability P gives
  us -log2(P) bits of information. The rarer the observation, the fewer
  possibilities are left, and the more information we gained.
- **Remaining entropy after an observation** is either:
  1. E[I_initial] - (-log2(P_observation)), or
  2. E[I_after_observation], calculated in the same way as E[I_initial].

  And E[I_initial] - E[I_after_observation] is the information gained by the
  event, -log2(P_observation).

## Choosing a guess with entropy
One strategy is to iterate over all possible bulls and cows patterns and see
how likely they are:

    for each guess G from 1000 to 9999:
        for each secret S from 1000 to 9999:
            G gives B bulls and C cows for S
            counter[B, C] += 1

        for each pattern: p(B, C) = counter[B, C] / 9000
        information(G) = -sum(p * log2(p))

After the outer loop, we have computed the information of every guess, so we
can choose the guess that gives us the most information.

**Note 1:** this is the general idea, but the implementation is heavily
vectorized for performance reasons.

**Note 2: why the entropy of the patterns is the information of the guess.**
This is actually the weirdest part, and it turns out to make this game a much
more complicated example than it sounds.

It is not so in the Find the Sub game. There we compute the information gain
directly:

    information gain = H(now) - E[H(after the ping)]

In Bulls and Cows we could do the same, and we would get the same number (for
1234: 2.75 bits either way). It's just that there is a shortcut here.

My intuition is the following:
- A guess can produce several patterns, each with its own probability p.
- Seeing a pattern gives us -log2(p) bits of information about the secret.
- So the information we expect from the guess is the sum, over the patterns,
  of the probability of each pattern times the information it gives us:
  sum(p * (-log2(p))).
- And that is exactly the entropy formula, -sum(p * log2(p)).

Both ways need the same pattern counts; the shortcut just skips computing
H(now) and the entropy left after each pattern. Looking back, for learning
entropy the shortcut was not the best choice: it hides the "before minus
after" idea that makes information gain intuitive. To learn information gain,
start with the Find the Sub game, which computes it the direct way.
