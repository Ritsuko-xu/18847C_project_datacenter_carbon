import os
import json
import matplotlib.pyplot as plt
import argparse
import numpy as np
import pandas as pd
from prettytable import PrettyTable
from helpers import splitlines_file
import pickle
import argparse
import glob
import json

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json_files", default="outputs/jaeger_json/jaeger_json")
    parser.add_argument("--histogram", action="store_true", help="plot histogram of latencies")
    parser.add_argument("--raw",default=True,action="store_true", help="raw latencies")
    parser.add_argument("--labels", "-l", type=str, default=None, help="labels for each directory in text file")
    parser.add_argument("--filter", "-f", type=str, default=None, help="text file with services to include (filter out everything else), one service per line")
    parser.add_argument("--title-suffix", "-t", type=str, default=None, help="suffix to add to title")
    parser.add_argument("--load")
    parser.add_argument("--file_name", default=None)
    return parser.parse_args()

def plot_histogram(traces):
    service_latencies = get_latencies(traces)
    
    for service in service_latencies:
        plt.hist(service_latencies[service], bins=10)
        plt.title(service)
        plt.show()

'''
SAMPLE SPAN:
{
    "traceID": "040bf662907ab34c",
    "spanID": "881c4dbde1c51027",
    "flags": 1,
    "operationName": "compose_creator_server",
    "references": [
        {
        "refType": "CHILD_OF",
        "traceID": "040bf662907ab34c",
        "spanID": "11e334ebed711c91"
        }
    ],
    "startTime": 1695740648913781,
    "duration": 6,
    "tags": [
        {
        "key": "internal.span.format",
        "type": "string",
        "value": "proto"
        }
    ],
    "logs": [],
    "processID": "p1",
    "warnings": null
}
'''

def make_span_tree(trace):
    spans = trace['spans']
    span_tree = {}
    for span in spans:
        span_id = span['spanID']
        if 'references' not in span or len(span['references']) == 0:
            continue
        if 'duration' not in span:
            continue
        parent_id = span['references'][0]['spanID']
        if parent_id not in span_tree:
            span_tree[parent_id] = []
        span_tree[parent_id].append(span_id)
    return span_tree

def get_span_by_id(trace, span_id):
    for span in trace['spans']:
        if span['spanID'] == span_id:
            return span
    return None

def span_id_to_operation_name(trace, span_id):
    return get_span_by_id(trace, span_id)['operationName']

def get_span_tree_root(span_tree):
    root = None
    children_spans = set()
    for parent, children in span_tree.items():
        for child in children:
            children_spans.add(child)
    for span in span_tree:
        if span not in children_spans:
            root = span
            break
    return root

def get_span_tree_roots(span_tree):
    roots = []
    children_spans = set()
    for parent, children in span_tree.items():
        for child in children:
            children_spans.add(child)
    for span in span_tree:
        if span not in children_spans:
            roots.append(span)
    return roots

def add_self_time_helper(trace, span_tree, span_id):
    '''
    Given a span, add the self time to the span given by span_id and all its children
    trace: the trace the span belongs to
    span_tree: the span tree of the trace
    span_id: the id of the span to add self time to
    '''
    span = get_span_by_id(trace, span_id)
    if span is None:
        return
    if 'self_time' in span:
        return
    span['self_time'] = span['duration']
    if span_id not in span_tree:
        return
    for child in span_tree[span_id]:
        # first subtract the child's duration from the parent's self time
        span['self_time'] -= get_span_by_id(trace, child)['duration']
        # then calculate the child's self time
        add_self_time_helper(trace, span_tree, child)

def add_self_time(trace):
    '''
    Given a trace, add the self time to each span in the trace
    trace: the trace to add self time to
    '''
    span_tree = make_span_tree(trace)
    roots = get_span_tree_roots(span_tree)
    for root in roots:
        add_self_time_helper(trace, span_tree, root)

def add_self_time_traces(traces):
    for trace in traces:
        add_self_time(trace)

def plot_histogram_from_pickle(pickle_file, load):
    traces = get_load_trace(pickle_file, load)
    plot_histogram(traces)

def extract_load_traces(pickle_file):
    with open(pickle_file, 'rb') as f:
        data = pickle.load(f)
    load_traces = {}
    for d in data:
        if len(d) < 3:
            continue
        load = d[0]
        if isinstance(d[2], str):
            load_traces[load] = "error"
        else:
            traces = d[2]['data']
            assert(all(['spans' in trace for trace in traces]))
            add_self_time_traces(traces)
            load_traces[load] = traces
    return load_traces

def get_load_trace(pickle_file, load):
    load_traces = extract_load_traces(pickle_file)
    return load_traces[load]

def process_span(span, service_durations, self_time):
    service = span['operationName']
    if service not in service_durations:
        service_durations[service] = []
    if self_time:
        if 'self_time' not in span:
            return
        duration = span['self_time']
    else:
        duration = span['duration']
    service_durations[service].append(duration)
        
