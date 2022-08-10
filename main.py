import PySimpleGUI as sg
from csv import reader
from matplotlib import pyplot
from numpy import interp, linspace
from json import dump, load
from random import randrange
from math import tan, radians, log, cos, sin
from os import path

import os
import psutil
process = psutil.Process(os.getpid())

def read_csv(file_name, graph_key, sigma3, dic_init, dic_alt):
    # Reads csv and pastes graph_name in dic, then calls split_graph
    
    with open(file_name) as csvfile:
        file = reader(csvfile, delimiter=';')
        dic_init[graph_key] = {
            'x':[],
            'y':[],
            'sigma3':sigma3,
            'Rf':0.95,
            'checkbox_sigma1':1,
            'checkbox_E50':0,
            'color':f"#{randrange(0, 230, 1):02x}{randrange(0, 230, 1):02x}{randrange(0, 230, 1):02x}",
            'sigma1_init':0.0
        }
        
        for row in file:
            dic_init[graph_key]['x'].append(float(row[1].replace(',','.')))
            dic_init[graph_key]['y'].append(float(row[0].replace(',','.')))
        
        dic_init[graph_key]['sigma1_max'] = max(dic_init[graph_key]['y'])
        dic_init[graph_key]['sigma1_init'] = min(dic_init[graph_key]['y'])
        dic_init[graph_key]['epsilon_init'] = min(dic_init[graph_key]['x'])
        dic_alt[f'{graph_key}_1'] = {
            'x':[],
            'y':[],
            'E50':{'sigma1':0, 'epsilon':0},
            'checkbox_sigma1':1,
            'checkbox_E50':0,
            'color':dic_init[graph_key]['color'],
        }
        dic_alt[f'{graph_key}_2'] = {
            'x':[],
            'y':[],
            'checkbox_sigma1':1
        }

def reopen():
    # Closes and opens main window
    global window, layout
    loc = window.CurrentLocation()
    window.close()
    layout = update_mainlayout(graphs, graphs_altered, graphs_created)
    window = sg.Window("Demo", layout, location=loc, element_padding=1)

def redraw_graph(dic, dic_cr):
    # Clears pyplot window and redraws all graphs in dic
    
    axes.clear()
    for graph_key in dic:
        if dic[graph_key]['checkbox_sigma1'] == 1:
            # Makes graphs 'tail' gray
            if graph_key[-2:] == '_2':
                axes.plot(dic[graph_key]['x'], dic[graph_key]['y'], linestyle='--', color='gray')
            
            else:
                axes.plot(
                    dic[graph_key]['x'],
                    dic[graph_key]['y'],
                    marker='.',
                    color = dic[graph_key]['color'],
                    label=graph_key[:-2]
                )
        if graph_key[-2:] == '_1' and dic[graph_key]['checkbox_E50'] == 1:
            pyplot.axline(
                (0, 0),
                (
                    dic[graph_key]['E50']['epsilon'],
                    dic[graph_key]['E50']['sigma1']
                ),
                color=dic[graph_key]['color'],
                linestyle='--',
                label=f'{graph_key[:-2]} E50'
            )
    for graph_key in dic_cr:
        y = linspace(0, dic_cr[graph_key]['q_f'], 100)
        x = (1/dic_cr[graph_key]['E_i']) * y / (1-y/(dic_cr[graph_key]['q_a']))
        axes.plot(x, y, label=graph_key, linestyle='--')

    axes.set_xlabel('\u03B5')
    axes.set_ylabel('\u03C31 [kPa]')
    pyplot.axvline(0.15, linestyle='--', color='red')
    pyplot.xlim(-0.01, 0.16)
    axes.legend()
    axes.grid(True)

def plot_graph(dic, graph_key):
    # Draws single graph from dic
    
    axes.clear()
    axes.plot(
        dic['x'],
        dic['y'],
        label=graph_key,
        marker='.',
        color = dic['color']
    )
    axes.set_xlabel('\u03B5')
    axes.set_ylabel('\u03C31 [kPa]')
    axes.legend()
    axes.grid(True)

