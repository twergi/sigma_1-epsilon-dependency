from math import tan, radians, cos, sin
from random import randrange
from numpy import linspace
import PySimpleGUI as sg
from modules.utils import float_comma
from typing import Tuple, List


def add_graph(DATA):
    ''' Opens create custom graph window
        and adds custom graphs to DATA
    '''

    changes = False

    layout = [
        [sg.HSeparator(), sg.Text(f"m = {DATA['m']}"), sg.HSeparator()],
        [
            sg.Text('Graph name'),
            sg.Push(),
            sg.Input(size=(15, 1), key='-graph_name-')
        ],
        [
            sg.Text('\u03C33 [kPa]'),
            sg.Push(),
            sg.Input(size=(15, 1), key='-sigma3-')
        ],
        [sg.Text('Rf'), sg.Push(), sg.Input(size=(15, 1), default_text=0.9, key='-Rf-')],
        [sg.Button('Add', bind_return_key=True), sg.Button('Cancel')]
    ]
    add_window = sg.Window('Add', layout)
    while True:
        event_5, values_5 = add_window.read()
        if event_5 == 'Add':
            if values_5['-graph_name-'] == '':
                sg.popup('Enter graph name')
                continue
            elif values_5['-sigma3-'] == '':
                sg.popup('Invalid \u03C33')
                continue
            elif values_5['-Rf-'] == '':
                sg.popup('Enter Rf')
                continue
            else:
                try:
                    sigma3 = float_comma(values_5['-sigma3-'])
                    Rf = float_comma(values_5['-Rf-'])
                except ValueError:
                    sg.popup('Wrong data type')
                    continue
                x_1, y_1, x_2, y_2, E50, E_i, q_f, q_a, p_ref = calculateGraphCR(DATA, Rf, sigma3)
                graph_name = values_5['-graph_name-']
                DATA['graphs_created'][graph_name] = {
                    '1': {
                        'x': x_1,
                        'y': y_1
                    },
                    '2': {
                        'x': x_2,
                        'y': y_2
                    },
                    'Rf': Rf,
                    'sigma3': sigma3,
                    'E50': E50,
                    'q_f': q_f,
                    'q_a': q_a,
                    'E_i': E_i,
                    'p_ref': p_ref,
                    'm': DATA['m'],
                    'checkbox_E50': False,
                    'color': f"#{randrange(40, 230, 1):02x}{randrange(40, 230, 1):02x}{randrange(40, 230, 1):02x}"
                }
                changes = True
                break

        if event_5 == 'Cancel' or event_5 == sg.WIN_CLOSED:
            break
    add_window.close()
    return changes

def calculateGraphCR(DATA, Rf, sigma3, p_ref=None) -> Tuple[List[float], List[float], List[float], List[float], float, float, float, float]:
    m_graphs_keys = DATA['m_graphs']
    graph_1 = min(
        m_graphs_keys,
        key=lambda graph: DATA['graphs_initial'][graph]['sigma3']
    )
    if not p_ref:
        p_ref = DATA['graphs_initial'][graph_1]['sigma3']
    E50_ref = (
        DATA['graphs_altered'][f"{graph_1}_1"]['E50']['sigma1']
        / DATA['graphs_altered'][f"{graph_1}_1"]['E50']['epsilon']
    )
    E50 = (
        E50_ref
        * (
            (
                DATA['value_c'] * cos(radians(DATA['value_phi']))
                + sigma3 * sin(radians(DATA['value_phi']))
            )
            / (
                DATA['value_c'] * cos(radians(DATA['value_phi']))
                + p_ref * sin(radians(DATA['value_phi']))
            )
        )
        ** DATA['m']
    )
    q_f = (
        (
            DATA['value_c'] / tan(radians(DATA['value_phi'])) + sigma3
        )
        * 2 * sin(radians(DATA['value_phi']))
        / (1 - sin(radians(DATA['value_phi'])))
    )
    q_a = q_f / Rf
    E_i = 2 * E50 / (2 - Rf)

    # y_1 and x_1 for first (colored) part of graph
    y_1 = [i for i in linspace(0, q_f, 100)]
    x_1 = [
        (
            1 / E_i * i
            / (1 - i / q_a)
        ) for i in y_1
    ]

    # y_2 and x_2 for second (gray) part of graph
    y_2 = [i for i in linspace(q_f, 0.99 * q_a, 30)]
    x_2 = [
        (
            1 / E_i * i
            / (1 - i / q_a)
        ) for i in y_2
    ]
    # Append values to create horizontal line on graph
    y_1.append(q_f)
    x_1.append(x_2[-1])

    return (x_1, y_1, x_2, y_2, E50, E_i, q_f, q_a, p_ref)