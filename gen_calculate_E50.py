import PySimpleGUI as sg
from utils import float_comma
from math import log, tan, radians, e


def calculate_E50_window(DATA):
    ''' Opens window to calculate E50 based on 
        generalized m and b 
    '''

    layout = [
        [sg.Text('Input \u03C33 to calculate E50 with parameters:')],
        [sg.Text(f"m={round(DATA['gen']['m'], 3)}")],
        [sg.Text(f"b={round(DATA['gen']['b'], 3)}")],
        [sg.Input(size=(10, 1), key='-SIGMA3-'), sg.Button('Calculate', key='-CALCULATE-')],
        [sg.Text('', key='-E50-')],
        [sg.Text('')],
        [sg.Button('Close')]
    ]

    window = sg.Window('Calculate E50', layout)
    while True:
        event, value = window.read()

        if event in ('Close', sg.WIN_CLOSED):
            break
        if event == '-CALCULATE-':
            try:
                sigma3 = float_comma(value['-SIGMA3-'])
            except:
                sg.popup('Incorrect \u03C33')
                continue
            c = DATA['value_c']
            phi = DATA['value_phi']
            p_ref = DATA['gen']['p_ref']
            m = DATA['gen']['m']
            b = DATA['gen']['b']
            ln_x = log(
                (sigma3 + c / tan(radians(phi)))
                / (p_ref + c / tan(radians(phi)))
            )
            E50 = e ** (m * ln_x + b)
            window['-E50-'].update(f"E50 = {round(E50, 2):,} [kPa]".replace(',', ' '))
    window.close()