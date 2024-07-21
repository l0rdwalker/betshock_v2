

#data = "2.7, 6, 6.5, 8, 11, 11, 12, 13, 15, 19, 23, 26, 51, 71, 126"
#data = data.split(" ")
#for idx in range(0,len(data)):
#    data[idx] = float(data[idx])
starting_price = [5.5, 2.9, 2.8, 19, 26, 12, 13, 41, 26, 41, 41, 41]
highest = [5.5, 3.8, 4.2, 21.5, 26, 16, 21.5, 43, 51, 61, 71, 81, 101]

data = starting_price
data = sorted(data)
print(len(data))
i_p = 0
for entry in data:
    i_p += 1/entry
    print(i_p,1/entry,entry)
print(i_p)