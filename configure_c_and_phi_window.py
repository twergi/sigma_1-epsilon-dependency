import PySimpleGUI as sg
from utils import float_comma


def configure_c_phi(DATA):
    ''' Open window to configure c and phi
    '''

    changes = False

    layout = [
        [
            sg.Column([
                [sg.Text('\u03C6')],
                [sg.Text('c')]
            ]),
            sg.Column([
                [sg.Input(default_text=DATA['value_phi'], key='-phi-', size=(5, 1))],
                [sg.Input(default_text=DATA['value_c'], key='-c-', size=(5, 1))]
            ]),
            sg.Column([
                [sg.Text('[°]')],
                [sg.Text('[kPa]')]
            ])
        ],
        [
            sg.Button('OK', bind_return_key=True), sg.Button('Cancel')
        ]
    ]
    configuration = sg.Window(title='', layout=layout)
    while True:
        event_4, values_4 = configuration.read()
        if event_4 == 'OK':
            if values_4['-phi-'] == '' or values_4['-phi-'] == '0':
                sg.popup('\u03C6 is not set')
                continue
            elif values_4['-c-'] == '':
                sg.popup('c is not set')
                continue
            else:
                try:
                    float_comma(values_4['-phi-'])
                    float_comma(values_4['-c-'])
                except ValueError:
                    sg.popup('Wrong \u03C6 or c')
                    continue
                DATA['value_phi'] = float_comma(values_4['-phi-'])
                DATA['value_c'] = float_comma(values_4['-c-'])
                changes = True
                break
        if event_4 in [sg.WIN_CLOSED, 'Cancel']:
            break
    configuration.close()
    return changes
