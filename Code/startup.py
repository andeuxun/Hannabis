import subprocess
import time

def run_scripts():
    # Execute the server script
    server_process = subprocess.Popen(['/usr/local/bin/python3.10', '/Users/antoinebois-berlioz/INSA/3TC/PPC/serveur.py'])

    # Wait for 1 second
    time.sleep(1)

    # Send "1" to the terminal
    subprocess.run('echo "1"', shell=True)

    # Execute the client script
    time.sleep(1)
    client_process = subprocess.Popen(['/usr/local/bin/python3.10', '/Users/antoinebois-berlioz/INSA/3TC/PPC/client.py'])

    # Wait for the client process to finish
    client_process.wait()

    # Terminate the server process after the client is done
    server_process.terminate()

if __name__ == "__main__":
    run_scripts()
