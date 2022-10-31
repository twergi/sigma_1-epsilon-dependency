import PySimpleGUI as sg
from matplotlib import pyplot
import os
import psutil
from utils import (
    calculate_m,
    split_graph,
    read_folder,
    calculate_gen_E50,
    calculate_ln_data,
    redraw_graph,
    set_axes_theme,
    set_sg_theme,
    trendline
)
from browse_window import browse_window
from add_graph_window import add_graph
from configure_c_and_phi_window import configure_c_phi
from save_load import save_load
from configure_graph_window import configure_window

process = psutil.Process(os.getpid())


def reopen(window, layout, DATA, bgColor):
    ''' Closes and opens main window '''

    location = window.CurrentLocation()
    window.close()
    layout = create_tabs(DATA, bgColor, btnColor, txtColor)
    window = sg.Window(
        "Demo",
        layout=layout, 
        location=location,
        element_padding=1
    )
    return window, layout


def create_column_layout(DATA, bgColor):
    ''' Creates layout consisting of columns to display opened graphs
    '''

    lst = [
        [[sg.Text('m', background_color=bgColor)]],  # column for m_graphs
        [[sg.Text('Name', background_color=bgColor)]],  # name
        [[sg.Text('\u03C33 [kPa]', background_color=bgColor)]],  # sigma_3
        [[sg.Text('E50 [kPa]', background_color=bgColor)]],  # E50
        [[sg.Text('E50_lab [kPa]', background_color=bgColor)]],  # E50_lab
        [[sg.Text('Display \u03C31', background_color=bgColor)]],  # checkbox_sigma
        [[sg.Text('Display E50', background_color=bgColor)]],  # checkbox_E50
        [[sg.Text('Configure', background_color=bgColor)]],  # configure
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
            [sg.Text(i, background_color=bgColor)]
        )
        lst[2].append(
            [sg.Text(DATA['graphs_initial'][i]['sigma3'], background_color=bgColor)]
        )
        lst[3].append(
            [sg.Text(
                f"{round(DATA['graphs_altered'][str(i)+str('_1')]['E50']['sigma1']/DATA['graphs_altered'][str(i)+str('_1')]['E50']['epsilon']):,}".replace(',', ' '),
                background_color=bgColor
            )]
        )
        lst[4].append(
            [sg.Text(
                f"{round(DATA['graphs_altered'][str(i)+str('_1')]['E50_lab']['sigma1']/DATA['graphs_altered'][str(i)+str('_1')]['E50_lab']['epsilon']):,}".replace(',', ' '),
                background_color=bgColor
            )]
        )
        lst[5].append(
            [
                sg.Text(
                    key=('checkbox_sigma1', i),
                    enable_events=True,
                    text=(cb_on if DATA['graphs_initial'][i]['checkbox_sigma1'] else cb_off),
                    background_color=bgColor,
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
                    background_color=bgColor,
                    tooltip='Enabled' if DATA['graphs_initial'][i]['checkbox_E50'] else 'Disabled',
                )
            ]
        )
        lst[7].append(
            [sg.Text(
                '\u2699',
                key=('configure_OG', i),
                enable_events=True,
                background_color=bgColor,
                tooltip='Open configuration'
            )]
        )

    layout = [
        [
            sg.Column(
                i,
                element_justification='center',
                background_color=bgColor
            ) for i in lst
        ]
    ]
    return layout if len(DATA['graphs_initial']) else []


def create_custom_column_layout(DATA, bgColor):
    ''' Creates column layout for custom graphs
    '''

    lst = [
        [[sg.Text('Name', background_color=bgColor)]],  # name
        [[sg.Text('\u03C33 [kPa]', background_color=bgColor)]],  # sigma_3
        [[sg.Text('E50 [kPa]', background_color=bgColor)]],  # E50
        [[sg.Text('q_f [kPa]', background_color=bgColor)]],  # q_f
        [[sg.Text('q_a [kPa]', background_color=bgColor)]],  # q_a
        [[sg.Text('m', background_color=bgColor)]],  # m
        [[sg.Text('Remove', background_color=bgColor)]],  # remove
    ]

    for i in DATA['graphs_created']:
        lst[0].append(
            [sg.Text(i, background_color=bgColor)]
        )
        lst[1].append(
            [sg.Text(DATA['graphs_created'][i]['sigma3'], background_color=bgColor)]
        )
        lst[2].append(
            [sg.Text(f"{round(DATA['graphs_created'][i]['E50']):,}".replace(',', ' '), background_color=bgColor)]
        )
        lst[3].append(
            [sg.Text(f"{round(DATA['graphs_created'][i]['q_f']):,}".replace(',', ' '), background_color=bgColor)]
        )
        lst[4].append(
            [sg.Text(f"{round(DATA['graphs_created'][i]['q_a']):,}".replace(',', ' '), background_color=bgColor)]
        )
        lst[5].append(
            [sg.Text(DATA['graphs_created'][i]['m'], background_color=bgColor)]
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
                background_color=bgColor
            ) for i in lst
        ]
    ]
    return layout if len(DATA['graphs_created']) else []


