# Limpieza igual a la del Certamen 2 (Bloques 1 y 2) y archivo para la app
import pandas as pd

df = pd.read_csv('Chicago_Crimes_2012_to_2017.csv', on_bad_lines='skip')
print('archivo completo:', len(df))
df = df[df['Year'].isin([2015, 2016])].copy()
print('2015 y 2016:', len(df))

df['Date'] = pd.to_datetime(df['Date'], format='mixed', errors='coerce')
df['Location Description'] = df['Location Description'].fillna('Sin dato')
df = df.dropna(subset=['Ward'])
df.loc[df['Primary Type'].isin(['NON - CRIMINAL', 'NON-CRIMINAL (SUBJECT SPECIFIED)']), 'Primary Type'] = 'NON-CRIMINAL'
print('despues de limpiar:', len(df), '| tipos:', df['Primary Type'].nunique())

cols = ['Date', 'Primary Type', 'Location Description', 'Arrest', 'Domestic', 'District',
        'Community Area', 'Latitude', 'Longitude', 'Year']
df = df[cols]
df['District'] = df['District'].astype('Int64')
df['Community Area'] = df['Community Area'].astype('Int64')
df['Latitude'] = df['Latitude'].round(5)
df['Longitude'] = df['Longitude'].round(5)
df = df.sort_values('Date')
df.to_csv('data/chicago_2015_2016_limpio.csv.gz', index=False, date_format='%Y-%m-%d %H:%M:%S')
print('arresto %:', round(df['Arrest'].mean() * 100, 2), '| domestico %:', round(df['Domestic'].mean() * 100, 2))
print('sin coordenadas:', df['Latitude'].isnull().sum())
