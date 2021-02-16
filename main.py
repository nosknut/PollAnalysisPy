# -*- coding: utf-8 -*-
import numpy as np
import csv
import matplotlib.pyplot as plt
import json
from pathlib import Path
from range_key_dict import RangeKeyDict

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

# ageRanges = {
#    '0-18': {'range': range(0, 19), 'color': 'red'},
#    '19-25': {'range': range(19, 26), 'color': blue},
#    '26-30': {'range': range(26, 31), 'color': 'olive'},
#    '31-40': {'range': range(31, 41), 'color': 'orange'},
#    '41-50': {'range': range(41, 51), 'color': 'blueviolet'},
#    '51-100': {'range': range(51, 101), 'color': 'brown'},
# }

ageRangeMap = {
    (0, 19): {'range': '0-18', 'color': 'red'},
    (19, 26): {'range': '19-25', 'color': blue},
    (26, 31): {'range': '26-30', 'color': 'olive'},
    (31, 41): {'range': '31-40', 'color': 'orange'},
    (41, 51): {'range': '41-50', 'color': 'blueviolet'},
    (51, 101): {'range': '51-100', 'color': 'brown'},
}

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


def drawGenderDiagram(vals, gender, title):
    bucket = getAgeRangeForGender(vals, gender)
    labels = []
    sizes = []
    colors = []
    for config in ageRangeMap.values():
        r = config['range']
        labels.append(r)
        sizes.append(bucket[r])
        colors.append(config['color'])
    drawPie(title, sizes, labels, colors)


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
    colors = [blue, 'red']
    drawPie(title, sizes, labels, colors)


def drawPie(title, sizes, labels, colors=colorOrder):
    plt.figure(title)
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


def drawConfirmationQuestionDiagram(vals, field, title):
    labels = []
    sizes = []
    for k, v in countSame(extractColumn(vals, field)).items():
        labels.append(k)
        sizes.append(v)
    drawPie(title, sizes, labels)


def filterRowsMatching(rows, key, value):
    vals = []
    for row in rows:
        if row[key] == value:
            vals.append(row)
    return vals


dumpFile = 'ignoredAwnsers.json'


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


def drawQuestionToAgeRelationships(vals, title):
    for q in vals[0].keys():
        drawQuestionToAgeRelationship(vals, q, title)


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


def groupRowsByAge(vals):
    ageBucket = {}
    for c in ageRangeMap.values():
        ageBucket[c['range']] = []

    for val in vals:
        age = int(val['Alder'])
        r = ageRanges[age]['range']
        ageBucket[r].append(val)

    for k, v in ageBucket.items():
        if len(v) == 0:
            ageBucket.pop(k, None)

    return ageBucket


def filrterList(vals, excludedVals):
    return filter(lambda val: val not in excludedVals, vals)


def drawQuestionToAgeRelationship(vals, question, title):
    ageBucket = groupRowsByAge(vals)
    badAwnsers = getBadAwnsers()

    plt.figure(question+'_'+title)
    n_groups = len(ageBucket.keys())
    #fig, ax = plt.subplots()
    index = np.arange(n_groups)
    bar_width = 0.35
    opacity = 0.8

    bucketLabels = ageBucket.keys()
    validAwnsers = countSame(filrterList(extractColumn(
        vals, question), badAwnsers[question])).keys()
    xAxisValueAwnserMap = {}
    for a in validAwnsers:
        xAxisValueAwnserMap[a] = []
    for ageRange in bucketLabels:
        rows = ageBucket[ageRange]
        awnserCountMap = countSame(filrterList(
            extractColumn(rows, question), badAwnsers[question]))
        for awnser in validAwnsers:
            count = awnserCountMap[awnser] if awnser in awnserCountMap else 0
            xAxisValueAwnserMap[awnser].append(count)

    for i, a in enumerate(validAwnsers):
        plt.bar(index + (float(i)*bar_width), xAxisValueAwnserMap[a], bar_width,
                alpha=opacity,
                color=colorOrder[i],
                label=a)

    plt.suptitle(title)
    plt.title('Spørsmål: '+question)
    plt.xlabel('Aldersgruppe')
    plt.ylabel('Stemmer')
    plt.xticks(index + bar_width, bucketLabels)
    plt.legend()
    plt.tight_layout()


def filterIrelevantQuestions(vals, questions):
    filtered=[]
    for val in vals:
        for q in questions:
            val.pop(q, None)
            filtered.append(val)
    return filtered

def main():
    with open('data.csv', encoding="utf-8") as csvFile:
        vals = list(csv.DictReader(csvFile))
        vals = ageSanetization(vals)
        #refreshSanetizationFile(vals)
        #drawGenderDiagram(vals, woman, 'Kvinnelig aldersgruppe')
        #drawGenderDiagram(vals, man, 'Mannlig aldersgruppe')
        #drawGenderRelationDiagram(vals, 'Kjønnsfordeling i undersøkelsen')
        # drawConfirmationQuestionDiagram(
        #    vals, 'Kontrollspørsmål: Svar "Nei"', 'Kontrollspørsmål hvor man er instruert til å svare nei')
        #maleRows = filterRowsMatching(vals, 'Kjønn', 'Mann')
        #femaleRows = filterRowsMatching(vals, 'Kjønn', 'Kvinne')
        drawQuestionToAgeRelationship(
            vals, 'Hvordan føler du deg i dag?', 'Forskjellig respons fra forskjellige aldersgrupper')
        
        #badQuestions=['Har du noe på hjertet?', 'Tidsmerke', 'Alder']
        #for q in filrterList(vals[0].keys(), badQuestions):
        #    print(q)
        #    drawQuestionToAgeRelationship(
        #        vals, q, 'Forskjellig respons fra forskjellige aldersgrupper')
        
        #drawQuestionToAgeRelationships(vals, 'Forskjellig respons fra forskjellige aldersgrupper')
        # for question in vals[0].keys():
        #    drawConfirmationQuestionDiagram(
        #        maleRows, question, 'Hva menn svarte på '+question)
        #    drawConfirmationQuestionDiagram(
        #        femaleRows, question, 'Hva kvinner svarte på '+question)
        plt.show()


main()
