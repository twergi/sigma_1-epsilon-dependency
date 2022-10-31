import PySimpleGUI as sg
from utils import float_comma


def edit_defaults_window(DATA):
    ''' Opens window to edit default values
    '''
    changes = False

    layout = [
        [sg.Column(
            [
                [sg.Text(
                    'R_f',
                    tooltip='Default for graphs generalization and file browsing'
                )],
                [sg.Text(
                    'p_ref',
                    tooltip='Default for graphs generalization'
                )]
            ]
        ),
        sg.Column(
            [
                [sg.Input(default_text=DATA['R_f'], size=(10, 1), key='-R_f-')],
                [sg.Input(default_text=DATA['gen']['p_ref'], size=(10, 1), key='-p_ref-')]
            ]
        ),
        sg.Column(
            [
                [sg.Text('[-]')],
                [sg.Text('[kPa]')]
            ]
        )],
        [sg.Button('OK'), sg.Button('Cancel')]
    ]

    window = sg.Window('Edit defauls', layout)
    while True:
        event, values = window.read()

        if event in ('Cancel', sg.WIN_CLOSED):
            break

        if event == 'OK':
            try:
                R_f = float_comma(values['-R_f-'])
                p_ref = float_comma(values['-p_ref-'])
            except:
                sg.popup('Incorrect values')
                continue
            DATA['R_f'] = R_f
            DATA['gen']['p_ref'] = p_ref
            changes = True
            break
    window.close()
    return changes
