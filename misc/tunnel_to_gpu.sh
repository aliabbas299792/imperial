#!/usr/bin/env python3

"""
Script for tunneling into a GPU machine
Assumes you have setup SSH key based authentication
"""

import argparse
import subprocess

GET_GPU_MACHINE_CMD = "/vol/linux/bin/freelabmachine -c 'regexp( \"gpu\", Machine)'"
LOGIN_SERVER = "shell3.doc.ic.ac.uk"


def run_remote_command(username, server, command):
    ssh_command = ["ssh", f"{username}@{server}", command]
    result = subprocess.run(ssh_command, capture_output=True, text=True)
    return result.stdout, result.stderr


def main():
    parser = argparse.ArgumentParser(description="SSH tunnel to GPU machine")
    parser.add_argument(
        "--local_port",
        type=int,
        default=8888,
        help="Local port number (default: 8888)",
    )
    parser.add_argument(
        "--remote_port",
        type=int,
        default=8888,
        help="Remote port number (default: 8888)",
    )
    parser.add_argument("username", type=str, help="Imperial shortcode")
    args = parser.parse_args()

    gpu_machine, _ = run_remote_command(
        args.username, LOGIN_SERVER, GET_GPU_MACHINE_CMD
    )

    ssh_command = [
        "ssh",
        "-L",
        f"{args.local_port}:localhost:{args.remote_port}",
        "-A",
        "-J",
        f"{args.username}@{LOGIN_SERVER}",
        f"{args.username}@{gpu_machine.strip()}",
    ]
    subprocess.run(ssh_command)


if __name__ == "__main__":
    main()

