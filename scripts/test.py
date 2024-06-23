import subprocess
import os
import time

def create_sandbox():
    project_dir = "./codesandbox_project"
    os.makedirs(project_dir, exist_ok=True)

    try:
        # Create the necessary files
        files = {
            "index.html": """
<!DOCTYPE html>
<html>
<head>
    <title>Hello World Button</title>
</head>
<body>
    <button id="helloButton">Click me!</button>
    <script src="index.js"></script>
</body>
</html>
            """,
            "index.js": """
document.getElementById("helloButton").addEventListener("click", function() {
    console.log("Hello, world, ruv!");
    alert("Hello, world, ruv!");
});
            """,
            "package.json": """
{
    "dependencies": {}
}
            """
        }

        # Create the files in the project directory
        for filename, content in files.items():
            with open(os.path.join(project_dir, filename), 'w') as f:
                f.write(content)

        # Wait for the filesystem to complete the file creation
        time.sleep(2)

        # Check that the files are created and available
        for filename in files.keys():
            file_path = os.path.join(project_dir, filename)
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File {file_path} does not exist")

        # Run the CodeSandbox CLI command with automatic "yes" response
        result = subprocess.run(
            ["codesandbox", project_dir],
            input="y\n",
            capture_output=True,
            text=True,
            timeout=60  # Set a timeout of 60 seconds
        )

        # Check if the command was successful
        if result.returncode == 0:
            print("CodeSandbox CLI output:")
            print(result.stdout)
            
            # Extract the sandbox URL from the output
            for line in result.stdout.split('\n'):
                if line.startswith("https://codesandbox.io/s/"):
                    print(f"Sandbox URL: {line.strip()}")
                    return
            
            print("Sandbox URL not found in the output.")
        else:
            print(f"Error running CodeSandbox CLI. Return code: {result.returncode}")
            print("Error output:")
            print(result.stderr)

    except subprocess.TimeoutExpired:
        print("The CodeSandbox CLI command timed out after 60 seconds.")
    except subprocess.CalledProcessError as e:
        print(f"Error running CodeSandbox CLI: {e}")
        print("Error output:")
        print(e.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    create_sandbox()
