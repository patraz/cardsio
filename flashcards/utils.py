import pandas as pd
import genanki
import csv
import random
import ast

def create_xlsx(list, pk):
    list_1 = []
    list_2 = []

    for item in list:
            list_1.append(item[0])
            list_2.append(item[1])

    d = {'col1': list_1, 'col2': list_2}
    df = pd.DataFrame(data=d)
    return df.to_excel(f"./xlsx_files/{pk}.xlsx", index=False)

def create_csv(list, pk):
    list_1 = []
    list_2 = []

    for item in list:
        list_1.append(item[0])
        list_2.append(item[1])

    d = {'col1': list_1, 'col2': list_2}
    df = pd.DataFrame(data=d)
    return df.to_csv(f"./csv_files/{pk}.csv", index=False)

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
    with open(f'./csv_files/{deck_pk}.csv', 'r', encoding='utf-8') as file:
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

def create_list_of_flashcards(d_old_str):
        l_cards = d_old_str.replace(":", ",")
        list_from_string = ast.literal_eval(l_cards)
        return list_from_string