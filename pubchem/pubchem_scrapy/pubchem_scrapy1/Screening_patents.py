import pandas as pd
df = pd.read_csv(r"E:\PROJECT\25_71_Robinagent\516541\patent\pubchem_cid_92786_patent.csv")

for row in df.iterrows():
    print(row)