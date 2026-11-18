import sqlite3
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent
SOURCE = BASE / "OLA_DataSet.xlsx"
if not SOURCE.exists():
    SOURCE = BASE.parents[1] / "OLA_DataSet.xlsx"
DATA_DIR = BASE / "data"

df = pd.read_excel(SOURCE, sheet_name="July")
n0 = len(df)
df = df.drop(columns=['Vehicle Images'])
df['Time'] = df['Time'].astype(str)
df['Date'] = pd.to_datetime(df['Date']).dt.normalize()
for c in ['Booking_ID','Customer_ID','Vehicle_Type','Pickup_Location','Drop_Location','Booking_Status']:
    df[c] = df[c].astype(str).str.strip()
df = df.drop_duplicates('Booking_ID')
# meaningful fills (NaN here = "not applicable for this status")
df['Canceled_Rides_by_Customer'] = df['Canceled_Rides_by_Customer'].fillna('Not Applicable')
df['Canceled_Rides_by_Driver']   = df['Canceled_Rides_by_Driver'].fillna('Not Applicable')
df['Incomplete_Rides']           = df['Incomplete_Rides'].fillna('Not Applicable')
df['Incomplete_Rides_Reason']    = df['Incomplete_Rides_Reason'].fillna('Not Applicable')
df['Payment_Method']             = df['Payment_Method'].fillna('Not Applicable')
# derived features
df['Hour']      = pd.to_datetime(df['Time'], format='%H:%M:%S').dt.hour
df['Day']       = df['Date'].dt.day
df['Day_Name']  = df['Date'].dt.day_name()
df['Week']      = ((df['Date'].dt.day-1)//7)+1
df['Is_Success']= (df['Booking_Status']=='Success').astype(int)
df['Time_Slot'] = pd.cut(df['Hour'],[-1,5,11,16,20,23],labels=['Night (0-5)','Morning (6-11)','Afternoon (12-16)','Evening (17-20)','Late Night (21-23)'])
df['Time_Slot'] = df['Time_Slot'].astype(str)
df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
DATA_DIR.mkdir(exist_ok=True)
df.to_csv(DATA_DIR / 'ola_cleaned.csv', index=False)
with sqlite3.connect(DATA_DIR / 'ola.db') as con:
    df.to_sql('ola_rides', con, if_exists='replace', index=False)
print(n0, len(df)); print(df.isna().sum().sum(), 'NaN left (numeric ones only for non-success):'); print(df.isna().sum()[df.isna().sum()>0])
