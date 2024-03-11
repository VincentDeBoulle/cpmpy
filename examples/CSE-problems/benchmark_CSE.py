import subprocess

files = [
    "examples/CSE-problems/duplicates.py",
    "examples/CSE-problems/permutations.py",
    "examples/CSE-problems/common_subs.py",
    "examples/CSE-problems/knights_tour.py"
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