def create_mainlayout(DATA, bgColor):
    ''' Creates layout of main window
    '''
    menu = [
        [
            '&File',
            [
                'Browse f&iles',
                'Browse f&older',
                '---',
                '&Save',
                '&Load',
                '---',
                '&Exit'
            ]
        ]
    ]

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
        sg.Button('Configure', key=('-c_and_phi-', 'main'))
    ]

    graphs_layout_columns = create_column_layout(DATA, bgColor)

    custom_graphs_layout = create_custom_column_layout(DATA, bgColor)

    layout = [
        [sg.Menu(
            menu_definition=menu,
        )],
        information_layout,
        [sg.Text()],
        [sg.Frame('Opened graphs', layout=graphs_layout_columns, expand_y=True)],
    ]

    if len(DATA['graphs_initial']) >= 2:
        layout.append([sg.Text()])
        custom_graphs_layout.append(
            [sg.Push(), sg.Button(button_text='Add')]
        )
        layout.append(
            [sg.Frame('Custom graphs', layout=custom_graphs_layout, expand_x=True)]
        )

    return layout


def create_gen_table(DATA, bgColor):
    ''' Creates layout of columns to look like table
    '''

    lst = [
        [[sg.Text('Index', background_color=bgColor)]],  # index
        [[sg.Text('\u03C33 [kPa]', background_color=bgColor)]],  # sigma_3
        [[sg.Text('E50 [kPa]', background_color=bgColor)]],  # E50
    ]
    graphs_len = len(DATA['gen']['graphs'])
    for i in range(graphs_len):
        lst[0].append(
            [sg.Text(
                i + 1,
                background_color=bgColor,
                tooltip=DATA['gen']['graphs'][i]['filename'],
            )]
        )
        lst[1].append(
            [sg.Text(
                DATA['gen']['graphs'][i]['sigma3'],
                background_color=bgColor,
            )]
        )
        lst[2].append(
            [sg.Text(
                f"{round(DATA['gen']['graphs'][i]['E50']):,}".replace(',', ' '),
                background_color=bgColor
            )]
        )

    layout = [[sg.Column(
        [
            [
                sg.Column(
                    i,
                    element_justification='center',
                    background_color=bgColor
                ) for i in lst
            ]
        ],
        scrollable=True if graphs_len >= 15 else False,
        vertical_scroll_only=True,
        expand_x=True,
        expand_y=True
    )]]
    return layout if len(DATA['gen']['graphs']) > 0 else []


def create_gen_layout(DATA, bgColor):
    ''' Creates layout for generalization tab
        of main window
    '''

    information_layout = [
        sg.Frame('', layout=[
            [sg.Text(
                f"p_ref={DATA['gen']['p_ref']} [kPa]",
            )],
            [sg.Text(
                f"y={round(DATA['gen']['m'], 3)}*x+{round(DATA['gen']['b'], 3)}",
                text_color='#0e0',
            )],
            [sg.Text(
                f"R\u00b2 = {round(DATA['gen']['R'] ** 2, 3)}"
            )]
        ]),
        sg.Push(),
        sg.Column([
            [
                sg.Text(text=f"\u03C6={DATA['value_phi']} [°]"),
                sg.Text(text=f"c={DATA['value_c']} [kPa]"),
                sg.Button('Configure', key=('-c_and_phi-', 'gen'))
            ],
            [sg.Push(), sg.Button('Show trendline', key='-TRENDLINE-')],
        ]),
    ]

    graphs_layout = create_gen_table(DATA, bgColor)

    layout = [
        information_layout,
        [sg.Text()],
        [sg.Frame(
            'Graphs in folder',
            layout=graphs_layout,
            expand_x=True,
            expand_y=True
        )],
    ]

    return layout


def create_tabs(DATA, bgColor, btnColor, txtColor):
    ''' Creates tabs layout for window
    '''

    tab_group = [
        [sg.TabGroup(
            [
                [sg.Tab('Main', create_mainlayout(DATA, bgColor))],
                [sg.Tab('Generalization', create_gen_layout(DATA, bgColor))]
            ],
            tab_background_color=bgColor,
            selected_background_color=btnColor,
            title_color=txtColor,
            border_width=0,
            tab_border_width=0,
        )]
    ]
    return tab_group


# Visuals
cb_on = '\u2611'  # Checkbox True
cb_off = '\u2610'  # Checkbox False
bgColor, btnColor, txtColor = set_sg_theme('dark')  # Sets colors for windows elements


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
    'gen': {
        'graphs': [],  # List for all graphs
        'ln_data': {
            'x': [],
            'y': []
        },
        'm': 0.0,  # Default value of m of trendline
        'p_ref': 0.0,  # Default value of p_ref
        'b': 0.0,  # Default value of b of trendline
        'R': 0.0,  # Default value of coefficient of correlation
        'R_f': 0.9,  # Default value of R_f
    }
}