def update_mainlayout(dic, dic_alt, dic_cr):
    # Updates layout of main window
    global m
    if len(dic) >= 2:
        graph_1 = list(dic)[0]
        graph_2 = list(dic)[1]
        sigma3_1 = dic[graph_1]['sigma3']
        sigma3_2 = dic[graph_2]['sigma3']
        E50_1 = dic_alt[f'{graph_1}_1']['E50']['sigma1'] / dic_alt[f'{graph_1}_1']['E50']['epsilon']
        E50_2 = dic_alt[f'{graph_2}_1']['E50']['sigma1'] / dic_alt[f'{graph_2}_1']['E50']['epsilon']
        m = - log(E50_2/E50_1) / log((sigma3_1 + value_c * 1/tan(radians(value_phi)))/(sigma3_2 + value_c * 1/tan(radians(value_phi))))
        m = round(m, 3)
    layout =  [[
            sg.Button('Browse files'),
            sg.Button('Plot'),
            sg.Push(),
            sg.VSeparator(),
            sg.Text(text=f'\u03C6={value_phi} [°]'),
            sg.Text(text=f'c={value_c} [kPa]'),
            sg.Button('Configure', key='-c_and_phi-')
            ],
            [sg.HSeparator(), sg.Text(f'm={m}'), sg.HSeparator()],
            [[
                sg.Text(i),
                sg.Text(f"\u03C33 = {dic[i]['sigma3']} [kPa]"),
                sg.Text(f"E50 = {round(dic_alt[str(i)+str('_1')]['E50']['sigma1']/dic_alt[str(i)+str('_1')]['E50']['epsilon'], 2)} [kPa]"),
                sg.Push(),
                sg.Checkbox(key=f'{i}_checkbox_sigma1', enable_events=True, text='\u03C31', default=(dic[i]['checkbox_sigma1'])),
                sg.Checkbox(key=f'{i}_checkbox_E50', enable_events=True, text='E50', default=(dic[i]['checkbox_E50'])),
                sg.Button('Configure', key=i)
            ] for i in dic],
            [sg.VPush()],
            [sg.HSeparator()],
            [
                sg.Input(key='SaveAs', visible=False, enable_events=True),
                sg.FileSaveAs(
                    button_text='Save',
                    file_types=(('TXT files', '*.txt'),)
                    ),
                sg.Input(key='Load', visible=False, enable_events=True),
                sg.FileBrowse(
                    button_text='Load',
                    file_types=(('TXT files', '*.txt'),),
                    ),
                sg.Push(),
                sg.Button('Exit')]]
    if len(dic) > 2:
        layout[2][2].insert(2, [sg.HSeparator()])
    if len(dic) >= 2:
        layout.insert(
            4,
            [
                [sg.HSeparator()],
                [[
                    sg.Text(i),
                    sg.Text(f"\u03C33 = {dic_cr[i]['sigma3']} [kPa]"),
                    sg.Text(f"E50 = {round(dic_cr[i]['E50'])} [kPa]"),
                    sg.Push(),
                    sg.Button('Remove', key=f"{i}_remove")
                ] for i in dic_cr],
                [sg.Push(), sg.Button(button_text='Add')]
            ])
    return layout

def split_graph(graph_key, dic_init, dic_alt):
    # Splits dic_init in break point (sigma_max * Rf) and adds obtained graphs in dic_alt
    
    break_y = dic_init[graph_key]['sigma1_max'] * dic_init[graph_key]['Rf']
    
    for i in range(len(dic_init[graph_key]['y'])):
        # Adds sigma1 and epsilon of E50
        if dic_init[graph_key]['y'][i] >= break_y / 2 and dic_init[graph_key]['y'][i-1] < break_y / 2:
            dic_alt[f'{graph_key}_1']['E50']['sigma1'] = break_y / 2
            dic_alt[f'{graph_key}_1']['E50']['epsilon'] = interp(break_y/2, dic_init[graph_key]['y'][i-1:i+1], dic_init[graph_key]['x'][i-1:i+1])
        
        # Creates break point and splits graphs
        if dic_init[graph_key]['y'][i] >= break_y:
            dic_alt[f'{graph_key}_1']['y'] = dic_init[graph_key]['y'][:i]
            dic_alt[f'{graph_key}_1']['y'].append(break_y)
            dic_alt[f'{graph_key}_1']['y'].append(break_y)
            dic_alt[f'{graph_key}_1']['x'] = dic_init[graph_key]['x'][:i]
            dic_alt[f'{graph_key}_1']['x'].append(interp(break_y, dic_init[graph_key]['y'][i-1:i+1], dic_init[graph_key]['x'][i-1:i+1]))
            dic_alt[f'{graph_key}_1']['x'].append(dic_init[graph_key]['x'][-1])

            dic_alt[f'{graph_key}_2']['y'] = dic_init[graph_key]['y'][i:]
            dic_alt[f'{graph_key}_2']['y'].insert(0, break_y)
            dic_alt[f'{graph_key}_2']['x'] = dic_init[graph_key]['x'][i:]
            dic_alt[f'{graph_key}_2']['x'].insert(0, interp(break_y, dic_init[graph_key]['y'][i-1:i+1], dic_init[graph_key]['x'][i-1:i+1]))
            
            break

