from random import randrange
import PySimpleGUI as sg
from os import path
from modules.utils import (
    float_comma,
    read_csv,
    split_graph
)


def browse_window(DATA, btnColor):
    ''' Create window where new graphs are imported
    '''

    changes = False

    # Create layout for window
    layout = [
        [
            sg.In(size=(20, 1), key='-file-'),
            sg.FileBrowse(
                file_types=(('CSV files', '*.csv'),)
            )
        ],
        [sg.Column([
            [sg.Text('Enter graph name')],
            [sg.Input(key='-graphname-', size=(20, 1))]
        ]),
            sg.Column([
                [sg.Text('\u03C33 [kPa]')],
                [sg.Input(key='-sigma3-', size=(20, 1))]])
        ],
        [sg.Column(
            [[
                sg.Text('Enter R_f'),
                sg.Input(
                    default_text=DATA['R_f'],
                    key='-R_f-',
                    size=(10, 1)
                )
            ]]
        )],
        [
            sg.Column(
                [[
                    sg.Input(
                        default_text=f"#{randrange(40, 230, 1):02x}{randrange(40, 230, 1):02x}{randrange(40, 230, 1):02x}",
                        key='-color-',
                        disabled=True,
                        size=(10, 1),
                        enable_events=True,
                        disabled_readonly_background_color=btnColor
                    ),
                    sg.ColorChooserButton(
                        button_text='Pick color',
                        target='-color-'
                    )
                ]]
            )
        ],
        [sg.Button('OK', bind_return_key=True), sg.Button('Cancel')]
    ]

    if DATA['value_phi'] == 0 and DATA['value_c'] == 0:
        layout.insert(-1,
                      [sg.Column([
                          [sg.Text('Enter \u03C6 [°]')],
                          [sg.Input(key='-value_phi-', size=(10, 1))]
                      ]),
                          sg.Column([
                              [sg.Text('c [kPa]')],
                              [sg.Input(key='-value_c-', size=(10, 1))]])
                      ],
                      )
    browse_files = sg.Window('Browse files', layout)

    # Create event loop
    while True:
        event_2, values_2 = browse_files.read()
        # When user presses OK button
        if event_2 == 'OK':
            if DATA['value_phi'] == 0 and DATA['value_c'] == 0:
                # Checks if phi is empty
                if (
                    values_2['-value_phi-'] == ''
                    or values_2['-value_phi-'] == '0'
                ):
                    sg.popup('\u03C6 is not set')
                    continue

                # Checks if c is empty
                if values_2['-value_c-'] == '':
                    sg.popup('c is not set')
                    continue

            # Checks path
            if values_2['-file-'] == '' or not path.exists(values_2['-file-']):
                sg.popup('Wrong path')
                continue

            # Checks graph name
            elif (
                values_2['-graphname-'] == ''
            ):
                sg.popup('Wrong graph name')
                continue

            # Checks sigma
            elif values_2['-sigma3-'] == '':
                sg.popup('Wrong \u03C33')
                continue

            # If everything is ok check if sigma3 is float, then reads csv and adds graph to dic graphs
            else:
                try:
                    float_comma(values_2['-sigma3-'])
                    if DATA['value_phi'] == 0 and DATA['value_c'] == 0:
                        float_comma(values_2['-value_phi-'])
                        float_comma(values_2['-value_c-'])
                    float_comma(values_2['-R_f-'])
                except ValueError:
                    sg.popup('Wrong \u03C33m, \u03C6 or c')
                    continue

                if DATA['value_phi'] == 0 and DATA['value_c'] == 0:
                    DATA['value_phi'] = float_comma(values_2['-value_phi-'])
                    DATA['value_c'] = float_comma(values_2['-value_c-'])

                read_csv(
                    values_2['-file-'],
                    values_2['-graphname-'],
                    float_comma(values_2['-sigma3-']),
                    float_comma(values_2['-R_f-']),
                    values_2['-color-'],
                    DATA
                )

                split_graph(values_2['-graphname-'], DATA)
                changes = True
                break

        # Closes window when window is closed or user presses Cancel button
        if event_2 in [sg.WIN_CLOSED, 'Cancel']:
            break

    # Closes window
    browse_files.close()
    return changes
