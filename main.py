import PySimpleGUI as sg
from csv import reader
from matplotlib import pyplot
from numpy import interp, linspace
from json import dump, load, JSONDecodeError
from random import randrange
from math import tan, radians, log, cos, sin
from os import path
import os
import psutil


process = psutil.Process(os.getpid())


def float_comma(string):
    return float(string.replace(',', '.'))


def read_csv(file_name, graph_key, sigma3, R_f, color, DATA):
    # Reads csv and pastes graph_name in dic, then calls split_graph

    with open(file_name) as csvfile:
        file = reader(csvfile, delimiter=';')
        DATA['graphs_initial'][graph_key] = {
            'x': [],
            'y': [],
            'sigma3': sigma3,
            'Rf': R_f,
            'checkbox_sigma1': 1,
            'checkbox_E50': 0,
            'color': color,
            'sigma1_init': 0.0
        }

        for row in file:
            DATA['graphs_initial'][graph_key]['x'].append(float_comma(row[1]))
            DATA['graphs_initial'][graph_key]['y'].append(float_comma(row[0]))

        DATA['graphs_initial'][graph_key]['sigma1_max'] = max(DATA['graphs_initial'][graph_key]['y'])
        DATA['graphs_initial'][graph_key]['sigma1_init'] = min(DATA['graphs_initial'][graph_key]['y'])
        DATA['graphs_initial'][graph_key]['epsilon_init'] = min(DATA['graphs_initial'][graph_key]['x'])
        DATA['graphs_altered'][f"{graph_key}_1"] = {
            'x': [],
            'y': [],
            'E50': {'sigma1': 0, 'epsilon': 0},
            'E50_lab': {'sigma1': 0, 'epsilon': 0},
            'checkbox_sigma1': 1,
            'checkbox_E50': 0,
            'color': DATA['graphs_initial'][graph_key]['color'],
        }
        DATA['graphs_altered'][f"{graph_key}_2"] = {
            'x': [],
            'y': [],
            'checkbox_sigma1': 1
        }


# def reopen():
def reopen(window, layout, DATA):
    ''' Closes and opens main window '''
    # global window, layout
    loc = window.CurrentLocation()
    window.close()
    layout = update_mainlayout(DATA)
    window = sg.Window("Demo", layout=layout, location=loc, element_padding=1)
    return window, layout


def redraw_graph(DATA):
    ''' Clears pyplot window and redraws all graphs in dic '''

    axes.clear()
    for graph_key in DATA['graphs_altered']:
        if DATA['graphs_altered'][graph_key]['checkbox_sigma1'] == 1:
            # Makes graphs 'tail' gray
            if graph_key[-2:] == '_2':
                axes.plot(
                    DATA['graphs_altered'][graph_key]['x'],
                    DATA['graphs_altered'][graph_key]['y'],
                    linestyle='--',
                    color='gray'
                    )

            else:
                axes.plot(
                    DATA['graphs_altered'][graph_key]['x'],
                    DATA['graphs_altered'][graph_key]['y'],
                    marker='.',
                    color=DATA['graphs_altered'][graph_key]['color'],
                    label=f"{graph_key[:-2]} (Rf={DATA['graphs_initial'][graph_key[:-2]]['Rf']})"
                )
        if graph_key[-2:] == '_1' and DATA['graphs_altered'][graph_key]['checkbox_E50'] == 1:
            pyplot.axline(
                (0, 0),
                (
                    DATA['graphs_altered'][graph_key]['E50']['epsilon'],
                    DATA['graphs_altered'][graph_key]['E50']['sigma1']
                ),
                color=DATA['graphs_altered'][graph_key]['color'],
                linestyle='--',
                label=f"{graph_key[:-2]} E50"
            )
    for graph_key in DATA['graphs_created']:
        axes.plot(
            DATA['graphs_created'][graph_key]['1']['x'],
            DATA['graphs_created'][graph_key]['1']['y'],
            label=f"{graph_key} (q_a={round(DATA['graphs_created'][graph_key]['q_a'], 2)} [kPa])",
            linestyle='--'
        )
        axes.plot(
            DATA['graphs_created'][graph_key]['2']['x'],
            DATA['graphs_created'][graph_key]['2']['y'],
            linestyle='--',
            color='gray'
        )

    axes.set_xlabel('\u03B5')
    axes.set_ylabel('\u03C31 [kPa]')
    pyplot.axvline(0.15, linestyle='--', color='red')
    pyplot.xlim(-0.01, 0.16)
    axes.legend()
    axes.grid(True)


