from helpers import convert_range
import pickle
import matplotlib.pyplot as plt
import argparse
import pandas as pd

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("stats_files", metavar="stats-files", type=str, nargs='+', help="stats files")
    parser.add_argument("--to-plot", "-p", type=str, default='cpu0_package_joules', help="type of data to plot")
    parser.add_argument("--range", "-r", type=str, default=None, help="range of data to plot")
    return parser.parse_args()

def prepare_data_for_plotting(file_path):
    with open(file_path, 'rb') as file:
        data = pickle.load(file)

    rows = []
    for entry in data:
        index = entry[0]
        stats_list = entry[1][1]
        for stats in stats_list:
            if stats is not None:
                stats['index'] = index
                rows.append(stats)
    return pd.DataFrame(rows)

def aggregate_data(dfs):
    # Concatenate all DataFrames and then group by 'index' to compute the mean for each index
    combined_df = pd.concat(dfs, axis=0)
    mean_df = combined_df.groupby('index').mean().reset_index()
    return mean_df

def plot_stats(df, attribute):
    if attribute in df.columns:
        plt.figure(figsize=(10, 6))
        plt.plot(df['index'], df[attribute], marker='o', linestyle='-')
        plt.title(f'Plot of {attribute} vs. Index')
        plt.xlabel('Index')
        plt.ylabel(attribute)
        plt.grid(True)
        plt.show()
    else:
        print(f"Attribute {attribute} not found in the DataFrame.")

def main():
    args = parse_args()
    dataframes = []

    for file_path in args.stats_files:
        print(f"Processing file: {file_path}")
        df = prepare_data_for_plotting(file_path)
        dataframes.append(df)

    combined_df = aggregate_data(dataframes)

    if args.range:
        range_start, range_end = convert_range(args.range)
        combined_df = combined_df[(combined_df['index'] >= range_start) & (combined_df['index'] <= range_end)]

    plot_stats(combined_df, args.to_plot)

if __name__ == "__main__":
    main()
