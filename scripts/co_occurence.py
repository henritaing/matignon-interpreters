import pandas as pd

df = pd.read_csv("data/coocc_src.csv")

# video × interpreter grid: 1 if the interpreter worked on the video, else 0
m = pd.crosstab(df["Video_ID"], df["Interpreter_#_A"]).clip(upper=1)

# co-occurrence: number of shared videos for each pair
co = m.T @ m
for interpreter in co.index:
    co.loc[interpreter, interpreter] = 0

# pandas sorts strings lexicographically, so interpreter_10 would come before interpreter_2
def interpreter_number(name: str) -> int:
    return int(name.removeprefix("interpreter_"))

sorted_interpreters = sorted(co.index, key=interpreter_number)
co = co.loc[sorted_interpreters, sorted_interpreters]

print(co)
co.to_csv("data/cooccurrence.csv")
