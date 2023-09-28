# 2048 Monto Carlo Solver

_By Asger Thousig Sehested(s234811), Benjamin Banks(s234802) og Lucas R.G. Pedersen(s234842)_

## Introduction

This was made for a project for a course a DTU September 2023. The following is frow our report:

> We aim to optimize one of our algorithms: 2048 Monto Carlo Solver (2MCS) for the score, given by the usual 2048 rules . We will optimize for 2 of Monto Carlo Search’s (MCS) most significant parameters. Firstly, how many simulations run for each potential move - referred to as simulation count (SC). Secondly, how many random moves each simulation makes after the initial move being examined - referred to as maximum search depth (MSD).
>
> We want to test our hypothesis that there exists an optimal MSD (that isn’t a limit) for each SC, and that a higher SC leads to a higher optimal MSD. We believe this is the case, as an MSD that is too low doesn’t provide enough information about the long-term consequences of potential moves, and one that is too high provides information too influenced by the random moves of the simulation and not the initial move we want to examine. A higher SC mitigates the effect of randomness, meaning the MSD can be higher without providing random information.

The code is well documented,

## Requirements

You need to have [Python3](https://www.python.org/downloads/) installed.

When installed, run the following to install the required python packages:

```console
pip install pygame, numpy
```

Run the acutal script by running:

```
python AI_Game2048.py
```

Play the game yourself by running:

```
python Play_Game2048.py
```

## Explenation

[Game2048.py](Game2048.py?plain=1#L4) is the game. You you find functions related to the game mechnics for 2048.

[AI_Game2048.py](AI_Game2048.py) is our 2MCS. You can change the following parameters:

-   Set the simulation_count(SC): [`line 14`](AI_Game2048.py?plain=1#L14)
-   Set the max_simulation_depth - MSD (read below): [`line 94`](AI_Game2048.py?plain=1#L94)
-   Disable or enable rendering of the game: [`line 116`](AI_Game2048.py?plain=1#L116)

As standard the script will simulate a specific max_simulation_depth(MSD) until the confidence interval of the mean score is 95%. After that i will take the next max_simulation_depth.
