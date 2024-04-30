import os
import subprocess

def find_html_files(directory):
    html_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    return html_files

def process_file(html_file):
    file_name = os.path.splitext(os.path.basename(html_file))[0]
    json_dir = f"/Users/xinshiwang/Documents/CMU Courses/18847C/hardware_reuse/outputs/jaeger_json/r320_79sat_json/{file_name}"
    command = f"python plot_jaeger.py --json_files \"{json_dir}\" --raw --file_name {file_name}"
    print(command)
    subprocess.run(command, shell=True, check=True)

def main():
    directory = '/Users/xinshiwang/Documents/CMU Courses/18847C/hardware_reuse/outputs/r320_70saturation'  # TODO: 更新为你的HTML文件所在目录
    html_files = find_html_files(directory)
    for html_file in html_files:
        process_file(html_file)

main()
