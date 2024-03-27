import subprocess
import os
import sys


# Function to get a list of all files in the git repository
def get_git_files(repo_path):
    prev_dir = os.getcwd()  # Save the current directory
    os.chdir(repo_path)  # Change to the repository directory
    files = (
        subprocess.check_output(["git", "ls-files"], cwd=repo_path)
        .decode("utf-8")
        .strip()
        .split("\n")
    )
    os.chdir(prev_dir)  # Change back to the previous directory
    return files


# Function to compile files into a single text file
def compile_files_into_text(files, repo_path, output_path):
    with open(output_path, "w") as outfile:
        for file in files:
            # Skip binary files like images
            if file.endswith(".png"):
                print(f"Skipping binary file: {file}")
                continue
            # Prefix with file name and path
            outfile.write(f"\n\n--- {file} ---\n\n")
            file_path = os.path.join(repo_path, file)
            try:
                with open(file_path, "r") as infile:
                    outfile.write(infile.read())
            except Exception as e:
                print(f"Error reading {file}: {e}")


if __name__ == "__main__":
    repo_path = "/Users/roland/code/Nur_dev"
    output_path = "/Users/roland/code/Nur_dev/content/repo_context/mdgrey33_nur.txt"
    git_files = get_git_files(repo_path)
    compile_files_into_text(git_files, repo_path, output_path)
    print(f"Compilation complete. Output file: {output_path}")
