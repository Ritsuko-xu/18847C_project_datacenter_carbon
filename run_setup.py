from helpers import *
from docker_services import get_node_ids
from update_swarm import cleanup, deploy_stack, set_compose_env
import argparse
import asyncio
import time
import os
import webbrowser
from set_governor import set_governor
from make_docker_compose import make_compose

GET_IPADDR = "hostname -I"
DSB_PATH = "~/DeathStarBench/{}/"
RUN_CONTAINER = f"cd {DSB_PATH} && sudo docker-compose up -d"
NGROK_SETUP = "sudo ngrok config add-authtoken 2GEGFS3Ug2CSJJXyS4Aml3LqeNe_5Jx6cTUZvetvWF21V5Hxj && \
               sudo ngrok http 16686 > /dev/null"

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("ssh_comms", default="ssh_commands.txt", metavar="ssh-comms", type=str, help="text file with ssh commands line by line")
    parser.add_argument("service_name", type=str, default="socialNetwork", help="name of the service to run workloads on")
    parser.add_argument("--no-setup", action="store_true", help="don't scp or run setup script")
    parser.add_argument("--no-sleep", action="store_true", help="don't sleep after running script")
    parser.add_argument("--no-copy", action="store_true", help="don't copy files to nodes")
    parser.add_argument("--only-copy", action="store_true", help="only copy files to nodes")
    parser.add_argument("--no-jaeger", action="store_true", help="don't automatically open jaeger page")
    parser.add_argument("--skip-swarm", action="store_true", help="don't setup swarm (don't init or join)")
    parser.add_argument("--compose", type=str, default=None, help="name of compose file to copy and use")
    parser.add_argument("--env", type=str, default=None, help="name of env file")
    parser.add_argument("--env-csv", type=str, default=None, help="name of csv file to convert to env file")
    parser.add_argument("--ip", type=str, default=None, help="use ip address that that starts with this")
    parser.add_argument("--jaeger-ip", type=str, default=None, help="use ip address for jaeger that that starts with this")
    parser.add_argument("--remote-compose", type=str, default=None, help="default compose file name in DSB repo")
    parser.add_argument("--governor", "-g", type=str, default=None, help="governor to set")
    parser.add_argument("--build", action="store_true", help="build docker images")
    return parser.parse_args()

def get_jaeger_url(node, jaeger_ip=None):
    private_ip, public_ip, all_ips = get_ip_address(node)
    if jaeger_ip is None:
        jaeger_ip = public_ip
    else:
        found = False
        for ip in all_ips:
            if ip.startswith(jaeger_ip):
                jaeger_ip = ip
                found = True
                break
        if not found:
            raise Exception(f"no ip starting with {jaeger_ip} found in node {node}")
    
    if jaeger_ip == "":
        raise Exception("no ip found")
        
    return f"http://{jaeger_ip}:16686"
    
def open_jaeger(node, jaeger_ip=None):
    url = get_jaeger_url(node, jaeger_ip=jaeger_ip)
    print(f"jaeger url: {url}", flush=True)
    webbrowser.open(url, new=0, autoraise=True)
    
def label_nodes(node):
    ids = get_node_ids(node)
    labels = [f"node{i}" for i in range(len(ids))]
    for id, label in zip(ids, labels):
        run_ssh_cmd(node, f"sudo docker node update --label-add \"node\"=true {id}")
        run_ssh_cmd(node, f"sudo docker node update --label-add \"name\"={label} {id}")
    
def init_swarm(node, master_ip):
    swarm_out = run_ssh_cmd(node, f"sudo docker swarm init --advertise-addr {master_ip}", check=True).split("\n")[4].strip()
    print(f"swarm join cmd: {swarm_out}", flush=True)
    return f"sudo {swarm_out}"

def get_ip_address(node):
    # get the private IP that starts with 10.
    ip_list = run_ssh_cmd(node, GET_IPADDR, check=True).split()
    private_ip = ""
    for ip in ip_list:
        if ip.startswith("10."):
            private_ip = ip
            break
    
    max_public_ip_try = 5
    public_ip = ""
    while public_ip == "" and max_public_ip_try > 0:
        public_ip = run_ssh_cmd(node, "sudo curl -s https://ipecho.net/plain").strip()
        max_public_ip_try -= 1
        if public_ip == "":
            if max_public_ip_try == 0:
                raise Exception("no public ip found")
            print("no public ip found, trying again in 1 second...", flush=True)
            time.sleep(1)
    
    return private_ip, public_ip, ip_list

