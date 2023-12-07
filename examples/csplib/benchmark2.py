import subprocess

files = ["examples/csplib/prob002_template_design.py",
         "examples/csplib/prob005_auto_correlation.py",
         "examples/csplib/prob026_sport_scheduling.py",
        "examples/csplib/prob049_number_partitioning.py",
         "examples/csplib/prob084_hadamard_matrix.py",
         "examples/csplib/prob028_bibd.py"
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