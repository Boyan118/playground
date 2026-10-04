# Bayesian search: the sub game

## Setup
- A map of squares.
- A **prior**: how likely the sub is to be in each square. It could be because
  subs prefer to hide in certain squares, or because we have some other reason
  to believe where they might hide.
- A **ping sensor**: a process for searching one square. It is inaccurate and
  expensive.

Sensor spec, for a ping on square X:

| Where the sub is      | P(Det_X) | P(ND_X) |                                  |
|-----------------------|----------|---------|----------------------------------|
| in X                  | 0.8      | 0.2     | a miss is a false negative       |
| next to X             | 0.25     | 0.75    | a detect is a false positive     |
| far from X            | 0.001    | 0.999   | a detect is a false positive     |

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
