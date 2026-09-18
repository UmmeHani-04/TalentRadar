# import pandas as pd

# df = pd.read_csv("submission.csv")

# print("Rows:", len(df))
# print("Duplicate IDs:", df["candidate_id"].duplicated().sum())

import pandas as pd

df = pd.read_csv("submission.csv")

print("Shape:", df.shape)
print("Rows:", len(df))

print("Last 5 rows:")
print(df.tail())