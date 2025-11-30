import subprocess
from argparse import ArgumentParser

NUM_VERTICES = 0
EDGES = set()

def load_instance(input_file_name):
    
    # read a graph, return the set of edges
    # update global NUM_VERTICES and EDGES
    
    global NUM_VERTICES, EDGES
    EDGES = set()
    
    with open(input_file_name, 'r') as file:
        for line in file:
            line = line.strip()
            # skip empty lines or lines starting with 'c'
            if not line or line.startswith('c'):
                continue
            
            parts = line.split()
            if line.startswith('p'):
                # line starts with 'p' and contains number of vertices and edges
                NUM_VERTICES = int(parts[2])
            elif line.startswith('e'):
                # line starts with 'e' and shows an edge between two vertices
                u, v = int(parts[1]), int(parts[2]) # vertices as integers u and v.
                
                if u != v:
                    # store edge as sorted tuple to avoid same edges
                    EDGES.add(tuple(sorted((u, v))))
    
    return EDGES

def get_counter_id(i, j, partial_sum_vars):
    
    # manage additional variables for the sequential counter
    # return variable ID representing the logical proposition
    
    # if count <= 0, always True
    if j <= 0: 
        return "TRUE"
    # if count > number of seen items, always False
    if j > i: 
        return "FALSE"
    
    # if variable does not exist, create new number
    # calculate number depending on how many variables created using NUM_VERTICES
    if (i, j) not in partial_sum_vars:
        new_num = NUM_VERTICES + len(partial_sum_vars) + 1
        partial_sum_vars[(i, j)] = new_num
    
    return partial_sum_vars[(i, j)]

def encode(instance, clique_size):
    
    # encodes the decision problem
    # args: instance, clique_size
    # return: cnf, total number of variables used
    
    cnf = []
    partial_sum_vars = {} 
    
    # iterate over pair of distinct vertices
    # if a pair does not have an edge connecting them in the graph, it is not possible to select them for the clique
    # add a clause (NOT u) or (NOT) v
    for u in range(1, NUM_VERTICES + 1):
        for v in range(u + 1, NUM_VERTICES + 1):
            if tuple(sorted((u, v))) not in EDGES:
                cnf.append([-u, -v, 0])

    # count if selected at least 'clique_size' vertices
    # partial_sum_vars[(i, j)]: among the first 'i' vertices, selected at least 'j' of them
    for i in range(1, NUM_VERTICES + 1):
        # build counter up to 'clique_size'
        for j in range(1, min(i, clique_size) + 1):
            
            # define when 'var_current_count' is TRUE
            
            curr = get_counter_id(i, j, partial_sum_vars)
            prev_same = get_counter_id(i - 1, j, partial_sum_vars)
            prev_less = get_counter_id(i - 1, j - 1, partial_sum_vars)
            curr_index = i 

            # skip if curr determined
            if curr == "FALSE" or curr == "TRUE": 
                continue
            
            # case 1: count was at least 'j' at the previous step (i-1)
            # CNF: (NOT prev_same) OR current
            if prev_same != "FALSE" and prev_same != "TRUE":
                cnf.append([-prev_same, curr, 0])
            elif prev_same == "TRUE":
                cnf.append([curr, 0]) 

            # case 2: count was at least 'j-1' at the previous step, AND vertex 'i' is selected
            # if both true, total count increases to 'j'
            # CNF: (NOT vertex_var) OR (NOT prev_less) OR current
            if prev_less != "FALSE":
                clause = [curr, -curr_index]
                if prev_less != "TRUE":
                    clause.append(-prev_less)
                clause.append(0)
                cnf.append(clause)

             # if count is reached, vertices must be selected
            
            # clause 1: -curr OR prev_same OR prev_less
            clause1 = [-curr]
            if prev_same != "FALSE" and prev_same != "TRUE": clause1.append(prev_same)
            if prev_less != "FALSE" and prev_less != "TRUE": clause1.append(prev_less)
            clause1.append(0)
            
            if prev_less != "TRUE" and prev_same != "TRUE":
                 cnf.append(clause1)

            # clause 2: -curr OR prev_same OR curr_index
            clause2 = [-curr, curr_index]
            if prev_same != "FALSE" and prev_same != "TRUE": clause2.append(prev_same)
            clause2.append(0)

            if prev_same != "TRUE":
                cnf.append(clause2)

    # among the first N vertices, the count must be at least 'clique_size'
    # add a clause containing this variable, make it True.
    final_var = get_counter_id(NUM_VERTICES, clique_size, partial_sum_vars)
    if isinstance(final_var, int):
        cnf.append([final_var, 0])
    elif final_var == "FALSE":
        # if impossible, make UNSAT
        cnf.append([1, 0])
        cnf.append([-1, 0]) 
    
    nr_vars = NUM_VERTICES + len(partial_sum_vars)
    return (cnf, nr_vars)

