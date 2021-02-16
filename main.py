# -*- coding: utf-8 -*-
import csv
import matplotlib.pyplot as plt

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

ageRanges = {
    '0-18': {'range': range(0, 19), 'color': 'red'},
    '19-25': {'range': range(19, 26), 'color': blue},
    '26-30': {'range': range(26, 31), 'color': 'olive'},
    '31-40': {'range': range(31, 41), 'color': 'orange'},
    '41-50': {'range': range(41, 51), 'color': 'blueviolet'},
    '51-100': {'range': range(51, 101), 'color': 'brown'},
}


def getAgeRangeForGender(vals, gender):
    bucket = {}
    for r, config in ageRanges.items():
        bucket[r] = 0
    for val in vals:
        age = int(val['Alder'])
        ageRange = None
        for r, config in ageRanges.items():
            if age in config['range']:
                ageRange = r
                break
        if ageRange:
            if gender == val['Kjønn']:
                bucket[ageRange] += 1
    return bucket


def drawGenderDiagram(vals, gender, title):
    bucket = getAgeRangeForGender(vals, gender)
    labels = []
    sizes = []
    colors = []
    for k, v in ageRanges.items():
        labels.append(k)
        sizes.append(bucket[k])
        colors.append(v['color'])
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


def sanetize(vals):
    filtered = []
    for q in vals[0].keys():
        c = countSame(extractColumn(vals, q))
        i = 0
        print(q)
        for k, v in c.items():
            print(str(i)+': '+str(v)+': '+str(k))
            i += 1
        print(input('A, b, c'))
    return filtered

def drawQuestionToAgeRelationship():
    return

def main():
    with open('data.csv', encoding="utf-8") as csvFile:
        vals = sanetize(list(csv.DictReader(csvFile)))
        #drawGenderDiagram(vals, woman, 'Kvinnelig aldersgruppe')
        #drawGenderDiagram(vals, man, 'Mannlig aldersgruppe')
        #drawGenderRelationDiagram(vals, 'Kjønnsfordeling i undersøkelsen')
        drawConfirmationQuestionDiagram(
            vals, 'Kontrollspørsmål: Svar "Nei"', 'Kontrollspørsmål hvor man er instruert til å svare nei')
        maleRows = filterRowsMatching(vals, 'Kjønn', 'Mann')
        femaleRows = filterRowsMatching(vals, 'Kjønn', 'Kvinne')
        drawQuestionToAgeRelationship(vals, 'Forskjellig respons fra forskjellige aldersgrupper')
        #for question in vals[0].keys():
        #    drawConfirmationQuestionDiagram(
        #        maleRows, question, 'Hva menn svarte på '+question)
        #    drawConfirmationQuestionDiagram(
        #        femaleRows, question, 'Hva kvinner svarte på '+question)
        plt.show()


main()
