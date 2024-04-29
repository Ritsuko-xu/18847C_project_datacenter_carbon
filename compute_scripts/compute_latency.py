import argparse
import glob
import json
import numpy as np

def parse_args():
    parser = argparse.ArgumentParser(description="Calculate and print latencies from Jaeger trace JSON files.")
    parser.add_argument("--json_files", required=True,
                        help="Path to the directory containing JSON files with traces.")
    parser.add_argument("--percentiles", type=int, nargs='*', default=[],
                        help="Percentile(s) to calculate latencies for, e.g., 50 90 99.")
    return parser.parse_args()

def load_json_files(directory):
    """
    Load and return traces from JSON files located in the specified directory.
    """
    files_pattern = f"{directory}/*.json"
    traces = []
    for file_path in glob.glob(files_pattern):
        with open(file_path, 'r') as file:
            trace_data = json.load(file)
            if isinstance(trace_data, dict):
                traces.append(trace_data)
            elif isinstance(trace_data, list):
                traces.extend(trace_data)
    return traces

def calculate_and_print_latencies(traces, percentiles):
    """
    Calculate and print the total, average, and specified percentile latencies for the given traces, in milliseconds.
    """
    latencies = []
    for trace in traces:
        spans = trace.get('data', [])[0].get('spans', []) if 'data' in trace else []
        for span in spans:
            latencies.append(span.get('duration', 0) / 1000)  # Convert to milliseconds

    if latencies:
        total_latency = sum(latencies)
        average_latency = np.mean(latencies)
        print(f"Total Latency: {total_latency:.3f} milliseconds")
        print(f"Average Latency: {average_latency:.3f} milliseconds")
        for percentile in percentiles:
            percentile_latency = np.percentile(latencies, percentile)
            print(f"{percentile}th Percentile Latency: {percentile_latency:.3f} milliseconds")
    else:
        print("No spans found. Unable to calculate latencies.")

def main():
    args = parse_args()
    traces = load_json_files(args.json_files)
    calculate_and_print_latencies(traces, args.percentiles)

if __name__ == "__main__":
    main()

