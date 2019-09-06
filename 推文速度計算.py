import sqlite3
import pandas as pd
from tqdm import tqdm

conn = sqlite3.connect(r"D:\\研究\\選舉研究\\資料\\推文資料_測試.db")
print("Open database successfully")

cursor = list(conn.execute("SELECT * from 推文資料"))
