import os
import subprocess

def scan_html_files(directory):
    """
    Scan for HTML files in the given directory.

    Parameters:
    - directory (str): The directory to scan for HTML files.

    Returns:
    - List[str]: A list of paths to the HTML files.
    """
    html_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".html"):
                html_files.append(os.path.join(root, file))
    return html_files

def parse_html_file(file_path, output_dir_base, ssh_commands_file):
    """
    Parse the given HTML file using the `parse_jaeger.py` script.

    Parameters:
    - file_path (str): The path to the HTML file.
    - output_dir_base (str): The base directory to save the output JSON files.
    - ssh_commands_file (str): The path to the ssh_commands.txt file.
    """
    file_name = os.path.basename(file_path).replace('.html', '')
    output_dir = os.path.join(output_dir_base, file_name)
    os.makedirs(output_dir, exist_ok=True)
    
    command = f"python parse_jaeger.py --html-file {file_path} --out-dir {output_dir}"
    subprocess.run(command, shell=True, check=True)

def main():
    directory_to_scan = "htmls/c220g1_load_350"  # TODO: Update this path
    output_dir_base = "c220g1_70sat_json"
    ssh_commands_file = "/Users/xinshiwang/Documents/CMU Courses/18847C/hardware_reuse/ssh_commands.txt"  # TODO: Update this path if necessary
    
    html_files = scan_html_files(directory_to_scan)
    for html_file in html_files:
        # if html_file in ["./text.html","./nginx-web.html","./home-timeline.html","./user-timeline.html","./user-mention.html","./user.html","./media.html","./compose-post-service.html","./url-shorten.html","./post-storage.html","./unique_id.html"]:
        #     continue
        parse_html_file(html_file, output_dir_base, ssh_commands_file)
        print(f"Processed {html_file}")


main()