# Open pyplot window and draw based on dic graphs_altered
pyplot.ion()
figure, axes = pyplot.subplots()
figure.canvas.mpl_connect('close_event', exit)
figure.show()

# Set pyplot theme
set_axes_theme(axes, figure, bgColor, txtColor)


redraw_graph(DATA, axes, figure)

# Set PySimpleGUI theme
sg.theme_background_color(bgColor)
sg.theme_button_color((txtColor, btnColor))
sg.theme_element_background_color(bgColor)
sg.theme_input_background_color(btnColor)
sg.theme_input_text_color(txtColor)
sg.theme_text_color(txtColor)
sg.theme_text_element_background_color(bgColor)

# Layout for main window
# layout = create_mainlayout(DATA, bgColor)
layout = create_tabs(DATA, bgColor, btnColor, txtColor)

# Create the window
window = sg.Window("Demo", layout, element_padding=1)

memory_initial = process.memory_info().rss / 1024 ** 2

# Create an event loop
while True:
    event_1, values_1 = window.read()

    print('event:', event_1)
    print('values:', values_1)

    # End program if user closes window or presses the OK button
    if event_1 == "Exit" or event_1 == sg.WIN_CLOSED:
        break

    # Opens graph configure (configure button is the same name as graph name)
    if event_1[0] == 'configure_OG':
        if configure_window(event_1[1], DATA, axes, btnColor):
            split_graph(event_1[1], DATA)
            redraw_graph(DATA, axes, figure)
            window, layout = reopen(window, layout, DATA, bgColor)

    # Opens browse window for files
    if event_1 == "Browse files":
        if browse_window(DATA, btnColor):
            if (
                DATA['value_c'] != 0
                and DATA['value_phi'] != 0
                and DATA['gen']['graphs'] != []
            ):
                calculate_ln_data(DATA)
            redraw_graph(DATA, axes, figure)
            window, layout = reopen(window, layout, DATA, bgColor)

    # Opens browse window for folder
    if event_1 == 'Browse folder':
        browse_folder = sg.popup_get_folder(
            message='Choose folder containing csv files',
            title='Browse folder',
            no_window=True
        )
        if browse_folder:
            read_folder(
                browse_folder,
                DATA
            )
            calculate_gen_E50(DATA)
            if DATA['value_phi'] != 0 and DATA['value_c'] != 0:
                calculate_ln_data(DATA)
            window, layout = reopen(window, layout, DATA, bgColor)

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
        redraw_graph(DATA, axes, figure)

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
        redraw_graph(DATA, axes, figure)

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
        redraw_graph(DATA, axes, figure)

    # Opens c and phi configure window
    if event_1[0] == '-c_and_phi-':
        if configure_c_phi(DATA):
            if (
                len(DATA['m_graphs']) == 2
                and DATA['value_c'] != 0
                and DATA['value_phi'] != 0
            ):
                DATA['m'] = calculate_m(DATA)

            if (
                DATA['value_c'] != 0
                and DATA['value_phi'] != 0
                and DATA['gen']['graphs'] != []
            ):
                calculate_ln_data(DATA)
            redraw_graph(DATA, axes, figure)
            window, layout = reopen(window, layout, DATA, bgColor)

    # Plots trendline
    if event_1 == '-TRENDLINE-':
        if (
            DATA['value_c'] == 0
            and DATA['value_phi'] == 0
        ):
            sg.popup('C and \u03C6 are not set')
            continue
        elif DATA['gen']['ln_data']['x'] == []:
            sg.popup('Add graphs with "File>Browse folder"')
            continue
        else:
            trendline(DATA, bgColor, txtColor)

    # Opens add window
    if event_1 == 'Add':
        if DATA['m']:
            if add_graph(DATA):
                window, layout = reopen(window, layout, DATA, bgColor)
                redraw_graph(DATA, axes, figure)
        else:
            sg.popup('Select two opened graphs to calculate "m"')

    # Deletes created graph
    if event_1[0] == 'remove':
        del DATA['graphs_created'][event_1[1]]
        window, layout = reopen(window, layout, DATA, bgColor)
        redraw_graph(DATA, axes, figure)

    # Loads file
    if event_1 == 'Load':
        if save_load(event_1, DATA):
            window, layout = reopen(window, layout, DATA, bgColor)
            redraw_graph(DATA, axes, figure)

    if event_1 == 'Save':
        save_load(event_1, DATA)

    if process.memory_info().rss / 1024 ** 2 - memory_initial > 100:
        sg.popup('RAM usage is high. It is recommended to restart the program')

window.close()