def get_latencies(traces, mean=True, percentile=None, self_time=False):
    service_durations = {}
    if isinstance(traces, str):
        raise Exception(f"error in traces: {traces}")
    
    # Check if traces is a list and handle accordingly
    if isinstance(traces, list):
        for trace in traces:
            spans = trace.get('spans', [])
            for span in spans:
                process_span(span, service_durations, self_time)
    else:
        spans = traces.get('spans', [])
        for span in spans:
            process_span(span, service_durations, self_time)

    # Process percentile and mean calculations
    if percentile is not None:
        if isinstance(percentile, list):
            percentile_ratio = (percentile[0], percentile[1])
            service_durations = {service: np.percentile(durations, percentile_ratio[0]) / np.percentile(durations, percentile_ratio[1]) for service, durations in service_durations.items()}
        else:
            service_durations = {service: np.percentile(durations, percentile) for service, durations in service_durations.items()}
    elif mean:
        service_durations = {service: np.mean(durations) for service, durations in service_durations.items()}
    return service_durations

def compare_file_latencies(files, load, normalize=False, print_table=True, labels=None, services=None, title_suffix=None, percentile=None, self_time=False):
    file_traces = []
    for i, file in enumerate(files):
        print(f"getting latencies for {file}")
        traces = get_load_trace(file, load)
        file_traces.append(traces)
    if labels is None:
        labels = files
    compare_latencies(file_traces, labels=labels, normalize=normalize, print_table=print_table, services=services, title_suffix=title_suffix, percentile=percentile, self_time=self_time)

def compare_load_latencies(pickle_file, loads, normalize=False, print_table=True, labels=None, services=None, title_suffix=None, percentile=None, self_time=False):
    load_traces = extract_load_traces(pickle_file)
    load_traces = {load: load_traces[load] for load in loads}
    if labels is None:
        labels = loads
    compare_latencies(load_traces.values(), labels=labels, normalize=normalize, print_table=print_table, services=services, title_suffix=title_suffix, percentile=percentile, self_time=self_time)

def compare_latencies(traces_list, labels=None, normalize=False, print_table=True, services=None, title_suffix=None, percentile=None, self_time=False):
    df = pd.DataFrame()
    if labels is None:
        labels = [f"traces {i}" for i in range(len(traces_list))]
    for i, traces in enumerate(traces_list):
        service_latencies = get_latencies(traces['data'][0], mean=True, percentile=percentile, self_time=self_time)
        service_latencies['label'] = labels[i]
        df = pd.concat([df, pd.DataFrame(service_latencies, index=[i])])
    
    # make dir the first column
    df = df[['label'] + [col for col in df.columns if col != 'label']]
    # use all columns except for dir - each row is a microservice, each column is a directory
    df_transposed = df[[col for col in df.columns if col != 'label']].transpose()
    # units are microseconds, convert to milliseconds
    if not isinstance(percentile, list):
        df_transposed = df_transposed / 1000
    # if labels are provided, use them as the column names
    if labels is not None:
        df_transposed.columns = labels
    # order rows alphabetically
    df_transposed = df_transposed.sort_index()
    print(type(df_transposed))
        
    if print_table:
        t = PrettyTable()
        # use all columns except for dir
        t.field_names = ['microservice'] + df_transposed.columns.tolist()
        # add values rounded to three decimal points
        rows = [[round(val, 3) for val in row] for row in df_transposed.values]
        for i, row in enumerate(rows):
            t.add_row([df_transposed.index[i]] + row)
        # change titles of data columns to labels if provided
        if labels is not None:
            t.field_names = ['microservice'] + labels
        print(t)
    
    if percentile is not None:
        y_title = f'{percentile}th Percentile Latency (ms)'
    else:
        y_title = 'Avg. Latency (ms)'
    if normalize:
        row_maxes = df_transposed.max(axis=1)
        df_transposed = df_transposed.div(row_maxes, axis=0)
        # get the reciprocal
        df_transposed = 1 / df_transposed
        if percentile is not None:
            y_title = f'{percentile}th Percentile Latency (speedup)'
        else:
            y_title = 'Normalized Avg. Latency (speedup)'
    
    if services is not None:
        df_transposed = df_transposed.loc[services]


    fig, ax = plt.subplots(figsize=(10, 5))
    df_transposed.plot(kind='bar', ax=ax, width=0.8)
    # set legend labels to directory names
    if labels is not None:
        legend = ax.legend(labels)
    else:
        legend = ax.legend(df['label'])

    # 如果你想隐藏图例，取消注释下面一行
    legend.set_visible(False)

    ax.set_ylabel(y_title)
    ax.set_xlabel('Microservice')
    title = args.file_name
    if self_time:
        title += ' (Self Time)'
    if title_suffix is not None:
        title += f" ({title_suffix})"
    ax.set_title(title)

    # 调整布局并保存图表
    plt.subplots_adjust(bottom=0.5)

    # 保存图表需要在plt.show()之前
    plt.savefig(f'{args.file_name}.png')

    # 现在显示图表
    # plt.show()

def main():
    global args 
    args = parse_args()
    
    if args.histogram:
        plot_histogram(args.json_dirs[0])
        return
    
    services = None
    if args.filter is not None:
        services = splitlines_file(args.filter)
    def load_json_files(directory):
        # 使用glob模块查找目录下的所有JSON文件
        json_files = glob.glob(f"{directory}/*.json")
        loaded_jsons = []
        for file in json_files:
            # 打开并加载每个JSON文件
            with open(file, 'r') as f:
                data = json.load(f)
                loaded_jsons.append(data)
        return loaded_jsons
    loaded_jsons = []
    loaded_jsons = load_json_files(args.json_files)
    compare_latencies(loaded_jsons, normalize=not args.raw, labels=splitlines_file(args.labels),
                      services=services, title_suffix=args.title_suffix)

if __name__ == "__main__":
   main()