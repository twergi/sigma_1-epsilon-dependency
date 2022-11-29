import PySimpleGUI as sg
from modules.utils import float_comma, cut_graph
from modules.add_graph_window import calculateGraphCR


def plot_graph(DATA, graph_key, axes):
    ''' Draws single graph from dic
    '''

    axes.clear()
    axes.plot(
        DATA['graphs_initial'][graph_key]['x'],
        DATA['graphs_initial'][graph_key]['y'],
        label=graph_key,
        marker='.',
        color=DATA['graphs_initial'][graph_key]['color']
    )
    axes.set_xlabel('\u03B5')
    axes.set_ylabel('\u03C31 [kPa]')
    axes.legend()
    axes.grid(True)


def configure_window(graph_key, DATA, axes, btnColor):
    ''' Opens window to configure each graph
    '''

    changes = False

    # Create layout for the window
    layout = [
        [
            sg.Input(
                default_text=DATA['graphs_initial'][graph_key]['color'],
                key='-color-',
                disabled=True,
                size=(10, 1),
                enable_events=True,
                disabled_readonly_background_color=btnColor
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
            plot_graph(DATA, graph_key, axes)

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
                changes = True
                break

    configure.close()
    return changes

def configure_cr_window(graph_key, DATA, btnColor):
    ''' Configure window for created graphs
    '''

    changes = False

    layout = [
        [
            sg.Input(
                default_text=DATA['graphs_created'][graph_key]['color'],
                key='-color-',
                disabled=True,
                size=(10, 1),
                enable_events=True,
                disabled_readonly_background_color=btnColor
            ),
            sg.ColorChooserButton(button_text='Pick color', target='-color-')
        ],

        [
            sg.Column([
                [sg.Text("\u03C33")],
                [sg.Text('Rf')]
            ]),

            sg.Column([
                [sg.Input(
                    default_text=DATA['graphs_created'][graph_key]['sigma3'],
                    key='-sigma3-',
                    size=(10, 1)
                )],
                [sg.Input(
                    default_text=DATA['graphs_created'][graph_key]['Rf'],
                    key='-Rf-',
                    size=(10, 1)
                )]
            ]),

            sg.Column([
                [sg.Text('[kPa]')],
                [sg.Text('[-]')]
            ])
        ],

        [sg.Button('OK', bind_return_key=True), sg.Button('Cancel')]
    ]
    configure = sg.Window(
        f"Configure {graph_key}",
        layout
    )

    while True:
        event_3, values_3 = configure.read()

        if event_3 == sg.WIN_CLOSED or event_3 == 'Cancel':
            break

        if event_3 == '-color-':
            DATA['graphs_created'][graph_key]['color'] = values_3['-color-']

        if event_3 == 'OK':
            try:
                new_sigma3 = float_comma(values_3['-sigma3-'])
                new_Rf = float_comma(values_3['-Rf-'])
            except ValueError:
                sg.popup('Invalid data type')
                continue
            if (
                float_comma(values_3['-Rf-']) <= 0
                or float_comma(values_3['-Rf-']) > 1
            ):
                sg.popup('Invalid Rf')
                continue

            else:
                if (
                    DATA['graphs_created'][graph_key]['Rf'] != new_Rf
                    or DATA['graphs_created'][graph_key]['sigma3'] != new_sigma3
                ):
                    DATA['graphs_created'][graph_key]['Rf'] = new_Rf
                    DATA['graphs_created'][graph_key]['sigma3'] = new_sigma3
                    p_ref = DATA['graphs_created'][graph_key]['p_ref']
                    x_1, y_1, x_2, y_2, E50, E_i, q_f, q_a, p_ref = calculateGraphCR(DATA, new_Rf, new_sigma3, p_ref)
                    DATA['graphs_created'][graph_key]['1']['x'] = x_1
                    DATA['graphs_created'][graph_key]['1']['y'] = y_1
                    DATA['graphs_created'][graph_key]['2']['x'] = x_2
                    DATA['graphs_created'][graph_key]['2']['y'] = y_2
                    DATA['graphs_created'][graph_key]['E50'] = E50
                    DATA['graphs_created'][graph_key]['E_i'] = E_i
                    DATA['graphs_created'][graph_key]['q_f'] = q_f
                    DATA['graphs_created'][graph_key]['q_a'] = q_a
                changes = True
                break

    configure.close()
    return changes