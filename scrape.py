import requests
import bs4 as bs
import pandas as pd
import country_converter as coco

url = 'https://en.wikipedia.org/wiki/COVID-19_lockdowns'
response = requests.get(url)
soup = bs.BeautifulSoup(response.text, "html.parser")
table = soup.find('table', {'class':"wikitable"})
df = pd.read_html(str(table))
df=pd.DataFrame(df[0])



df1 = df.copy()
df1.columns = df1.columns.droplevel([0])
country_codes = ["AE", "EG", "CA", "IQ", "CN", "IS", "DK", "MX", "NL", "QA", "SG", "US"]
country_names = list(map(lambda x: coco.convert(x, to='name_short'), country_codes))

idx = df1["Country / territory"].isin(country_names)



df2 = df1[idx.values]
df2.columns = df2.columns.droplevel(0)
df2 = df2.rename({'Country / territory' : 'Country'}, axis = 1)
cols = []
count = 1
for column in df2.columns:
    if column == 'Start date':
        cols.append(f'Start_date_{count}')
        count+=1
        continue
    elif column == 'End date':
        cols.append(f'End_date_{count-1}')
        
        continue
 
    cols.append(column)
df2.columns = cols
df2 = df2.drop(["Length (days)", "Total length (days)", "Level"], axis = 1).dropna(axis = 1, how = 'all')
df2 = df2.applymap(lambda x: str(x).split('[')[0])

corona_lockdowns = {}
for country in df2.Country.unique():
    dates = []
    for i in range(4):
        start = pd.to_datetime(df2[df2.Country == country][f"Start_date_{i+1}"]).min()
        end   = pd.to_datetime(df2[df2.Country == country][f"End_date_{i+1}"]).max()
        if type(start) is pd.Timestamp:
            date_range = pd.Series(pd.date_range(start, end)).dt.date
            dates.extend(date_range)
    corona_lockdowns[coco.convert(country, to ='ISO2')] = dates
