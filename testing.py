

#data = "2.7, 6, 6.5, 8, 11, 11, 12, 13, 15, 19, 23, 26, 51, 71, 126"
#data = data.split(" ")
#for idx in range(0,len(data)):
#    data[idx] = float(data[idx])
#starting_price = [5.5, 2.9, 2.8, 19, 26, 12, 13, 41, 26, 41, 41, 41]
#highest = [5.5, 3.8, 4.2, 21.5, 26, 16, 21.5, 43, 51, 61, 71, 81, 101]
#data = starting_price

#data = [6, 7, 6, 8.5, 17, 21, 27, 35, 46, 41, 51, 51]
#data = sorted(data)
#print(len(data))
#i_p = 0
#for entry in data:
#    i_p += 1/entry
#    print(i_p,1/entry,entry)
#print(i_p)


arbitrage_sums = {
    "Pakenham": {
        "R1": 0.9774838893873888,
        "R2": 1.0124144228498009,
        "R3": 0.9466670636010056
    },
    "Sunshine Coast": {
        "R1": 0.7657071722209816,
        "R2": 0.8347985347985349,
        "R3": 0.6752681533752564
    },
    "Grafton": {
        "R1": 0.8564596191424296,
        "R2": 0.8118106465749874,
        "R3": 0.7497156941751799
    },
    "Hawkesbury": {
        "R1": 0.950938712642747,
        "R2": 0.8334012008541227,
        "R3": 0.22772693979910463
    },
    "Hobart": {
        "R1": 0.9608393598739559,
        "R2": 0.9738429358571726,
        "R3": 0.9351591624829391
    },
    "Carnarvon": {
        "R1": 1.0114566666874938,
        "R2": 0.9670505767577643,
        "R3": 0.8774645786479649
    },
    "Port Augusta": {
        "R1": 0.9165323582966736,
        "R2": 0.775137168033343,
        "R3": 0.851233638265015
    }
}

stake = 500
loss = 0
win = 0
# Calculate minimum returns
returns = []
for location, race_data in arbitrage_sums.items():
    for race, arbitrage_sum in race_data.items():
        if arbitrage_sum > 1:
            loss += 1
        else:
            win += 1
        returns.append((stake / arbitrage_sum) - stake)
print(sum(returns),win,loss,win/(win+loss))
print(((sum(returns)/len(returns))*31)+sum(returns))