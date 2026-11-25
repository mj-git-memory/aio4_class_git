import pandas as pd

splits = {'train': 'data/train-00000-of-00001-258bcfc491c8fd80.parquet', 'validation': 'data/validation-00000-of-00001-185d63abd14a6096.parquet', 'test': 'data/test-00000-of-00001-9c3147d142d3ea1f.parquet'}
df = pd.read_parquet("hf://datasets/james-burton/wine_reviews/" + splits["train"])
print(df.iloc[:2, :])
