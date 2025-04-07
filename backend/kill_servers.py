#!/usr/bin/env python3
import os
import sys
import subprocess
import signal

def kill_process_on_port(port):
    """Kill any process using the specified port."""
    try:
        # Find process ID using the port
        result = subprocess.run(
            f"lsof -i :{port} -t", 
            shell=True, 
            capture_output=True, 
            text=True
        )
        
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            print(f"Found processes using port {port}: {pids}")
            
            for pid in pids:
                if pid:
                    try:
                        # Kill the process
                        os.kill(int(pid), signal.SIGKILL)
                        print(f"Killed process {pid} on port {port}")
                    except Exception as e:
                        print(f"Error killing process {pid}: {str(e)}")
        else:
            print(f"No process found using port {port}")
            
    except Exception as e:
        print(f"Error checking port {port}: {str(e)}")

def main():
    """Kill processes on common API server ports."""
    print("Checking and killing servers on common ports...")
    
    # Common API server ports
    ports = [8000, 8001, 8080, 8081, 8082]
    
    for port in ports:
        kill_process_on_port(port)
    
    print("Done checking ports")

if __name__ == "__main__":
    main() 