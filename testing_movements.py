data = [[215,81,46],[103,35,31],[99,41,27],[82,1.75,2],[78,67,35],[76,2.25,2.35],[75,6,7],[74,71,67],[63,71,34]]

count = 1
sorted_by_odds = sorted(data, key=lambda x: x[1])
for entry in sorted_by_odds:
    entry.append(count)
    count += 1

sorted_by_market = sorted(sorted_by_odds, reverse=True, key=lambda x: x[0])
sort_by_new_odds = sorted(sorted_by_odds, key=lambda x: x[2])
predicted_movements = []

for odds_idx in range(0,len(sorted_by_odds)):
    for shifted_odds_idx in range(0,len(sorted_by_market)):
        odds_entry = sorted_by_odds[odds_idx]
        market_entry = sorted_by_market[shifted_odds_idx]
        if odds_entry[3] == market_entry[3]:
            if odds_idx < shifted_odds_idx:
                predicted_movements.append(['up',sorted_by_odds[odds_idx][1]<sorted_by_odds[odds_idx][2]])
            elif odds_idx > shifted_odds_idx:
                predicted_movements.append(['down',sorted_by_odds[odds_idx][1]>sorted_by_odds[odds_idx][2]])
            else:
                predicted_movements.append(['n/a',sorted_by_odds[odds_idx][1]==sorted_by_odds[odds_idx][2]])
            break
print('epic')