def plot_graph(DATA, graph_key):
    # Draws single graph from dic

    axes.clear()
    axes.plot(
        DATA['graphs_init'][graph_key]['x'],
        DATA['graphs_init'][graph_key]['y'],
        label=graph_key,
        marker='.',
        color=DATA['graphs_init'][graph_key]['color']
    )
    axes.set_xlabel('\u03B5')
    axes.set_ylabel('\u03C31 [kPa]')
    axes.legend()
    axes.grid(True)


def calculate_m(DATA):
    graph_1 = DATA['m_graphs'][0]
    graph_2 = DATA['m_graphs'][1]
    sigma3_1 = DATA['graphs_initial'][graph_1]['sigma3']
    sigma3_2 = DATA['graphs_initial'][graph_2]['sigma3']
    E50_1 = (
        DATA['graphs_altered'][f"{graph_1}_1"]['E50']['sigma1']
        / DATA['graphs_altered'][f"{graph_1}_1"]['E50']['epsilon']
    )
    E50_2 = (
        DATA['graphs_altered'][f"{graph_2}_1"]['E50']['sigma1']
        / DATA['graphs_altered'][f"{graph_2}_1"]['E50']['epsilon']
    )
    m = (
        - log(E50_2 / E50_1)
        / log(
            (
                sigma3_1 + DATA['value_c'] * 1 / tan(radians(DATA['value_phi']))
            )
            / (
                sigma3_2 + DATA['value_c'] * 1 / tan(radians(DATA['value_phi']))
            )
        )
    )
    DATA['p_ref'] = min(
        DATA['graphs_initial'][graph_1]['sigma3'],
        DATA['graphs_initial'][graph_2]['sigma3']
    )
    m = round(m, 3)
    return m


def create_column_layout(DATA):
    ''' Creates layout consisting of columns to display opened graphs
    '''
    bg_clr = '#202020'

    lst = [
        [[sg.Text('m', background_color=bg_clr)]],  # column for m_graphs
        [[sg.Text('Name', background_color=bg_clr)]], # name
        [[sg.Text('\u03C33 [kPa]', background_color=bg_clr)]], # sigma_3
        [[sg.Text('E50 [kPa]', background_color=bg_clr)]], # E50
        [[sg.Text('E50_lab [kPa]', background_color=bg_clr)]], # E50_lab
        [[sg.Text('Display \u03C31', background_color=bg_clr)]], # checkbox_sigma
        [[sg.Text('Display E50', background_color=bg_clr)]], # checkbox_E50
        [[sg.Text('Configure', background_color=bg_clr)]], # configure
    ]

    for i in DATA['graphs_initial']:
        lst[0].append(
            [sg.Text(
                cb_on if i in DATA['m_graphs'] else cb_off,
                enable_events=True,
                key=('checkbox_m', i),
                tooltip='Enabled' if i in DATA['m_graphs'] else 'Disabled',
            )]
        )
        lst[1].append(
            [sg.Text(i, background_color=bg_clr)]
        )
        lst[2].append(
            [sg.Text(DATA['graphs_initial'][i]['sigma3'], background_color=bg_clr)]
        )
        lst[3].append(
            [sg.Text(
                f"{round(DATA['graphs_altered'][str(i)+str('_1')]['E50']['sigma1']/DATA['graphs_altered'][str(i)+str('_1')]['E50']['epsilon']):,}".replace(',', ' '),
                background_color=bg_clr
            )]
        )
        lst[4].append(
            [sg.Text(
                f"{round(DATA['graphs_altered'][str(i)+str('_1')]['E50_lab']['sigma1']/DATA['graphs_altered'][str(i)+str('_1')]['E50_lab']['epsilon']):,}".replace(',', ' '),
                background_color=bg_clr
            )]
        )
        lst[5].append(
            [
                sg.Text(
                    key=('checkbox_sigma1', i),
                    enable_events=True,
                    text=(cb_on if DATA['graphs_initial'][i]['checkbox_sigma1'] else cb_off),
                    background_color=bg_clr,
                    tooltip='Enabled' if DATA['graphs_initial'][i]['checkbox_sigma1'] else 'Disabled',
                )
            ]
        )
        lst[6].append(
            [
                sg.Text(
                    key=('checkbox_E50', i),
                    enable_events=True,
                    text=(cb_on if DATA['graphs_initial'][i]['checkbox_E50'] else cb_off),
                    background_color=bg_clr,
                    tooltip='Enabled' if DATA['graphs_initial'][i]['checkbox_E50'] else 'Disabled',
                )
            ]
        )
        lst[7].append(
            [sg.Text(
                '\u2699',
                key=('configure_OG', i),
                enable_events=True,
                background_color=bg_clr,
                tooltip='Open configuration'
            )]
        )

    layout = [
        [
            sg.Column(
                i,
                element_justification='center',
                background_color=bg_clr
            ) for i in [
                lst[0],
                lst[1],
                lst[2],
                lst[3],
                lst[4],
                lst[5],
                lst[6],
                lst[7],
            ]
        ]
    ]
    return layout if len(DATA['graphs_initial']) else []


