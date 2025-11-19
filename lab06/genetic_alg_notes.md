# Genetics Algorithm
## GA steps
1. Population initialization
  randomly creating initial set of chromosomes
2. Fitness evaluation
  calculating the function result for each individual
3. Selection
  Selecting parental choromosomes based on their evaluation
4. Crossover
  Genes parts from chromosomes exchange between parents with `Pc` possibility
5. Mutation
  Random changes of separate bits in chromosome with `Pm` chance
6. Preparing the new generation
  Creation of a new population, cycle repeats


The process cycles `G` times

## Initial parameters

Population number -     `N` = 4 (4-20)
Chromosome Length -     `L` = 4 (number of bits for encoding the variable)
Crossover chance -      `Pc` = 0.8 (0-1)
Mutation chance -       `Pm` = 0.05 (0-1)
Number of Generations - `G` (>=30)