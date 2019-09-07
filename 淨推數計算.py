import sqlite3
import pandas as pd
from tqdm import tqdm

#讀入資料
conn = sqlite3.connect(r"D:\\研究\\資料\\data.db")
print("Open database successfully")