def create_custom_column_layout(DATA):
    ''' Creates column layout for custom graphs
    '''
    bg_clr = '#202020'

    lst = [
        [[sg.Text('Name', background_color=bg_clr)]],  # name
        [[sg.Text('\u03C33 [kPa]', background_color=bg_clr)]],  # sigma_3
        [[sg.Text('E50 [kPa]', background_color=bg_clr)]],  # E50
        [[sg.Text('q_f [kPa]', background_color=bg_clr)]],  # q_f
        [[sg.Text('q_a [kPa]', background_color=bg_clr)]],  # q_a
        [[sg.Text('m', background_color=bg_clr)]],  # m
        [[sg.Text('Remove', background_color=bg_clr)]],  # remove
    ]

    for i in DATA['graphs_created']:
        lst[0].append(
            [sg.Text(i, background_color=bg_clr)]
        )
        lst[1].append(
            [sg.Text(DATA['graphs_created'][i]['sigma3'], background_color=bg_clr)]
        )
        lst[2].append(
            [sg.Text(f"{round(DATA['graphs_created'][i]['E50']):,}".replace(',', ' '), background_color=bg_clr)]
        )
        lst[3].append(
            [sg.Text(f"{round(DATA['graphs_created'][i]['q_f']):,}".replace(',', ' '), background_color=bg_clr)]
        )
        lst[4].append(
            [sg.Text(f"{round(DATA['graphs_created'][i]['q_a']):,}".replace(',', ' '), background_color=bg_clr)]
        )
        lst[5].append(
            [sg.Text(DATA['graphs_created'][i]['m'], background_color=bg_clr)]
        )
        lst[6].append(
            [sg.Text(
                '\u274C',
                key=('remove', i),
                enable_events=True,
                tooltip='Remove this graph',
            )]
        )

    layout = [
        [
            sg.Column(
                i,
                element_justification='center',
                background_color=bg_clr
            ) for i in [
                lst[0],
                lst[1],
                lst[2],
                lst[3],
                lst[4],
                lst[5],
                lst[6],
            ]
        ]
    ]
    return layout if len(DATA['graphs_created']) else []


