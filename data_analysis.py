import os
import pandas as pd
import argparse


def full_path(p):
    abspath = os.path.abspath(p)
    return abspath

def join_path(p, f):
    joined = os.path.join(p, f)
    return joined

def fix_labeling(label):
    label = label.replace(",", ", ")
    label = label.replace("_", " ")
    return label

def create_csv(path, sep=","):
    abspath = full_path(path)
    csv_file = "{}/{}_labels.tsv".format(abspath, path)
    f = open(csv_file, 'a+')
    if os.path.isdir(path):
        for klass in os.listdir(path):
            klass = join_path(path, klass)
            if os.path.isdir(klass):
                for filename in os.listdir(klass):
                    _, k = os.path.split(klass)
                    k = fix_labeling(k)
                    filename.strip()
                    sep.strip()
                    k.strip()
                    row = '{}{}"{}"\n'.format(filename, sep, k)
                    f.write(row)
                    print(row[:-1])
    f.close()

def process_tsv(input_path, output):
    df = pd.read_csv(input_path, sep="\t", names=["X", "Y"])
    df_sorted = df.sort_values(['X', 'Y'], ascending=True)
    df_sorted.to_csv(output, sep="\t", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input_path",
        help="Set this flag to specfiy the input path for csv or tsv file")
    parser.add_argument(
        "-o",
        "--output_path",
        help="Set this flag to specfiy the output path for csv or tsv file")
    parser.add_argument(
        "-p",
        "--process_tsv",
        action="store_true",
        help="Set this to process tsv files")
    parser.add_argument(
        "-s",
        "--seperator",
        help="Set this to specfiy the seperator for csv generater it can be , or \\t")
    parser.add_argument(
        "--csv",
        action="store_true",
        help="Set this to generate csv file with list of labeled data",
        default=False)


    args = parser.parse_args()
    path = args.input_path
    output = args.output_path

    if args.process_tsv:
        process_tsv(path, output)
    if args.csv:
        create_csv(path, seperator)
