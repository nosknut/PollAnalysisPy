# -*- coding: utf-8 -*-
import numpy as np
import csv
import matplotlib.pyplot as plt
import json
from pathlib import Path
from range_key_dict import RangeKeyDict
from matplotlib.backends.backend_pdf import PdfPages

man = 'Mann'
woman = 'Kvinne'
blue = 'cornflowerblue'

colorOrder = [
    'red',
    blue,
    'olive',
    'orange',
    'blueviolet',
    'brown',
    'indigo',
    'purple',
    'magenta',
    'cyan',
    'pink',
    'lightgray',
    'goldenrod',
]

ageRangeMap = {
    (0, 19): {'range': '0-18', 'color': 'red'},
    (19, 26): {'range': '19-25', 'color': blue},
    (26, 31): {'range': '26-30', 'color': 'olive'},
    (31, 41): {'range': '31-40', 'color': 'orange'},
    (41, 51): {'range': '41-50', 'color': 'blueviolet'},
    (51, 101): {'range': '51-100', 'color': 'brown'},
}
    
figSize=(12, 6)
dumpFile = 'ignoredAwnsers.json'
ageRangeLabels=list(map(lambda b:b['range'], ageRangeMap.values()))
ageRanges = RangeKeyDict(ageRangeMap)

def getAgeRangeForGender(vals, gender):
    bucket = {}
    for config in ageRangeMap.values():
        bucket[config['range']] = 0
    for val in vals:
        age = int(val['Alder'])
        ageRange = ageRanges[age]['range'] if age else None
        if ageRange:
            if gender == val['Kjønn']:
                bucket[ageRange] += 1
    return bucket

def drawPieFromBucket(title, bucket):
    labels = []
    sizes = []
    for k, v in bucket.items():
        labels.append(k)
        sizes.append(v)
    drawPie(title, sizes, labels)


def countFieldMatchingValue(vals, field, value):
    count = 0
    for row in vals:
        if row[field] == value:
            count += 1
    return count


def drawGenderRelationDiagram(vals, title):
    labels = [man, woman]
    sizes = [
        countFieldMatchingValue(vals, 'Kjønn', man),
        countFieldMatchingValue(vals, 'Kjønn', woman)
    ]
    drawPie(title, sizes, labels)


def drawPie(title, sizes, labels, colors=colorOrder):
    plt.figure(title, figsize=figSize)
    plt.title(title)
    plt.axis('equal')
    plt.pie(sizes, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=140, colors=colors)


def extractColumn(rows, key):
    return map(lambda row: row[key], rows)


def countSame(values):
    bucket = {}
    for value in values:
        if not value in bucket:
            bucket[value] = 0
        bucket[value] += 1
    return bucket

# bucket{awnser: numvotes}
def resultBucketForQuestion(rows, question):
    return countSame(extractColumn(rows, question))

def filterRowsMatching(rows, key, value):
    vals = []
    for row in rows:
        if row[key] == value:
            vals.append(row)
    return vals

def getBadAwnsers():
    badAwnsers = {}
    if Path(dumpFile).is_file():
        with open(dumpFile, "r", encoding="utf8") as f:
            val = f.read()
            if val:
                badAwnsers = json.loads(val)
            f.close()
    return badAwnsers


def writeToJson(val, name):
    with open(name, "w+", encoding="utf8") as f:
        json.dump(val, f, indent=2, ensure_ascii=False)
        f.close()


def refreshSanetizationFile(vals):
    ignoredResponses = getBadAwnsers()
    for q in vals[0].keys():
        print('\n\n\n'+q)
        if not q in ignoredResponses:
            ignoredResponses[q] = []
        c = countSame(extractColumn(vals, q))
        keys = list(c.keys())
        for i in range(len(keys)):
            k = keys[i]
            v = c[k]
            removedText = "(filtered): " if k in ignoredResponses[q] else ""
            print(removedText+str(i)+': '+str(v)+': '+str(k))
        indexesToFilterOut = input(
            '\nType a comma separated list with no spaces of the ones you want removed: ')
        if not indexesToFilterOut:
            print('None were removed')
            continue
        for i in map(int, indexesToFilterOut.split(',')):
            ignoredResponses[q].append(keys[i])
    writeToJson(ignoredResponses, dumpFile)
    return ignoredResponses


def drawGroupsForAllQuestions(vals, groups, groupLabel, badQuestions, title):
    for q in filrterList(vals[0].keys(), badQuestions):
        drawGroupedResults(vals, groups, q, title, groupLabel)

def ageSanetization(vals):
    sanetized = []
    for val in vals:
        try:
            age = int(val['Alder'])
            if ageRanges[age]:
                sanetized.append(val)
        except KeyError:
            print('Found bad age: '+str(age))
    return sanetized

def groupRowsByField(rows, field, buckets, bucketMatcher):
    bucket = {}
    for b in buckets:
        bucket[b]=[]
    for row in rows:
        val = row[field]
        bucketKey=bucketMatcher(val, buckets)
        if bucketKey in bucket:
            bucket[bucketKey].append(row)

    for k, v in bucket.items():
        if len(v) == 0:
            bucket.pop(k, None)
    return bucket