def update_mainlayout(DATA):
    ''' Updates layout of main window
    '''
    menu = [['&File', ['&Browse files', '---', '&Save', '&Load', '---', '&Exit']]]

    information_layout = [
        sg.Frame('', layout=[
            [sg.Text(
                f"p_ref={DATA['p_ref']} [kPa]",
                key='-P_REF_VALUE-'
            )],
            [sg.Text(
                f"m={DATA['m']}",
                text_color='#0e0',
                key='-M_VALUE-',
            )]
        ]),
        sg.Push(),
        sg.Text(text=f"\u03C6={DATA['value_phi']} [°]"),
        sg.Text(text=f"c={DATA['value_c']} [kPa]"),
        sg.Button('Configure', key='-c_and_phi-')
    ]

    graphs_layout_columns = create_column_layout(DATA)

    custom_graphs_layout = create_custom_column_layout(DATA)

    layout = [
        [sg.Menu(
            menu_definition=menu,
        )],
        information_layout,
        [sg.Text()],
        [sg.Frame('Opened graphs', layout=graphs_layout_columns)],
    ]

    if len(DATA['graphs_initial']) >= 2:
        layout.append([sg.Text()])
        custom_graphs_layout.append(
            [sg.Push(), sg.Button(button_text='Add')]
        )
        layout.append(
            [sg.Frame('Custom graphs', layout=custom_graphs_layout)]
        )

    return layout


def split_graph(graph_key, DATA):
    """ Splits dic_init in break point (sigma_max * Rf)
        and adds obtained graphs in dic_alt
    """

    break_y = DATA['graphs_initial'][graph_key]['sigma1_max'] * DATA['graphs_initial'][graph_key]['Rf']

    for i in range(len(DATA['graphs_initial'][graph_key]['y'])):
        # Adds sigma1 and epsilon of E50
        if (
            DATA['graphs_initial'][graph_key]['y'][i] >= break_y / 2
            and DATA['graphs_initial'][graph_key]['y'][i - 1] < break_y / 2
        ):
            DATA['graphs_altered'][f"{graph_key}_1"]['E50']['sigma1'] = break_y / 2
            DATA['graphs_altered'][f"{graph_key}_1"]['E50']['epsilon'] = (
                interp(
                    break_y / 2,
                    DATA['graphs_initial'][graph_key]['y'][i - 1:i + 1],
                    DATA['graphs_initial'][graph_key]['x'][i - 1:i + 1]
                )
                )

        # Creates break point and splits graphs
        if (
            DATA['graphs_initial'][graph_key]['y'][i] >= break_y
        ):
            DATA['graphs_altered'][f"{graph_key}_1"]['y'] = DATA['graphs_initial'][graph_key]['y'][:i]
            DATA['graphs_altered'][f"{graph_key}_1"]['y'].append(break_y)
            DATA['graphs_altered'][f"{graph_key}_1"]['y'].append(break_y)
            DATA['graphs_altered'][f"{graph_key}_1"]['x'] = DATA['graphs_initial'][graph_key]['x'][:i]
            DATA['graphs_altered'][f"{graph_key}_1"]['x'].append(
                interp(
                    break_y,
                    DATA['graphs_initial'][graph_key]['y'][i - 1:i + 1],
                    DATA['graphs_initial'][graph_key]['x'][i - 1:i + 1]
                )
                )
            DATA['graphs_altered'][f"{graph_key}_1"]['x'].append(DATA['graphs_initial'][graph_key]['x'][-1])

            DATA['graphs_altered'][f"{graph_key}_2"]['y'] = DATA['graphs_initial'][graph_key]['y'][i:]
            DATA['graphs_altered'][f"{graph_key}_2"]['y'].insert(0, break_y)
            DATA['graphs_altered'][f"{graph_key}_2"]['x'] = DATA['graphs_initial'][graph_key]['x'][i:]
            DATA['graphs_altered'][f"{graph_key}_2"]['x'].insert(0, interp(
                break_y,
                DATA['graphs_initial'][graph_key]['y'][i - 1:i + 1],
                DATA['graphs_initial'][graph_key]['x'][i - 1:i + 1]
            )
            )
            break

        for i in range(len(DATA['graphs_initial'][graph_key]['y'])):
            # Adds sigma1 and epsilon of E50_lab
            if (
                DATA['graphs_initial'][graph_key]['y'][i] >= DATA['graphs_initial'][graph_key]['sigma1_max'] / 2
            ):
                DATA['graphs_altered'][f"{graph_key}_1"]['E50_lab']['sigma1'] = DATA['graphs_initial'][graph_key]['sigma1_max'] / 2
                DATA['graphs_altered'][f"{graph_key}_1"]['E50_lab']['epsilon'] = interp(
                    DATA['graphs_initial'][graph_key]['sigma1_max'] / 2,
                    DATA['graphs_initial'][graph_key]['y'][i - 1:i + 1],
                    DATA['graphs_initial'][graph_key]['x'][i - 1:i + 1]
                )
                break


