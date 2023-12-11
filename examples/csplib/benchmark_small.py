import subprocess

files = [
    "examples/csplib/prob005_auto_correlation.py",
    "examples/csplib/prob028_bibd.py",
    "examples/csplib/prob049_number_partitioning.py",
    "examples/csplib/prob054_n_queens.py"
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