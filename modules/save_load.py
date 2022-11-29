import PySimpleGUI as sg
from json import dump, load, JSONDecodeError


def save_load(w_type, DATA):
    ''' Opens window to save or load save file'''

    changes = False

    # Set layout depending on window type parameter
    if w_type == 'Save':
        layout = [
            [
                sg.Text('Choose where to save current data:')],
            [
                sg.Input(key='SaveAs'),
                sg.FileSaveAs(
                    button_text='Browse',
                    file_types=(('TXT files', '*.txt'),)
                ),
            ],
            [
                sg.Button('Save data'), sg.Button('Cancel')
            ]
        ]
    elif w_type == 'Load':
        layout = [
            [sg.Text('Choose file to load data:')],
            [
                sg.Input(key='Load'),
                sg.FileBrowse(
                    button_text='Browse',
                    file_types=(('TXT files', '*.txt'),),
                ),
            ],
            [
                sg.Button('Load data'),
                sg.Button('Cancel')
            ]
        ]
    save_load_window = sg.Window(title=w_type, layout=layout)
    while True:
        event_4, values_4 = save_load_window.read()
        if event_4 == 'Save data':
            save_file(values_4['SaveAs'], DATA)
            changes = True
            break
        if event_4 == 'Load data':
            load_file(values_4['Load'], DATA)
            changes = True
            break
        if event_4 in [sg.WIN_CLOSED, 'Cancel']:
            break
    save_load_window.close()
    return changes


def save_file(file_name, DATA):
    # Saves all data in save file
    with open(file_name, 'w') as file:
        dump(DATA, file, indent=4)


def load_file(file_name, DATA):
    # Loads provided save file and inputs data in graphs and graphs_altered
    with open(file_name) as load_file:
        try:
            loaded_data = load(load_file)
            for key in loaded_data.keys():
                DATA[key] = loaded_data[key]
        except JSONDecodeError:
            sg.popup('File is not supported')
