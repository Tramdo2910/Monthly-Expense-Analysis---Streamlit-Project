import pandas as pd
import sqlite3

# 1. Read the CSV
df = pd.read_csv('Daily Household Transactions.csv')

# 2. Connect to SQLite database (creates file if not exists)
conn = sqlite3.connect('expenses.db')

# 3. Write the DataFrame to a SQL table (named 'transactions')
df.to_sql('transactions', conn, if_exists='replace', index=False)

# 4. Check (optional): Query back some data
result = pd.read_sql('SELECT * FROM transactions LIMIT 5', conn)
print(result)

# 5. Always close the connection!
conn.close()