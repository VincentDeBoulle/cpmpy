import subprocess

files = ["examples/csplib/prob110_peaceably_co-existing_armies_of_queens.py",
         "examples/csplib/prob006_golomb.py"
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