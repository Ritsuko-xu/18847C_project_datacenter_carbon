from helpers import *
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("ssh_comms", metavar="ssh-comms", type=str, help="text file with ssh commands line by line")
    parser.add_argument("governor", type=str, default="performance", help="governor to set")
    parser.add_argument("--just-print", action="store_true", help="just print the governors and exit")
    return parser.parse_args()

def set_governor(governor, nodes):
    asyncio.run(run_remote_async(nodes, f"./set_governor.sh {governor}", check=True))

def print_governors(nodes):
    output = asyncio.run(run_remote_async(nodes, f"cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor | uniq"))
    for o in output:
        print(o[0].strip())

def main():
    args = parse_args()
    nodes, _ = parse_ssh_file(args.ssh_comms)
    if not args.just_print:
        set_governor(args.governor, nodes)
    print_governors(nodes)

if __name__ == "__main__":
    main()