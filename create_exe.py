import subprocess

# Define the command to run
command = "pyinstaller Youber.spec"
# Run the command in the shell
subprocess.run(command, shell=True)