def cut_graph(graph_key, dic_init, dic_alt, sigma1_init):
    for i in range(len(dic_init[graph_key]['y'])):
        if dic_init[graph_key]['y'][i] >= sigma1_init:
            epsilon_init = interp(sigma1_init, dic_init[graph_key]['y'][i-1:i+1], dic_init[graph_key]['x'][i-1:i+1])
            break
    
    for i in range(len(dic_init[graph_key]['y'])):
        dic_init[graph_key]['y'][i] += dic_init[graph_key]['sigma1_init'] - sigma1_init
        dic_init[graph_key]['x'][i] += dic_init[graph_key]['epsilon_init'] - epsilon_init
    
    for i in range(len(dic_alt[f'{graph_key}_1']['y'])):
        dic_alt[f'{graph_key}_1']['y'][i] += dic_init[graph_key]['sigma1_init'] - sigma1_init
        dic_alt[f'{graph_key}_1']['x'][i] += dic_init[graph_key]['epsilon_init'] - epsilon_init
    
    for i in range(len(dic_alt[f'{graph_key}_2']['y'])):
        dic_alt[f'{graph_key}_2']['y'][i] += dic_init[graph_key]['sigma1_init'] - sigma1_init
        dic_alt[f'{graph_key}_2']['x'][i] += dic_init[graph_key]['epsilon_init'] - epsilon_init

    dic_init[graph_key]['sigma1_max'] += dic_init[graph_key]['sigma1_init'] - sigma1_init
    dic_init[graph_key]['sigma1_init'] = sigma1_init
    dic_init[graph_key]['epsilon_init'] = epsilon_init

