import subprocess

files = [
    "examples/csplib/prob007_all_interval.py",
    "examples/csplib/prob008_vessel_loading.py",
    "examples/csplib/prob009_perfect_squares.py",
    "examples/csplib/prob019_magic_sequence.py",
    "examples/csplib/prob028_bibd.py",
    "examples/csplib/prob049_number_partitioning.py",
    "examples/csplib/prob050_diamond_free.py",
    "examples/csplib/prob053_gracefull_graphs.py",
    "examples/csplib/prob054_n_queens.py",
    "examples/csplib/prob076_costas_arrays.py",
    "examples/csplib/prob084_hadamard_matrix.py",
]

for file_name in files:
    try:
        print(file_name)
        cmd = ["python", file_name]
        subprocess.run(cmd)
    except FileNotFoundError:
        print("Error: file {} not found".format(file_name))
    except Exception as e:
        print("Error running {}: {}".format(file_name, e))