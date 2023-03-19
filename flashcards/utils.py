import pandas as pd
import genanki
import csv
import random


list =[['Question', 'Jaki jest kolor sierści kota syjamskiego?', 'Answer', 'Ciemny brąz lub czarny'], ['Question', 'Jakie są cechy charakterystyczne kota brytyjskiego?', 'Answer', 'Krótka sierść, duże uszy i okrągłe oczy'], ['Question', 'Jakie są cechy charakterystyczne kota perskiego?', 'Answer', 'Długa sierść, duże oczy i krótkie uszy'], ['Question', 'Jaki jest kolor sierści kota rosyjskiego niebieskiego?', 'Answer', 'Niebieski'], ['Question', 'Jaki jest kolor sierści kota sfinksa?', 'Answer', 'Brak sierści'], ['Question', 'Jakie są cechy charakterystyczne kota syberyjskiego?', 'Answer', 'Gruba sierść, duże uszy i okrągłe oczy'], ['Question', 'Jaki jest kolor sierści kota bengalskiego?', 'Answer', 'Ciemny brąz lub czarny z jasnymi plamami'], ['Question', 'Jakie są cechy charakterystyczne kota ragdolla?', 'Answer', 'Długa sierść, duże oczy i krótkie uszy'], ['Question', 'Jaki jest kolor sierści kota norweskiego leśnego?', 'Answer', 'Ciemny brąz lub czarny z jasnymi plamami'], ['Question', 'Jakie są cechy charakterystyczne kota maine coona?', 'Answer', 'Gruba sierść, duże uszy i okrągłe oczy']]

list_1 = []
list_2 = []

for item in list:
    list_1.append(item[1])
    list_2.append(item[3])



# df = pandas.DataFrame(data={"col1": list_1, "col2": list_2})
# df.to_csv("./file.csv", sep=',',index=False)


def create_xlsx(list, pk):
    list_1 = []
    list_2 = []

    for item in list:
            list_1.append(item[1])
            list_2.append(item[3])

    d = {'col1': list_1, 'col2': list_2}
    df = pd.DataFrame(data=d)
    return df.to_excel(f"./xlsx_files/{pk}.xlsx", index=False)

def create_csv(list, pk):
    list_1 = []
    list_2 = []

    for item in list:
        list_1.append(item[1])
        list_2.append(item[3])

    d = {'col1': list_1, 'col2': list_2}
    df = pd.DataFrame(data=d)
    return df.to_csv(f"./csv_files/{pk}.csv", index=False)





# Define the fields for your Anki notes


def create_apkg_from_csv(deck_pk):
    my_model = genanki.Model(
    random.randrange(1 << 30, 1 << 31),
    'My Model',
    fields=[
        {'name': 'Front'},
        {'name': 'Back'},

    ],
    templates=[
        {
        'name': 'Card 1',
        'qfmt': '{{Front}}',
        'afmt': '{{FrontSide}}<hr id="answer">{{Back}}',
        },
    ])

    # Read the data from the CSV file
    with open(f'./csv_files/{deck_pk}.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader) # Skip the header row
        notes = [genanki.Note(
            model=my_model,
            fields=[row[0], row[1]]
        ) for row in reader]

    # Create the Anki deck and add the notes to it
    my_deck = genanki.Deck(
    random.randrange(1 << 30, 1 << 31),
    f'{deck_pk}',
    
    )
    for note in notes:
        my_deck.add_note(note)
    

    # Create the Anki package and write it to a file
    my_package = genanki.Package(my_deck)
    return my_package.write_to_file(f'./apkg_files/{deck_pk}.apkg')