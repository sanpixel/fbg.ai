import pandas as pd

df = pd.read_csv('players.csv')
print('Player price stats:')
print(df['Price'].describe())
print()

print('Position price ranges:')
for pos in ['QB','RB','WR','TE','K','DEF']:
    pos_df = df[df['Position']==pos]
    print(f'{pos}: {len(pos_df)} players, ${pos_df["Price"].min():.0f}-${pos_df["Price"].max():.0f}')

print()
print('Sample team cost calculation:')
print('1 QB (cheapest): $', df[df['Position']=='QB']['Price'].min())
print('1 RB (cheapest): $', df[df['Position']=='RB']['Price'].min()) 
print('2 WR (cheapest): $', df[df['Position']=='WR']['Price'].min() * 2)
print('1 TE (cheapest): $', df[df['Position']=='TE']['Price'].min())
print('1 K (cheapest): $', df[df['Position']=='K']['Price'].min())
print('1 DEF (cheapest): $', df[df['Position']=='DEF']['Price'].min())
print('2 FLEX (cheapest RB): $', df[df['Position']=='RB']['Price'].min() * 2)
print('5 BENCH (cheapest): $', df.nsmallest(5, 'Price')['Price'].sum())

min_cost = (df[df['Position']=='QB']['Price'].min() + 
           df[df['Position']=='RB']['Price'].min() + 
           df[df['Position']=='WR']['Price'].min() * 2 +
           df[df['Position']=='TE']['Price'].min() + 
           df[df['Position']=='K']['Price'].min() + 
           df[df['Position']=='DEF']['Price'].min() +
           df[df['Position']=='RB']['Price'].min() * 2 +
           df.nsmallest(5, 'Price')['Price'].sum())

print(f'Minimum possible team cost: ${min_cost:.0f}')
