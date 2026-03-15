# !/usr/bin/python

import pandas as pd
import numpy as np
import os
import argparse
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=FutureWarning)

BUCKET_SIZE_MS = 1000
#BUCKET_SIZE_MS = 1

def filter_to_application_(trace):
    try:
        while len(trace) > 0:
            record = trace[0]
            exclude = False
            exclude = any((
                (r'.' not in record),
                #(r"Lambda" in record),
                #(r'scala.' in record and '.scala\.' not in record), 
                (r'GLIBC' in record), 
                (r'unknown_Java' in record), 
                #(r'renaissance' in record), 
                #(r'java.' not in record and 'jdk.' not in record and "scala." not in record and "sun." not in record), 
                #(r'java.' not in record), 
                #(r'java.' in record and '.java\.' not in record),
                #(r'javax.' in record and '.javax\.' not in record),
                #(r'jdk.' in record and '.jdk\.' not in record),
                #(r'sun.' in record and '.sun\.' not in record),
                (r'org.apache.commons.' in record and '.org.apache.commons\.' not in record),
                (r'<init>' in record),
                (r'.so' in record),
                (r'::' in record),
                (r'[' in record),
                (r']' in record)
            ))
            if not exclude:
                return trace
            else:
                trace.pop(0)
    except:
        pass
    return 'end'

def filter_to_application(df, bucket=BUCKET_SIZE_MS):
    mask = (df.trace == 'end') | df.trace.str.contains('jlibc') | df.trace.str.contains('jrapl') | df.trace.str.contains('saraswati') | (df.trace == 'dummy')
    df = df[~mask]
    df.trace = df.trace.str.split(';').map(filter_to_application_)
    method = df.trace.str[0]
    df = df[(df.trace != 'end') & (method != 'e') & ~(method.str.contains('org.dacapo.harness'))]
    df["timestamp"] = df["timestamp"] // 10**6 // bucket
    df.trace = df.trace.map(lambda arr : ";".join(arr))
    return df

def parse_args():
    parser = argparse.ArgumentParser(description='profile trace accumulation')
    parser.add_argument('data', type=str, help='path to probing data')
    parser.add_argument(
        '--output_directory',
        default=None,
        help='location to write the summary and metrics'
    )
    parser.add_argument(
        "--out_file_name",
        default="profiling_data.csv",
        help="filename for alignment"
    )
    args = parser.parse_args()
    if args.output_directory is None:
        args.output_directory = os.path.join(args.data)
    return args

def second_fun(x):
    arr = x.split(";")
    if len(arr) < 2:
        return arr[0]
    return arr[1]+"-->"+arr[0]

def third_fun(x):
    arr = x.split(";")
    if len(arr) < 2:
        return arr[0]
    if len(arr) == 2:
        return arr[1]+"-->"+arr[0]
    return arr[2]+"-->"+arr[1]+"-->"+arr[0]


def first_fun(x):
    return x.split(";")[0]

def hash_entire_trace(x):
    return f"{x.__hash__()}"

def hash_partial_trace(x):
    return f"{second_fun(x).__hash__()}"
    #return f"{first_fun(x).__hash__()}"

