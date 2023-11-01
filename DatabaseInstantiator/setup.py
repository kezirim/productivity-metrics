import subprocess

# Create a Docker volume
create_volume_command = "docker volume create mongo_data"

# Run MongoDB in a Docker container
run_mongo_command = (
    "docker run -d -p 28000:27017 -v mongo_data:/data/db --name mongodb_container mongo"
)

subprocess.run(create_volume_command, shell=True)
subprocess.run(run_mongo_command, shell=True)