def cut_graph(graph_key, DATA, sigma1_init):
    for i in range(len(DATA['graphs_initial'][graph_key]['y'])):
        if DATA['graphs_initial'][graph_key]['y'][i] >= sigma1_init:
            epsilon_init = interp(
                sigma1_init, DATA['graphs_initial'][graph_key]['y'][i - 1:i + 1],
                DATA['graphs_initial'][graph_key]['x'][i - 1:i + 1]
                )
            break

    for i in range(len(DATA['graphs_initial'][graph_key]['y'])):
        DATA['graphs_initial'][graph_key]['y'][i] += (
            DATA['graphs_initial'][graph_key]['sigma1_init']
            - sigma1_init
        )
        DATA['graphs_initial'][graph_key]['x'][i] += (
            DATA['graphs_initial'][graph_key]['epsilon_init']
            - epsilon_init
        )

    for i in range(len(DATA['graphs_altered'][f"{graph_key}_1"]['y'])):
        DATA['graphs_altered'][f"{graph_key}_1"]['y'][i] += (
            DATA['graphs_initial'][graph_key]['sigma1_init']
            - sigma1_init
        )
        DATA['graphs_altered'][f"{graph_key}_1"]['x'][i] += (
            DATA['graphs_initial'][graph_key]['epsilon_init']
            - epsilon_init
            )

    for i in range(len(DATA['graphs_altered'][f'{graph_key}_2']['y'])):
        DATA['graphs_altered'][f"{graph_key}_2"]['y'][i] += (
            DATA['graphs_initial'][graph_key]['sigma1_init']
            - sigma1_init
        )
        DATA['graphs_altered'][f"{graph_key}_2"]['x'][i] += (
            DATA['graphs_initial'][graph_key]['epsilon_init']
            - epsilon_init
        )

    DATA['graphs_initial'][graph_key]['sigma1_max'] += (
        DATA['graphs_initial'][graph_key]['sigma1_init']
        - sigma1_init
        )
    DATA['graphs_initial'][graph_key]['sigma1_init'] = sigma1_init
    DATA['graphs_initial'][graph_key]['epsilon_init'] = epsilon_init


