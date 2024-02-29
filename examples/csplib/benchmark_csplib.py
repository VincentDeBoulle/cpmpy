import subprocess

files = [
    "examples/csplib/prob002_template_design.py",
    "examples/csplib/prob005_auto_correlation.py",
    "examples/csplib/prob006_golomb.py",
    "examples/csplib/prob007_all_interval.py",
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