# -*- coding: utf-8 -*-
"""
Created on Sat Mar 12 12:40:23 2016

@author: salo
"""

import os
import pandas as pd
import numpy as np


def df_to_list(df, column_name, prefix):
    table = df[pd.notnull(df[column_name])][column_name]
    table.apply(lambda x: "{%s}" % "| ".join(x))
    table = table.tolist()
    table = [item.replace(" ", "").replace("'", "") for sublist in
             table for item in sublist.split("| ")]
    parents = table
    while parents:
        parents = [".".join(item.split(".")[:-1]) for item in parents if len(item.split("."))>1]
        table += parents
    table = ["{0}.{1}".format(prefix, item) for item in table]
    return table

folder = "/home/tsalo006/cogpo/"
filenames = ["Face.csv", "Pain.csv", "Passive.csv", "Reward.csv",
             "Semantic.csv", "Word.csv", "nBack.csv"]
data_dir = "/home/tsalo006/cogpo/athena-data/combined/"
             
column_to_cogpo = {"Paradigm Class": "Experiments.ParadigmClass",
                   "Behavioral Domain": "Experiments.BehavioralDomain",}
#                   "Diagnosis": "Subjects.Diagnosis",
#                   "Stimulus Modality": "Conditions.StimulusModality",
#                   "Stimulus Type": "Conditions.StimulusType",
#                   "Response Modality": "Conditions.OvertResponseModality",
#                   "Response Type": "Conditions.OvertResponseType",
#                   "Instructions": "Conditions.Instruction"}

full_cogpo = []
file_ = filenames[0]
for i, file_ in enumerate(filenames):
    full_file = os.path.join(folder, file_)
    df_temp = pd.read_csv(full_file, dtype=str)
    if i == 0:
        df = df_temp
    else:
        df = pd.concat([df, df_temp], ignore_index=True)

for column in column_to_cogpo.keys():
    table = df_to_list(df, column, column_to_cogpo[column])
    full_cogpo += table

full_cogpo = sorted(list(set(full_cogpo)))

# Preallocate label DataFrame
df = df[df["PubMed ID"].str.contains("^\d+$")].reset_index()
list_of_pmids = df["PubMed ID"].unique().tolist()
list_of_files = os.listdir(data_dir)
list_of_files = [os.path.splitext(file_)[0] for file_ in list_of_files]
print len(list_of_pmids)
print len(list_of_files)
list_of_pmids = sorted(list(set(list_of_pmids).intersection(list_of_files)))
print len(list_of_pmids)

column_names = ["pmid"] + full_cogpo
df2 = pd.DataFrame(columns=column_names,
                   data=np.zeros((len(list_of_pmids), len(column_names))))
df2["pmid"] = list_of_pmids

for row in df.index:
    pmid = df["PubMed ID"].iloc[row]
    if pmid in list_of_pmids:
        for column in column_to_cogpo.keys():
            values = df[column].iloc[row]
            if pd.notnull(values):
                values = values.split("| ")
                values = ["{0}.{1}".format(column_to_cogpo[column], item.replace(" ", "").replace("'", "")) for item in values]
                for value in values:
                    for out_column in df2.columns:
                        if out_column in value:
                            ind = df2.loc[df2["pmid"]==pmid].index[0]
                            df2[out_column].iloc[ind] = 1

# Reduce DataFrame
label_counts = df2.sum()
rep_labels = label_counts[label_counts>4].index
df3 = df2[rep_labels]
df4 = df3[(df3.T != 0).any()]

df4.to_csv("/home/tsalo006/cogpo/train_labels.csv", index=False)
