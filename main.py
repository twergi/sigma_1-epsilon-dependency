import PySimpleGUI as sg
from matplotlib import pyplot
import os
import psutil
from utils import calculate_m, split_graph
from browse_window import browse_window
from add_graph_window import add_graph
from configure_c_and_phi_window import configure_c_phi
from save_load import save_load
from configure_graph_window import configure_window

process = psutil.Process(os.getpid())


def reopen(window, layout, DATA):
    ''' Closes and opens main window '''

    location = window.CurrentLocation()
    window.close()
    layout = create_mainlayout(DATA)
    window = sg.Window("Demo", layout=layout, location=location, element_padding=1)
    return window, layout


def redraw_graph(DATA, axes):
    ''' Clears pyplot window and redraws all graphs in DATA '''

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
            label=f"{graph_key} (q_a={round(DATA['graphs_created'][graph_key]['q_a'])} [kPa])",
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


def create_mainlayout(DATA):
    ''' Creates layout of main window
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

    graphs_layout_columns = create_column_layout(DATA, bgColor)

    custom_graphs_layout = create_custom_column_layout(DATA, bgColor)

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


def axes_set_theme(axes, figure, bgColor, txtColor):
    ''' Sets dark colors for plot window
    '''
    axes.set_facecolor(bgColor)
    figure.patch.set_facecolor(bgColor)
    axes.spines['bottom'].set_color(txtColor)
    axes.spines['top'].set_color(txtColor)
    axes.spines['right'].set_color(txtColor)
    axes.spines['left'].set_color(txtColor)
    axes.tick_params('both', colors=txtColor)
    axes.yaxis.label.set_color(txtColor)
    axes.xaxis.label.set_color(txtColor)


def set_sg_theme(theme: str):
    ''' Returns colors for windows elements
        depending on passed color theme
    '''
    if theme == 'dark':
        bgColor = '#202020'
        btnColor = '#303030'
        txtColor = '#DED7CF'
    elif theme == 'light':
        bgColor = '#DFDFDF'
        btnColor = '#CFCFCF'
        txtColor = '#212830'
    return bgColor, btnColor, txtColor


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
}

# Open pyplot window and draw based on dic graphs_altered
figure, axes = pyplot.subplots()

# Set pyplot theme
axes_set_theme(axes, figure, bgColor, txtColor)

pyplot.ion()
pyplot.show(block=False)
redraw_graph(DATA, axes)

# Set PySimpleGUI theme
sg.theme_background_color(bgColor)
sg.theme_button_color((txtColor, btnColor))
sg.theme_element_background_color(bgColor)
sg.theme_input_background_color(btnColor)
sg.theme_input_text_color(txtColor)
sg.theme_text_color(txtColor)
sg.theme_text_element_background_color(bgColor)

# Layout for main window
layout = create_mainlayout(DATA)

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

    # Opens graph configure (configure button is the same name as graph name)
    if event_1[0] == 'configure_OG':
        configure_window(event_1[1], DATA, axes, btnColor)
        split_graph(event_1[1], DATA)
        window, layout = reopen(window, layout, DATA)

    # Opens browse window if user presses Browse files button
    if event_1 == "Browse files":
        if DATA['value_c'] == 0 and DATA['value_phi'] == 0 and len(DATA['graphs_initial']) == 1:
            sg.popup('c and \u03C6 are not set')
            continue
        browse_window(DATA, btnColor)
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

    redraw_graph(DATA, axes)
    if process.memory_info().rss / 1024 ** 2 - memory_initial > 100:
        sg.popup('RAM usage is high. It is recommended to restart the program')

window.close()
