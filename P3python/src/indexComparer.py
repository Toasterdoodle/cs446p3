toRead1 = open('scientificBM25.txt', 'r')
toRead2 = open('scientificOR.txt', 'r')
noDuplicates = set()
for line in toRead1:
    line = line.split()
    print(line)
    if line[2] not in noDuplicates:
        noDuplicates.add(line[2])
    else:
        print('Duplicate Detected')
for line in toRead2:
    line = line.split()
    print(line)
    if line[2] not in noDuplicates:
        noDuplicates.add(line[2])
    else:
        print('Duplicate Detected')
print(len(noDuplicates))