def align_benchmark_iter_profiler_super(path, _benchmark, start_iteration, end_iteration, warm_up=0, bucket=BUCKET_SIZE_MS):
    profiles = pd.DataFrame() 
    for benchmark in [_benchmark]:
        bench = benchmark
        data_dir = os.path.join(path, benchmark)
        try:
            p_df = pd.DataFrame()
            for iteration in range(start_iteration, end_iteration+1):
                try:
                    p_df = pd.concat([p_df, pd.read_csv(os.path.join(data_dir, f'profile_{iteration}.csv'))])
                except FileNotFoundError:
                    pass
            profiles = filter_to_application(p_df, bucket=bucket)
            profiles["benchmark"] = bench
        except Exception as e:
            print(f'error getting profiling data for {bench}')
            print(e)
            return pd.DataFrame()
    #profiles["func"] = profiles.trace.map(first_fun)
    profiles["func"] = profiles.trace.map(hash_partial_trace)
    top_methods = profiles["func"].unique()
    profiles_cnt = profiles.groupby(["timestamp","func","benchmark"]).count().reset_index()
    pairs = profiles.groupby(["timestamp","func"]).count().index
    counts = []
    for ts,fn in pairs:
        #count = profiles[(profiles["timestamp"] == ts) & (profiles["trace"].str.contains(fn))].count()
        count = profiles[(profiles["timestamp"] == ts) & (profiles["trace"].apply(hash_partial_trace) == fn)].count()
        counts.append((ts,fn,count[0]))
    profiles_cnt = pd.DataFrame(counts, columns=["ts","func","count"])
    profiles_cnt["benchmark"] = _benchmark
    profiles_cnt = profiles_cnt.pivot_table(values="count", index=[profiles_cnt.ts, profiles_cnt.benchmark], columns=["func"]).reset_index()
    counts = []
    for fn in top_methods:
        #count = profiles[(profiles["trace"].str.contains(fn))].count()
        count = profiles[(profiles["trace"].apply(hash_partial_trace) == fn)].count()
        counts.append((fn, count[0]))
    profiles_cnt_filter = pd.DataFrame(counts, columns=["func","count"])
    profiles_cnt_filter = profiles_cnt_filter[profiles_cnt_filter["count"] > 3]["func"].values.tolist() #3 signifies the number of times the method showed up in an interval...in this case at least four times per interval
    profiles_cnt = profiles_cnt[["ts","benchmark"]+profiles_cnt_filter]
    with open(f"{path}/{_benchmark}/trace_mappings.csv", "a") as fp:
        for mapping in (profiles["trace"].apply(second_fun) + profiles["func"].apply(lambda fn: f",{fn}")).unique():
            fp.write(f"{mapping}\n")
    return profiles_cnt


def align_benchmark_iter_profiler(path, _benchmark, iteration, warm_up=0, bucket=BUCKET_SIZE_MS):
    profiles = pd.DataFrame() 
    for benchmark in [_benchmark]:
        bench = benchmark
        data_dir = os.path.join(path, benchmark)
        try:
            profiles = filter_to_application(pd.read_csv(os.path.join(data_dir, f'profile_{iteration}.csv')), bucket=bucket)
            profiles["benchmark"] = bench
        except Exception as e:
            print(f'error getting profiling data for {bench}')
            print(e)
            return pd.DataFrame()
    #profiles["func"] = profiles.trace.map(first_fun)
    profiles["func"] = profiles.trace.map(hash_partial_trace)
    top_methods = profiles["func"].unique()
    profiles_cnt = profiles.groupby(["timestamp","func","benchmark"]).count().reset_index()
    pairs = profiles.groupby(["timestamp","func"]).count().index
    counts = []
    for ts,fn in pairs:
        count = profiles[profiles["timestamp"] == ts]
        #count = count[count["trace"].str.contains(fn)].count()
        count = count[count["trace"].apply(hash_partial_trace) == fn].count()
        counts.append((ts,fn,count[0]))
    profiles_cnt = pd.DataFrame(counts, columns=["ts","func","count"])
    profiles_cnt["benchmark"] = _benchmark
    profiles_cnt = profiles_cnt.pivot_table(values="count", index=[profiles_cnt.ts, profiles_cnt.benchmark], columns=["func"]).reset_index()
    counts = []
    for fn in top_methods:
        #count = profiles[(profiles["trace"].str.contains(fn))].count() #Counting up number of times the method shows up at all instead of within certain timestamps
        #count = profiles_cnt[fn].sum()
        count = profiles[(profiles["trace"].apply(hash_partial_trace) == fn)].count()
        counts.append((fn, count[0]))
    profiles_cnt_filter = pd.DataFrame(counts, columns=["func","count"])
    profiles_cnt_filter = profiles_cnt_filter[profiles_cnt_filter["count"] > 3]["func"].values.tolist() #3 signifies the number of times the method showed up in an interval...in this case at least four times per interval
    profiles_cnt = profiles_cnt[["ts","benchmark"]+profiles_cnt_filter]
    with open(f"{path}/{_benchmark}/trace_mappings.csv", "a") as fp:
        #hash function seems to be seeded, but doesn't affect static information
        for mapping in (profiles["trace"].apply(second_fun) + profiles["func"].apply(lambda fn: f",{fn}")).unique():
            fp.write(f"{mapping}\n")
    return profiles_cnt

def main():
    return
            
if __name__ == '__main__':
    main()