def browse_window(DATA):
    # Create the window
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
                    default_text=0.9,
                    key='-R_f-',
                    size=(10, 1)
                )
            ]]
        )],
        [
            sg.Column(
                [[
                    sg.Input(
                        default_text=f"#{randrange(0, 230, 1):02x}{randrange(0, 230, 1):02x}{randrange(0, 230, 1):02x}",
                        key='-color-',
                        disabled=True,
                        size=(10, 1),
                        enable_events=True,
                        text_color='#303030'
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
                break

        # Closes window when window is closed or user presses Cancel button
        if event_2 in [sg.WIN_CLOSED, 'Cancel']:
            break

    # Closes window
    browse_files.close()


def configure_window(graph_key, DATA):
    # Opens window to configure each graph

    layout = [
        [
            sg.Input(
                default_text=DATA['graphs_initial'][graph_key]['color'],
                key='-color-',
                disabled=True, size=(10, 1),
                enable_events=True,
                text_color='#303030'
            ),
            sg.ColorChooserButton(button_text='Pick color', target='-color-')
        ],

        [
            sg.Column([
                [sg.Text("\u03C33")],
                [sg.Text('\u03C31_max')],
                [sg.Text('\u03C31_initial')],
                [sg.Text('Rf')]
            ]),

            sg.Column([
                [sg.Input(
                    default_text=DATA['graphs_initial'][graph_key]['sigma3'],
                    key='-sigma3-',
                    size=(10, 1)
                )],
                [sg.Input(
                    default_text=DATA['graphs_initial'][graph_key]['sigma1_max'],
                    key='-sigma1_max-',
                    size=(10, 1)
                )],
                [sg.Input(
                    default_text=DATA['graphs_initial'][graph_key]['sigma1_init'],
                    key='-sigma1_init-',
                    size=(10, 1)
                )],
                [sg.Input(
                    default_text=DATA['graphs_initial'][graph_key]['Rf'],
                    key='-Rf-',
                    size=(10, 1)
                )]
            ]),

            sg.Column([
                [sg.Text('[kPa]')],
                [sg.Text('[kPa]')],
                [sg.Text('[kPa]')],
                [sg.Text('[-]')]
            ])
        ],

        [sg.Button('OK', bind_return_key=True), sg.Button('Cancel')]
    ]

    configure = sg.Window(
        f"Configure {graph_key}",
        layout,
        resizable=True,
        grab_anywhere=True
    )

    while True:
        event_3, values_3 = configure.read()

        if event_3 == sg.WIN_CLOSED or event_3 == 'Cancel':
            DATA['graphs_initial'][graph_key]['color'] = DATA['graphs_altered'][f"{graph_key}_1"]['color']
            break

        if event_3 == '-color-':
            DATA['graphs_initial'][graph_key]['color'] = values_3['-color-']
            plot_graph(DATA, graph_key)

        if event_3 == 'OK':
            try:
                float_comma(values_3['-sigma3-'])
                float_comma(values_3['-Rf-'])
                float_comma(values_3['-sigma1_max-'])
                float_comma(values_3['-sigma1_init-'])
            except ValueError:
                sg.popup('Invalid data type')
                continue
            if (
                float_comma(values_3['-Rf-']) <= 0
                or float_comma(values_3['-Rf-']) > 1
            ):
                sg.popup('Invalid Rf')
                continue

            elif (
                float_comma(values_3['-sigma1_max-']) <= 0
                or float_comma(values_3['-sigma1_max-'])
                > max(DATA['graphs_initial'][graph_key]['y'])
            ):
                sg.popup('Invalid \u03C31_max')
                continue

            elif (
                float_comma(values_3['-sigma1_init-'])
                > max(DATA['graphs_initial'][graph_key]['y'])
                or float_comma(values_3['-sigma1_init-'])
                < min(DATA['graphs_initial'][graph_key]['y'])
            ):
                sg.popup('Invalid \u03C31_initial')
                continue

            else:
                DATA['graphs_initial'][graph_key]['Rf'] = float_comma(values_3['-Rf-'])
                DATA['graphs_initial'][graph_key]['sigma3'] = float_comma(values_3['-sigma3-'])
                DATA['graphs_initial'][graph_key]['sigma1_max'] = float_comma(
                    values_3['-sigma1_max-']
                )
                DATA['graphs_altered'][f"{graph_key}_1"]['color'] = DATA['graphs_initial'][graph_key]['color']
                if (
                    float_comma(values_3['-sigma1_init-'])
                    != DATA['graphs_initial'][graph_key]['sigma1_init']
                ):
                    cut_graph(
                        graph_key, DATA,
                        float_comma(values_3['-sigma1_init-'])
                    )
                break

    configure.close()


def add_graph(DATA):
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
                    float_comma(values_5['-sigma3-'])
                    float_comma(values_5['-Rf-'])
                except ValueError:
                    sg.popup('Wrong data type')
                    continue
                graph_1 = list(DATA['graphs_initial'])[0]
                p_ref = DATA['graphs_initial'][graph_1]['sigma3']
                E50_ref = (
                    DATA['graphs_altered'][f"{graph_1}_1"]['E50']['sigma1']
                    / DATA['graphs_altered'][f"{graph_1}_1"]['E50']['epsilon']
                )
                sigma3 = float_comma(values_5['-sigma3-'])
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
                Rf = float_comma(values_5['-Rf-'])
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
                y_2 = [i for i in linspace(q_f, 0.99* q_a, 30)]
                x_2 = [
                    (
                        1 / E_i * i
                        / (1 - i / q_a)
                    ) for i in y_2
                ]
                # Append values to create horizontal line on graph
                y_1.append(q_f)
                x_1.append(x_2[-1])

                DATA['graphs_created'][values_5['-graph_name-']] = {
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
                    'm': DATA['m'],
                }
                break

        if event_5 == 'Cancel' or event_5 == sg.WIN_CLOSED:
            break
    add_window.close()


def configure_c_phi(DATA):
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
                break
        if event_4 in [sg.WIN_CLOSED, 'Cancel']:
            break
    configuration.close()


def save_load(w_type, DATA):
    ''' Opens window to save or load save file'''
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
            break
        if event_4 == 'Load data':
            load_file(values_4['Load'], DATA)
            break
        if event_4 in [sg.WIN_CLOSED, 'Cancel']:
            break
    save_load_window.close()


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


# Main dictionary of program
DATA = {
    'graphs_initial': {},  # Dictionary storing all initial graphs
    'graphs_altered': {},  # Dictionary storing all altered graphs
    'graphs_created': {},  # Dictionary storing all user created graphs
    'm_graphs': [],  # List with ywo names of graphs to calculate m
    'value_phi': 0.0,  # Default value if phi
    'value_c': 0.0,  # Default value of c
    'm': 0.0,  # Default value of m
    'p_ref': 0.0,  # Default value of p_ref
}

# Visuals
cb_on = '\u2611'  # Checkbox True
cb_off = '\u2610'  # Checkbox False

# Open pyplot window and draw based on dic graphs_altered
figure, axes = pyplot.subplots()
# redraw_graph(graphs_altered, graphs_created, graphs)
redraw_graph(DATA)

# Set dark theme
axes.set_facecolor('#202020')
figure.patch.set_facecolor('#202020')
axes.spines['bottom'].set_color('#DED7CF')
axes.spines['top'].set_color('#DED7CF')
axes.spines['right'].set_color('#DED7CF')
axes.spines['left'].set_color('#DED7CF')
axes.tick_params('both', colors='#DED7CF')
axes.yaxis.label.set_color('#DED7CF')
axes.xaxis.label.set_color('#DED7CF')

pyplot.ion()
pyplot.show(block=False)

# Set dark theme
sg.theme_background_color('#202020')
sg.theme_button_color(('#DED7CF', '#303030'))
sg.theme_element_background_color('#202020')
sg.theme_input_background_color('#303030')
sg.theme_input_text_color('#DED7CF')
sg.theme_text_color('#DED7CF')
sg.theme_text_element_background_color('#202020')


# Layout for main window
layout = update_mainlayout(DATA)

# Create the window
window = sg.Window("Demo", layout, element_padding=1)

memory_initial = process.memory_info().rss / 1024 ** 2

# Create an event loop
while True:
    event_1, values_1 = window.read()

    print(event_1, values_1)

    # End program if user closes window or presses the OK button
    if event_1 == "Exit" or event_1 == sg.WIN_CLOSED:
        break

    # Open plot window
    if event_1 == 'Plot':
        figure, axes = pyplot.subplots()
        # redraw_graph(graphs_altered, graphs_created, graphs)
        redraw_graph(DATA)
        axes.set_facecolor('#202020')
        figure.patch.set_facecolor('#202020')
        axes.spines['bottom'].set_color('#DED7CF')
        axes.spines['top'].set_color('#DED7CF')
        axes.spines['right'].set_color('#DED7CF')
        axes.spines['left'].set_color('#DED7CF')
        axes.tick_params('both', colors='#DED7CF')
        axes.yaxis.label.set_color('#DED7CF')
        axes.xaxis.label.set_color('#DED7CF')
        pyplot.ion()
        pyplot.show(block=False)

    # Opens graph configure (configure button is the same name as graph name)
    if event_1[0] == 'configure_OG':
        configure_window(event_1[1], DATA)
        split_graph(event_1[1], DATA)
        window, layout = reopen(window, layout, DATA)

    # Opens browse window if user presses Browse files button
    if event_1 == "Browse files":
        if DATA['value_c'] == 0 and DATA['value_phi'] == 0 and len(DATA['graphs_initial']) == 1:
            sg.popup('c and \u03C6 are not set')
            continue
        browse_window(DATA)
        window, layout = reopen(window, layout, DATA)

    # Adds/removes m from m_graphs
    if event_1[0] == 'checkbox_m':
        if window[event_1].get() == cb_on:
            values_1[event_1] = 0
            window[event_1].update(cb_off)
            window[event_1].set_tooltip('Disabled')
        else:
            values_1[event_1] = 1
            window[event_1].update(cb_on)
            window[event_1].set_tooltip('Enabled')
        
        if len(DATA['m_graphs']) == 2:
            if values_1[event_1]:
                old_graph = DATA['m_graphs'].pop(0)
                window[(event_1[0], old_graph)].update(cb_off)
                window[(event_1[0], old_graph)].set_tooltip('Disabled')
                DATA['m_graphs'].append(event_1[1])

                DATA['m'] = calculate_m(DATA)
                window['-M_VALUE-'].update(f"m={DATA['m']}")
                window['-P_REF_VALUE-'].update(f"p_ref={DATA['p_ref']} [kPa]")
            else:
                DATA['m_graphs'].remove(event_1[1])
                DATA['m'] = 0.0
                DATA['p_ref'] = 0.0
                window['-M_VALUE-'].update(f"m={DATA['m']}")
                window['-P_REF_VALUE-'].update(f"p_ref={DATA['p_ref']} [kPa]")
        else:
            if values_1[event_1]:
                DATA['m_graphs'].append(event_1[1])

                if len(DATA['m_graphs']) == 2:
                    DATA['m'] = calculate_m(DATA)
                    window['-M_VALUE-'].update(f"m={DATA['m']}")
                    window['-P_REF_VALUE-'].update(f"p_ref={DATA['p_ref']} [kPa]")
            else:
                DATA['m_graphs'].remove(event_1[1])


    # Disables/Enables graph sigma1 on checkbox
    if event_1[0] == 'checkbox_sigma1':
        if window[event_1].get() == cb_on:
            values_1[event_1] = 0
            window[event_1].update(cb_off)
            window[event_1].set_tooltip('Disabled')
        else:
            values_1[event_1] = 1
            window[event_1].update(cb_on)
            window[event_1].set_tooltip('Enabled')

        DATA['graphs_initial'][event_1[1]]['checkbox_sigma1'] = int(values_1[event_1])
        DATA['graphs_altered'][f"{event_1[1]}_1"]['checkbox_sigma1'] = int(
            values_1[event_1]
        )
        DATA['graphs_altered'][f"{event_1[1]}_2"]['checkbox_sigma1'] = int(
            values_1[event_1]
        )

    # Enables/Disables graph E50 on checkbox
    if event_1[0] == 'checkbox_E50':
        if window[event_1].get() == cb_on:
            values_1[event_1] = 0
            window[event_1].update(cb_off)
            window[event_1].set_tooltip('Disabled')
        else:
            values_1[event_1] = 1
            window[event_1].update(cb_on)
            window[event_1].set_tooltip('Enabled')

        DATA['graphs_initial'][event_1[1]]['checkbox_E50'] = int(values_1[event_1])
        DATA['graphs_altered'][f"{event_1[1]}_1"]['checkbox_E50'] = int(
            values_1[event_1]
        )

    # Opens c and phi configure window
    if event_1 == '-c_and_phi-':
        configure_c_phi(DATA)
        window, layout = reopen(window, layout, DATA)

    # Opens add window
    if event_1 == 'Add':
        if DATA['m']:
            add_graph(DATA)
            window, layout = reopen(window, layout, DATA)
        else:
            sg.popup('Select two opened graphs to calculate "m"')

    # Deletes created graph
    if event_1[0] == 'remove':
        del DATA['graphs_created'][event_1[1]]
        window, layout = reopen(window, layout, DATA)

    # Loads file
    if event_1 == 'Load':
        save_load(event_1, DATA)
        window, layout = reopen(window, layout, DATA)

    if event_1 == 'Save':
        save_load(event_1, DATA)

    # redraw_graph(graphs_altered, graphs_created, graphs)
    redraw_graph(DATA)
    if process.memory_info().rss / 1024 ** 2 - memory_initial > 100:
        sg.popup('RAM usage is high. It is recommended to restart the program')

window.close()
exit()