def groupRowsByAge(rows):
    return groupRowsByField(rows, 'Alder', ageRangeLabels, lambda val, buckets: ageRanges[int(val)]['range'])

def filrterList(vals, excludedVals):
    return filter(lambda val: val not in excludedVals, vals)

def countTotalVotesInBucket(bucket):
    countBucket={}
    for bucketKey, rows in bucket.items():
        countBucket[bucketKey]=len(rows)
    return countBucket

def protectedDevide(a, b):
    if b == 0:
        return a
    return a/b

#orderedRows: normal rows in groups of the x axis ticks
def drawGroupedResults(unorderedRows, orderedRows, question, title, bucketLabel, asPercentage=True):
    totalVotesBucket=countTotalVotesInBucket(orderedRows)
    badAwnsers = getBadAwnsers()
    bucketLabels = orderedRows.keys()
    plt.figure(question+'_'+title, figsize=figSize)
    n_groups = len(bucketLabels)
    #fig, ax = plt.subplots()
    index = np.arange(n_groups)

    validAwnsers = countSame(filrterList(extractColumn(
        unorderedRows, question), badAwnsers[question])).keys()
    xAxisValueAwnserMap = {}
    numBars=0
    for a in validAwnsers:
        xAxisValueAwnserMap[a] = []
    for ageRange in bucketLabels:
        totalVotesInAgeRange=totalVotesBucket[ageRange]
        rows = orderedRows[ageRange]
        awnserCountMap = countSame(filrterList(
            extractColumn(rows, question), badAwnsers[question]))
        for awnser in validAwnsers:
            count = awnserCountMap[awnser] if awnser in awnserCountMap else 0
            percentageOfAgeGroup=protectedDevide(count, totalVotesInAgeRange)*100
            xAxisValueAwnserMap[awnser].append(percentageOfAgeGroup if asPercentage else count)
            numBars+=(1/len(bucketLabels))
    
    #the value is 0.15 is tuned for 5 bars
    bar_width = 0.15 / (numBars / 5)
    opacity = 0.8

    numValidAwnsers=len(validAwnsers)
    for i, a in enumerate(validAwnsers):
        plt.bar(index + ((i+1)*bar_width), xAxisValueAwnserMap[a], bar_width,
                alpha=opacity,
                color=colorOrder[i],
                label=a)

    plt.suptitle(title)
    plt.title('Spørsmål: '+question)
    plt.xlabel(bucketLabel)
    plt.ylabel('Prosent av stemmer i respektive grupper' if asPercentage else 'Stemmer')
    plt.xticks(index + (numValidAwnsers/2*bar_width), bucketLabels)
    plt.legend()
    plt.tight_layout()


def filterIrelevantQuestions(vals, questions):
    filtered=[]
    for val in vals:
        for q in questions:
            val.pop(q, None)
            filtered.append(val)
    return filtered

def saveFigsToPdf():
        pdf=PdfPages('output.pdf')
        for fig in range(1, plt.gcf().number + 1): ## will open an empty extra figure :(
            pdf.savefig( fig )
        pdf.close()

def groupRowsByGender(rows):
    return groupRowsByField(rows, 'Kjønn', ['Mann', 'Kvinne'], lambda val, buckets: val)

def drawPieForAllQuestions(rows, questionTitlePrefix):
        for question in rows[0].keys():
            drawPieFromBucket(questionTitlePrefix+question, resultBucketForQuestion(rows, question))

def main():
    with open('data.csv', encoding="utf-8") as csvFile:
        vals = list(csv.DictReader(csvFile))
        vals = ageSanetization(vals)
        #refreshSanetizationFile(vals)
        drawPieFromBucket('Kvinnelig aldersgruppe', getAgeRangeForGender(vals, woman))
        drawPieFromBucket('Mannlig aldersgruppe', getAgeRangeForGender(vals, man))
        drawGenderRelationDiagram(vals, 'Kjønnsfordeling i undersøkelsen')
        drawPieFromBucket('Kontrollspørsmål hvor man er instruert til å svare nei', resultBucketForQuestion(
            vals, 'Kontrollspørsmål: Svar "Nei"'))
        badQuestions=['Har du noe på hjertet?', 'Tidsmerke', 'Alder']
        drawGroupsForAllQuestions(vals, groupRowsByAge(vals), 'Aldersgruppe', badQuestions, 'Forskjellig respons fra forskjellige aldersgrupper')
        drawGroupsForAllQuestions(vals, groupRowsByGender(vals), 'Kjønnn', badQuestions, 'Forskjellig respons fra forskjellige kjønn')
        drawPieForAllQuestions(filterRowsMatching(vals, 'Kjønn', 'Mann'), 'Hva menn svarte på ')
        drawPieForAllQuestions(filterRowsMatching(vals, 'Kjønn', 'Kvinne'), 'Hva kvinner svarte på ')
        drawPieForAllQuestions(vals, '')
        saveFigsToPdf()
        #plt.show()
main()
