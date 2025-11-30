**Maximum Clique Solver**

This is a solution for the Maximum Clique problem. The provided Python code encodes, solves, and decodes the problem via reduction to SAT.

The SAT solver used by default is Glucose. The Python script calls the solver as a subprocess.


**Problem Description**

The Maximum Clique problem challenges the user to find the largest subset of vertices in a graph such that every two distinct vertices in the clique are adjacent. Formally, for a graph G=(V, E), a clique is a subset C of V such that for every u, v in C, if u is not equal to v, then (u, v) is in E.

An example of a valid input format is:


c graph with 3 vertices, 3 edges

c maximum clique is 3

p edge 3 3

e 1 2

e 2 3

e 1 3



Where lines starting with c are comments. The line starting with p defines the number of vertices, and the number of edges. Lines starting with e define an edge between vertex u and vertex v.


**Encoding**


To find the Maximum Clique, the code solves a sequence of decision problems. SAT solver answer Yes or No to a specific formula, so we cannot ask for the maximum.

So, we use an iterative way:

1) Start with a target clique size K = 1

2) Check if a clique of size K exist?

3) Run the SAT solver.

   * If SAT: Store the result and try K = K + 1

   * If UNSAT: The largest successful K is the maximum size
     

For each step K, we generate a specific CNF formula using the following constraints:

If two vertices u and v are not connected by an edge in the input graph, they can not both be in the clique.

Variable S_{i,j} is true if and only if the count reaches j after seeing vertex i.

We make sure that the final counter variable S_{N, K} must be TRUE.

 
 
**User documentation**
 

 
Basic usage:

python3 max_clique.py [-h] [-i INPUT] [-o OUTPUT] [-s SOLVER] [-v {0,1}]



Command-line options:

-h, --help : Show a help message and exit.

-i INPUT, --input INPUT : The instance file in DIMACS format (Required).

-o OUTPUT, --output OUTPUT : Output file for the generated CNF formula. Default: formula.cnf.

-s SOLVER, --solver SOLVER : The path to the SAT solver executable. Default: glucose.

-v {0,1}, --verb {0,1} : Verbosity of the SAT solver output.

 

**Example instances**

 
triangle.clq: A graph with 3 vertices and 3 edges

square.clq: A graph with 4 vertices and 4 edges

 
**Experiments**
 

Experiments were run on a MacBook Air M3.
 

Instance: triangle.clq

 
Clique Size (K) ************************ Time (s) ********************* Result

1 *************************************** 0.001 ************************ SAT

2 *************************************** 0.001 ************************ SAT

3 *************************************** 0.001 ************************ SAT


Instance: square.clq


Clique Size (K) ************************ Time (s) ********************* Result

1 *************************************** 0.001 ************************ SAT

2 *************************************** 0.001 ************************ SAT

3 *************************************** 0.001 *********************** UNSAT
