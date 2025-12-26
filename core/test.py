import yfinance as yf

df = yf.download("GOOGL", period="10y")
print(df.columns)