def browse_window():
    # Create the window
    browse_files = sg.Window(
        'Browse files',
        layout=[
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
            [sg.Button('OK', bind_return_key=True), sg.Button('Cancel')]
            ])
    
    # Create event loop
    while True:
        event_2, values_2 = browse_files.read()
        print(event_2)
        # When user presses OK button
        if event_2 == 'OK':
            # Checks path
            if (
                values_2['-file-'] == '' or
                not path.exists(values_2['-file-'])
            ):
                sg.popup('Wrong path')
                continue
            
            # Checks graph name
            elif (
                values_2['-graphname-'] in ['Browse files', 'Exit', 'Update', 'SaveAs', 'Load'] or
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
                    float(values_2['-sigma3-'])
                except:
                    sg.popup('Wrong \u03C33')
                    continue
                read_csv(values_2['-file-'], values_2['-graphname-'], float(values_2['-sigma3-']), graphs, graphs_altered)
                split_graph(values_2['-graphname-'], graphs, graphs_altered)
                break
        
        # Closes window when window is closed or user presses Cancel button
        if event_2 in [sg.WIN_CLOSED, 'Cancel']:
            break
    
    # Closes window
    browse_files.close()

def configure_window(graph_key, dic, dic_alt):
    # Opens window to configure each graph
    
    layout = [
        [
            sg.Input(default_text=dic[graph_key]['color'], key='-color-', disabled=True, size=(10, 1), enable_events=True, text_color='#303030'),
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
                [sg.Input(default_text=dic[graph_key]['sigma3'], key='-sigma3-', size=(10, 1))],
                [sg.Input(default_text=dic[graph_key]['sigma1_max'], key='-sigma1_max-', size=(10, 1))],
                [sg.Input(default_text=dic[graph_key]['sigma1_init'], key='-sigma1_init-', size=(10, 1))],
                [sg.Input(default_text=dic[graph_key]['Rf'], key='-Rf-', size=(10, 1))]
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
    
    configure = sg.Window(f'Configure {graph_key}', layout, resizable=True, grab_anywhere=True)
    plot_graph(dic[graph_key], graph_key)
    
    while True:
        event_3, values_3 = configure.read()
        
        if event_3 == sg.WIN_CLOSED or event_3 == 'Cancel':
            dic[graph_key]['color'] = dic_alt[f'{graph_key}_1']['color']
            break
        
        if event_3 == '-color-':
            dic[graph_key]['color'] = values_3['-color-']
            plot_graph(dic[graph_key], graph_key)

        if event_3 == 'OK':
            try:
                float(values_3['-sigma3-'])
                float(values_3['-Rf-'])
                float(values_3['-sigma1_max-'])
                float(values_3['-sigma1_init-'])
            except:
                sg.popup('Invalid data type')
                continue
            if (
                float(values_3['-Rf-']) <= 0 or
                float(values_3['-Rf-']) > 1
            ):
                sg.popup('Invalid Rf')
                continue
            
            elif (
                float(values_3['-sigma1_max-']) <= 0 or
                float(values_3['-sigma1_max-']) > max(dic[graph_key]['y'])
            ):
                sg.popup('Invalid \u03C31_max')
                continue
            
            elif (
                float(values_3['-sigma1_init-']) > max(dic[graph_key]['y']) or
                float(values_3['-sigma1_init-']) < min(dic[graph_key]['y'])
            ):
                sg.popup('Invalid \u03C31_initial')
                continue

            else:
                dic[graph_key]['Rf'] = float(values_3['-Rf-'])
                dic[graph_key]['sigma3'] = float(values_3['-sigma3-'])
                dic[graph_key]['sigma1_max'] = float(values_3['-sigma1_max-'])
                dic_alt[f'{graph_key}_1']['color'] = dic[graph_key]['color']
                if float(values_3['-sigma1_init-']) != dic[graph_key]['sigma1_init']:
                    cut_graph(graph_key, dic, dic_alt, float(values_3['-sigma1_init-']))
                break
    
    configure.close()

def add_graph(dic_cr, dic_alt, dic_init):
    layout = [
        [sg.HSeparator(), sg.Text(f'm = {m}'), sg.HSeparator()],
        [sg.Text('Graph name'), sg.Push(), sg.Input(size=(15, 1), key='-graph_name-')],
        [sg.Text('\u03C33 [kPa]'), sg.Push(), sg.Input(size=(15, 1), key='-sigma3-')],
        [sg.Text('Rf'), sg.Push(), sg.Input(size=(15, 1), key='-Rf-')],
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
                    float(values_5['-sigma3-'])
                    float(values_5['-Rf-'])
                except:
                    sg.popup('Wrong data type')
                    continue
                graph_1 = list(dic_init)[0]
                p_ref = dic_init[graph_1]['sigma3']
                E50_ref = dic_alt[f'{graph_1}_1']['E50']['sigma1'] / dic_alt[f'{graph_1}_1']['E50']['epsilon']
                sigma3 = float(values_5['-sigma3-'])
                E50 = E50_ref * (
                    ( value_c * cos(radians(value_phi)) + sigma3 * sin(radians(value_phi)) ) / ( value_c * cos(radians(value_phi)) + p_ref * sin(radians(value_phi)) )
                ) ** m
                Rf = float(values_5['-Rf-'])
                q_f = ( value_c / tan(radians(value_phi)) + sigma3 ) * 2 * sin(radians(value_phi)) / ( 1 - sin(radians(value_phi)) )
                q_a = q_f / Rf
                E_i = 2 * E50 / ( 2 - Rf )
                dic_cr[values_5['-graph_name-']] = {
                    'Rf':Rf,
                    'sigma3':sigma3,
                    'E50':E50,
                    'q_f':q_f,
                    'q_a':q_a,
                    'E_i':E_i
                }
                break
        
        if event_5 == 'Cancel' or event_5 == sg.WIN_CLOSED():
            break
    add_window.close()

def configure_c_phi():
    global value_phi, value_c
    layout = [
        [
            sg.Column([
                [sg.Text('\u03C6')],
                [sg.Text('c')]
            ]),
            sg.Column([
                [sg.Input(default_text=value_phi, key='-phi-', size=(5, 1))],
                [sg.Input(default_text=value_c, key='-c-', size=(5, 1))]
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
                    float(values_4['-phi-'])
                    float(values_4['-c-'])
                except:
                    sg.popup('Wrong \u03C6 or c')
                    continue
                value_phi = float(values_4['-phi-'])
                value_c = float(values_4['-c-'])
                break
        if event_4 in [sg.WIN_CLOSED, 'Cancel']:
            break
    configuration.close()

def save_file(file_name):
    # Saves all data in save file
    s_f = {'graphs':graphs, 'graphs_altered':graphs_altered, 'value_phi': value_phi, 'value_c':value_c, 'm':m, 'graphs_created':graphs_created}
    with open(file_name, 'w') as file:
        dump(s_f, file, indent = 4)

def load_file(file_name):
    # Loads provided save file and inputs data in graphs and graphs_altered
    with open(file_name) as load_file:
        data = load(load_file)
        global graphs, graphs_altered, value_phi, value_c, m, graphs_created
        graphs = data['graphs']
        graphs_altered = data['graphs_altered']
        value_phi = data['value_phi']
        value_c = data['value_c']
        m = data['m']
        graphs_created = data['graphs_created']


# Dic storing all initial graphs
graphs = {}

# Dic storing altered initial graphs
graphs_altered = {}

# Dic storing all user created graphs
graphs_created = {}

# Structure of dictionaries can be seen in save files

# Values set by default, will be changed by user
value_phi = 0.0
value_c = 0.0
m = 0.0

# Open pyplot window and draw based on dic graphs_altered
figure, axes = pyplot.subplots()
redraw_graph(graphs_altered, graphs_created)
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

# Set default theme
sg.theme_background_color('#202020')
sg.theme_button_color(('#DED7CF', '#303030'))
sg.theme_element_background_color('#202020')
sg.theme_input_background_color('#303030')
sg.theme_input_text_color('#DED7CF')
sg.theme_text_color('#DED7CF')
sg.theme_text_element_background_color('#202020')

# Layout for main window
layout = update_mainlayout(graphs, graphs_altered, graphs_created)

# Create the window
window = sg.Window("Demo", layout, element_padding=1)

memory_initial = process.memory_info().rss/1024 ** 2

# Create an event loop
while True:
    event_1, values_1 = window.read()
    
    # End program if user closes window or presses the OK button
    if event_1 == "Exit" or event_1 == sg.WIN_CLOSED:
        break
    
    # Open plot window
    if event_1 == 'Plot':
        figure, axes = pyplot.subplots()
        redraw_graph(graphs_altered, graphs_created)
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
    if event_1 in graphs:
        configure_window(event_1, graphs, graphs_altered)
        split_graph(event_1, graphs, graphs_altered)
        reopen()

    # Opens browse window if user presses Browse files button
    if event_1 == "Browse files":
        if value_c == 0 and value_phi == 0 and len(graphs) == 1:
            sg.popup('c and \u03C6 are not set')
            continue
        browse_window()
        reopen()

    # Disables graph sigma1 on checkbox
    if event_1[-16:] == '_checkbox_sigma1':
        graphs[event_1[:-16]]['checkbox_sigma1'] = int(values_1[event_1])
        graphs_altered[f'{event_1[:-16]}_1']['checkbox_sigma1'] = int(values_1[event_1])
        graphs_altered[f'{event_1[:-16]}_2']['checkbox_sigma1'] = int(values_1[event_1])

    # Disables graph E50 on checkbox
    if event_1[-13:] == '_checkbox_E50':
        graphs[event_1[:-13]]['checkbox_E50'] = int(values_1[event_1])
        graphs_altered[f'{event_1[:-13]}_1']['checkbox_E50'] = int(values_1[event_1])

    # Opens c and phi configure window
    if event_1 == '-c_and_phi-':
        configure_c_phi()
        reopen()

    # Opens add window
    if event_1 == 'Add':
        add_graph(graphs_created, graphs_altered, graphs)
        reopen()
    
    # Deletes created graph
    if event_1[-7:] == '_remove':
        del graphs_created[event_1[:-7]]
        reopen()

    # Saves file
    if event_1 == 'SaveAs':
        save_file(values_1['SaveAs'])
    
    # Loads file
    if event_1 == 'Load':
        load_file(values_1['Load'])
        reopen()

    redraw_graph(graphs_altered, graphs_created)
    if process.memory_info().rss/1024 ** 2 - memory_initial > 100:
        sg.popup('RAM usage is high. It is recommended to restart the program')

window.close()