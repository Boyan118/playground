# Bayesian search: the sub game

## Goal
- Learn about Bayes' theorem.

But it also turned out to be an excellent playground for:
- understanding how to apply entropy, and how to use it to find the next
  square to ping;
- understanding, in a very intuitive setting, how to read a confusion matrix.

## Setup
- A map of squares.
- A **prior**: how likely the sub is to be in each square. It could be because
  subs prefer to hide in certain squares, or because we have some other reason
  to believe where they might hide.
- A **ping sensor**: a process for searching one square. It is inaccurate and
  expensive.

Sensor spec, for a ping on square X:

| Where the sub is      | P(Det_X) | P(ND_X) |                                              |
|-----------------------|----------|---------|----------------------------------------------|
| in X                  | 0.8      | 0.2     | a miss is a false negative (Type II error)   |
| next to X             | 0.25     | 0.75    | a detect is a false positive (Type I error)  |
| far from X            | 0.001    | 0.999   | a detect is a false positive (Type I error)  |

Notation: `Det_X` means "we pinged X and got a Detect", and `ND_X` means "we
pinged X and got No_Detect".

## Bayes' theorem
In its raw form (A and B here are events, not squares):

    P(A|B) = P(B|A) * P(A) / P(B)

For us: P(sub in S | outcome) = P(outcome | sub in S) * P(S) / P(outcome).

## Example
Four squares in a row. The sub is really in C.

    A     B     C     D
    0.4   0.1   0.3   0.2     <- prior

### Ping A, get No_Detect
We want P(A|ND_A) = P(ND_A|A) * P(A) / P(ND_A).

- **P(A)** is the prior: 0.4.
- **P(ND_A|A)** is the probability of No_Detect given the sub is in A. From the
  spec: 0.2.
- **P(ND_A)** is the total probability of getting No_Detect at A. It can
  happen in four ways, one for each square the sub could be in:
  - sub in A: P(ND_A|A) * P(A) = 0.2 * 0.4 = 0.08
  - sub in B (next to A): P(ND_A|B) * P(B) = 0.75 * 0.1 = 0.075
  - sub in C (far from A): P(ND_A|C) * P(C) = 0.999 * 0.3 = 0.2997
  - sub in D (far from A): P(ND_A|D) * P(D) = 0.999 * 0.2 = 0.1998

  P(ND_A) = 0.08 + 0.075 + 0.2997 + 0.1998 = **0.6545**

The same denominator gives the whole updated map:

| Square | P(ND_A\|S) * P(S) | P(S\|ND_A) |
|--------|------------------|-----------|
| A      | 0.08             | 0.1222    |
| B      | 0.075            | 0.1146    |
| C      | 0.2997           | 0.4579    |
| D      | 0.1998           | 0.3053    |

### Ping A, get Detect
We want P(A|Det_A) = P(Det_A|A) * P(A) / P(Det_A).

- sub in A: P(Det_A|A) * P(A) = 0.8 * 0.4 = 0.32
- sub in B (next to A): P(Det_A|B) * P(B) = 0.25 * 0.1 = 0.025
- sub in C (far from A): P(Det_A|C) * P(C) = 0.001 * 0.3 = 0.0003
- sub in D (far from A): P(Det_A|D) * P(D) = 0.001 * 0.2 = 0.0002

P(Det_A) = **0.3455**

| Square | P(S\|Det_A) |
|--------|------------|
| A      | 0.9262     |
| B      | 0.0724     |
| C      | 0.00087    |
| D      | 0.00058    |

Either way, the updated map becomes the prior for the next turn.

## Checks and takeaways
- **Sanity check:** a ping has only two outcomes, so
  P(ND_A) + P(Det_A) = 0.6545 + 0.3455 = 1. Each updated map must also sum
  to 1.
- **The true position never enters the math.** That the sub is really in C
  only decides which outcome the real sensor tends to produce (here, No_Detect
  at A 99.9% of the time). The update uses only the prior and the sensor spec.
  This is why the sensor's spec (what the searcher knows) and the real world
  (where the sub is) are separate things. See finding #6 in
  `sub_game_review.md`.

## How to use entropy to decide which square to ping
The formula for entropy is

    H = -sum(p * log2(p))

The sum is over all the squares, and p is the probability that the sub is in
the square. The result is the uncertainty in bits. In other words, it is the
number of ideal yes/no questions we need to ask, on average, to solve the game.

We can calculate the entropy of the map now, H(now). Then for each square we
have two options:
- ping and get a Detect;
- ping and get a No_Detect.

As in the calculations above, we can work out the updated map for each
option, and therefore calculate the entropy of each updated map: H(after Det)
and H(after ND).

The expected entropy after the ping weights the two by how likely they are:

    E[H(after)] = P(Det) * H(after Det) + P(ND) * H(after ND)

where P(Det) is the denominator from the Bayes update above (0.3455 for a ping
on A), and P(ND) = 1 - P(Det).

The information gain is how much the ping is expected to reduce the entropy:

    information gain = H(now) - E[H(after)]

Calculating this for all squares lets us choose the square with the biggest
information gain.

A really cool experiment is to look at the moves recommended by this criterion,
starting with a uniform map.


## How to interpret a confusion matrix
Let's simplify the specification of the ping sensor in the following way:
- if the sub is in the square, there is an 80% probability to get a positive
  reading, and 20% to get a negative reading (false negative, Type II error);
- if the sub is not in the square, there is a 5% probability to get a positive
  reading (false positive, Type I error), and 95% to get a negative reading.

Let's place this into a table (each row sums to 100%):

|                   | Sensor: 1 | Sensor: 0 |
|-------------------|-----------|-------------------|
| **Actual: 1** (sub there)    | 80% (TP)  | 20% (FN, Type II) |
| **Actual: 0** (no sub)       | 5% (FP, Type I) | 95% (TN)  |

In statistics, a false positive is a **Type I error** and a false negative is
a **Type II error**. Their rates are called α (here 5%) and β (here
20%), and 1 - β is the power (80%), which is the same as recall below.

We can think of the sensor as an ML model too: a classifier. But for me the
sensor version became an easy mental shortcut to reason about the problem
intuitively.

What is the accuracy of this sensor/model? Accuracy measures, out of all the
trials, how many times we got the correct result. Let's suppose there are 10
squares with a sub and 1000 squares without one:

    TP = 80% of 10   = 8
    FN = 20% of 10   = 2
    TN = 95% of 1000 = 950
    FP =  5% of 1000 = 50

    accuracy = (TP + TN) / (TP + FP + TN + FN) = 958 / 1010 = ~95%

But if you get a positive, the probability that it is a true positive is
TP / (TP + FP) = 8 / 58 = ~14%. This might be a little surprising, given that
the accuracy of the sensor is 95%. The reason: there are so many empty squares
that their 5% false positives (50) swamp the real detections (8). Accuracy
even rewards a useless sensor: one that always says 0 would get
1000 / 1010 = ~99%.

There are two popular metrics that address this:
- **Recall:** TP / (TP + FN) = 8 / 10 = 80%. If the sub is really in the
  square, how often does the sensor detect it?
- **Precision:** TP / (TP + FP) = 8 / 58 = ~14%. If the sensor gives a
  positive, how often is the sub really there?