def call_solver(cnf, nr_vars, output_name, solver_name, verbosity):
    
    # write CNF, run Glucose
    # return: subprocess result

    # write the CNF formula to a file in DIMACS format
    with open(output_name, "w") as file:
        file.write("p cnf " + str(nr_vars) + " " + str(len(cnf)) + '\n')
        for clause in cnf:
            file.write(' '.join(str(lit) for lit in clause) + '\n')
    
    # run the SAT solver as a subprocess to get variables
    return subprocess.run([solver_name, '-model', output_name], stdout=subprocess.PIPE, text=True)

def print_result(result, verbosity):
    
    # parse the solver's output
    # return: list of vertices in the clique if SAT, or None if UNSAT
    # optionally print solver statistics
    
    if result is None: 
        return None
    output = result.stdout
    
    if not output:
        return None
    
    # print statistics if verbosity is 1
    if verbosity > 0:
        for line in output.split('\n'):
            if line.startswith('c'):
                print(line)

    if "UNSATISFIABLE" in output:
        return None

    # parse the variable assignments
    model = []
    for line in output.split('\n'):
        if line.startswith("v"):
            # skip 'v' and parse integers
            parts = line.split()
            for part in parts:
                if part == 'v': continue
                val = int(part)
                if val != 0:
                    model.append(val)
    
    # keep only positive variables corresponding to vertices
    clique = []
    for v in model:
        if 1 <= v <= NUM_VERTICES:
            clique.append(v)
    
    if clique:
        return clique
        
    return None

if __name__ == "__main__":

    parser = ArgumentParser()

    parser.add_argument(
        "-i",
        "--input",
        required=True,
        type=str,
        help=(
            "The instance file."
        ),
    )

    parser.add_argument(
        "-o",
        "--output",
        default="formula.cnf",
        type=str,
        help=(
            "Output file for the DIMACS format (i.e. the CNF formula)."
        ),
    )

    parser.add_argument(
        "-s",
        "--solver",
        default="glucose",
        type=str,
        help=(
            "The SAT solver to be used."
        ),
    )

    parser.add_argument(
        "-v", 
        "--verb", 
        default=1, 
        type=int, 
        choices=range(0,2), 
        help=(
            "Verbosity of the SAT solver used."
        ),
    )
    
    args = parser.parse_args()

    # get input instance
    load_instance(args.input)

    max_clique = []
    curr_size = 1
    
    # find maximum clique size
    while curr_size <= NUM_VERTICES:
        # pass instance to encode
        cnf, nr_vars = encode(EDGES, curr_size)
        
        # run the solver
        result = call_solver(cnf, nr_vars, args.output, args.solver, args.verb)
        
        # parse result
        clique = print_result(result, args.verb)
        
        if clique:
            # if found a clique of this size, save and try to find a bigger one
            max_clique = clique
            curr_size += 1
        else:
            # if no clique of this size exists, stop
            break
    
    # print result
    if max_clique:
        print(f"Maximum Clique Size: {len(max_clique)}")
        print("Vertices: " + " ".join(str(v) for v in sorted(max_clique)))
    else:
        if NUM_VERTICES > 0:
            print("No clique found.")
