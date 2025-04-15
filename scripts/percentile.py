import pandas as pd

def print_percentiles(csv_file):
    df = pd.read_csv(csv_file)

    for metric in ["memory_MB", "cpu_percent"]:
        print(f"\n== {metric.upper()} Percentiles ==")
        for p in [50, 75, 90, 95, 99, 100]:
            val = df[metric].quantile(p / 100.0)
            print(f"{p}th percentile: {val:.2f}")

if __name__ == "__main__":
    print_percentiles("/Users/ashutoshverma/Documents/grocer-ease-chatbot/resource_usage_6308.csv")
