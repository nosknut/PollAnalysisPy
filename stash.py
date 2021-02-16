
import csv
import matplotlib.pyplot as plt

ageRanges=[]

def countSame(values):
    bucket = {}
    for value in values:
        if not value in bucket:
            bucket[value] = 0
        bucket[value] += 1
    return bucket

def groupAge(ageCountMap):
    groupBucket = {}
    for minAge, maxAge in ageRanges:
        bucketName = str(minAge)+'-'+str(maxAge)
        groupBucket[bucketName]=0
        for ageString, count in ageCountMap.items():
            age = int(ageString)
            if age >= minAge and age <= maxAge:
                groupBucket[bucketName] += 1
    return groupBucket


def genderBuckets(vals):
    bucket = {}
    for val in vals:
        age = val['Alder']
        gender = val['Kjønn']
        bucket[gender] = bucket[gender] if (gender in bucket) else []
        bucket[gender].append(age)

    i = 0
    for gender, ages in bucket.items():
        validGenders = ['Mann', 'Kvinne']
        if not gender in validGenders:
            continue
        ageBucket = groupAge(countSame(ages))
        labels=[]
        sizes=[]
        for minAge, maxAge in ageRanges:
            rangeName=str(minAge)+'-'+str(maxAge)
            labels.append(rangeName)
            sizes.append(ageBucket[rangeName])
        plt.figure('Aldersgruppe for kjonn '+str(gender))
        i += 1
        plt.pie(sizes, labels=labels, autopct='%1.1f%%',
                shadow=True, startangle=140, colors=('red', 'brown', 'green', 'yellow', 'purple', 'orange'))
        plt.axis('equal')
        plt.title("Aldersgrupper for " + gender)