def main():
    # parse commandline args
    args = parse_args()

    #verify service name exists
    service = find_service(args.service_name)
    dsb_path = None
    service_name = None
    if service:
        service_name = service["service_name"]
        # setup dsb_path for entire script
        dsb_path = DSB_PATH.format(service_name)
        # update current service name in json file for future reference
        update_current_service(service_name)
        # reset constraints
        reset_service_constraints()
        print("service name found!")
        print(f"current service name: {get_current_service_name()}")
        print(f"dsb_path: {dsb_path}")
    else:
        print("invalid service name")
        return

    # extract names of nodes
    nodes, ssh_commands = parse_ssh_file(args.ssh_comms)

    # test ssh connection by echoing hello
    print("testing ssh connections...", flush=True)
    responses = asyncio.run(run_remote_async(nodes, "echo hello"))
    if not all([r[0] == "hello" for r in responses]) and not all(r[2] == 0 for r in responses):
        print("ssh connection failed")
        return
    print("ssh connections successful!!! :))))) for now......", flush=True)

    if not args.no_copy:
        # copy the scripts that are needed on all nodes
        print("copying scripts to nodes...", flush=True)
        # get all files in the setup folder
        scripts_dir = "scripts"
        files = os.listdir(scripts_dir)
        for f in files:
            # copy the file to all nodes
            asyncio.run(run_remote_async(nodes, f"{scripts_dir}/{f}", scp=True, exec=True, check=True))
    else:
        print("skipping script copy...", flush=True)
    
    if args.only_copy:
        print("only copying scripts", flush=True)
        return

    # if governor specified, then set it across all nodes
    if args.governor is not None:
        print(f"setting governor to {args.governor}...", flush=True)
        set_governor(args.governor, nodes)

    # perform setup on all nodes
    if not args.no_setup:
        # copy the scripts that are needed on all nodes
        print("running setup scripts..", flush=True)
        # run the setup script (installs pip, DSB, dependencies, etc.)
        asyncio.run(run_remote_async(nodes, f"./setup.sh {service_name}", print_stderr=False, check=True))
        # run the implementation to install rapl
        asyncio.run(run_remote_async(nodes, "./rapl_install.sh", background=False))
        
        # copy master scripts to master node
        print("copying master scripts to master node...", flush=True)
        run_scp_cmd(nodes[0], "master_setup.sh", check=True, exec=True)
        run_scp_cmd(nodes[0], "deploy_stack.sh", path=dsb_path, check=True, exec=True)

        # run master setup script
        print("running master setup script...", flush=True)
        run_ssh_cmd(nodes[0], f"sudo ./master_setup.sh {service_name}", stderr=False, check=True)
        print("done setup", flush=True)
    else:
        print("skipping setup", flush=True)
    
    if args.build:
        print("building docker images...", flush=True)
        # build docker images
        run_ssh_cmd(nodes[0], "sudo ./build.sh", check=True)
        
    if args.compose is not None:
        print("copying custom compose file...", flush=True)
        # if custom compose file given, copy that to master
        run_scp_cmd(nodes[0], args.compose, path=f"{dsb_path}docker-compose-swarm.yml", check=True)
    else:
        print(f"copying {dsb_path}docker-compose-swarm-{service_name}.yml...", flush=True)
        run_scp_cmd(nodes[0], f"docker-compose-swarm-{service_name}.yml", path=f"{dsb_path}docker-compose-swarm.yml", check=True)
    
    env_file = ".env" if args.env is None else args.env
    env_csv = f"env_csvs/{service_name}/env_empty.csv" if args.env_csv is None else args.env_csv
    # if custom csv file given, make the .env file
    print("making .env file...", flush=True)
    make_compose(env_csv, f".env", nodes)
    # if custom env file given, copy that to master
    print("copying .env file...", flush=True)
    run_scp_cmd(nodes[0], env_file, path=f"{dsb_path}.env", check=True)
    
    if args.skip_swarm:
        print("skipping swarm", flush=True)
        return
    
    # just in case nodes are already in a swarm - leave (this will return with non-zero if not in swarm)
    print("leaving swarm, if already in one...", flush=True)
    asyncio.run(run_remote_async(nodes[1:], "sudo docker swarm leave --force", print_stderr=True))
    run_ssh_cmd(nodes[0], "sudo docker swarm leave --force", stderr=True)
    
    print("initializing swarm...", flush=True)
    # get the private IP (or use one given as commandline arg)
    private_ip, public_ip, all_ips = get_ip_address(nodes[0])
    master_ip = ""
    if args.ip is not None:
        # check if any ips start with args.ip
        for ip in all_ips:
            if ip.startswith(args.ip):
                master_ip = ip
                break
        if master_ip == "":
            print(f"no ip starting with {master_ip} found in node {nodes[0]}", flush=True)
            return
    else:
        if public_ip == "":
            print("no private ip found starting with 10.", flush=True)
            return
        master_ip = public_ip
    print(f"using master ip: {master_ip}", flush=True)
    
    # initialize swarm on master node
    swarm_join = init_swarm(nodes[0], master_ip)
    print("swarm initialized")
    
    # join workers to swarm
    if len(nodes) > 1:
        print("joining workers...", flush=True)
        outs = asyncio.run(run_remote_async(nodes[1:], swarm_join))
        # check if any exited with non-zero status
        for o, n in zip(outs, nodes[1:]):
            if o[2] != 0:
                raise Exception(f"error joining worker {n} to swarm")
        print("done joining", flush=True)
    else:
        print("no workers to join (only 1 node)", flush=True)
    
    # label nodes using Docker
    print("labeling nodes...", flush=True)
    label_nodes(nodes[0])
    
    # deploy the stack on the swarm
    print("deploying stack...", flush=True)
    cleanup(nodes)
    deploy_stack(nodes[0], "docker-compose-swarm.yml", env_file, dsb_path)
    print("done deploying stack", flush=True)
        
    if not args.no_sleep:
        # need to sleep due to some weird asyncio behavior
        time.sleep(60)
    
    # open the jaeger browser UI
    if not args.no_jaeger:
        open_jaeger(nodes[0])

if __name__ == "__main__":
    main()