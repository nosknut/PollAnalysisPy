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
        try:
            ageRange = ageRanges[age]['range'] if age else None
            if ageRange:
                if gender == val['Kjønn']:
                    bucket[ageRange] += 1
        except KeyError:
            print('Fount bad age: '+str(age))
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


def sanetize(vals):
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
            print(ignoredResponses)
            with open(dumpFile, "w+", encoding="utf8") as f:
                json.dump(ignoredResponses, f, indent=2, ensure_ascii=False)
                f.close()
    return ignoredResponses


def drawQuestionToAgeRelationships(vals, title):
    for q in vals[0].keys():
        drawQuestionToAgeRelationship(vals, q, title)


def drawQuestionToAgeRelationship(vals, question, title):
    ageBucket = {}

    for val in vals:
        if val['Alder'] in []:
            return

    labels = []
    sizes = []

    for k, v in countSame(extractColumn(vals, question)).items():
        labels.append(k)
        sizes.append(v)
    # data to plot
    n_groups = 4
    means_frank = (90, 55, 40, 65)
    means_guido = (85, 62, 54, 20)

    # create plot
    fig, ax = plt.subplots()
    index = np.arange(n_groups)
    bar_width = 0.35
    opacity = 0.8

    rects1 = plt.bar(index, means_frank, bar_width,
                     alpha=opacity,
                     color='b',
                     label='Frank')

    rects2 = plt.bar(index + bar_width, means_guido, bar_width,
                     alpha=opacity,
                     color='g',
                     label='Guido')

    plt.xlabel('Alternativ')
    plt.ylabel('Stemmer')
    plt.title(title + question)
    plt.xticks(index + bar_width, ('A', 'B', 'C', 'D'))
    plt.legend()

    plt.tight_layout()
    return


def main():
    with open('data.csv', encoding="utf-8") as csvFile:
        vals = list(csv.DictReader(csvFile))
        # vals=sanetize(vals)#get rid of noisy and negligable awnsers
        drawGenderDiagram(vals, woman, 'Kvinnelig aldersgruppe')
        drawGenderDiagram(vals, man, 'Mannlig aldersgruppe')
        drawGenderRelationDiagram(vals, 'Kjønnsfordeling i undersøkelsen')
        # drawConfirmationQuestionDiagram(
        #    vals, 'Kontrollspørsmål: Svar "Nei"', 'Kontrollspørsmål hvor man er instruert til å svare nei')
        #maleRows = filterRowsMatching(vals, 'Kjønn', 'Mann')
        #femaleRows = filterRowsMatching(vals, 'Kjønn', 'Kvinne')
        drawQuestionToAgeRelationship(
            vals, 'Alder', 'Forskjellig respons fra forskjellige aldersgrupper')
        #drawQuestionToAgeRelationships(vals, 'Forskjellig respons fra forskjellige aldersgrupper')
        # for question in vals[0].keys():
        #    drawConfirmationQuestionDiagram(
        #        maleRows, question, 'Hva menn svarte på '+question)
        #    drawConfirmationQuestionDiagram(
        #        femaleRows, question, 'Hva kvinner svarte på '+question)
        plt.show()


main()
