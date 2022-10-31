from csv import reader
from math import tan, log, radians
from numpy import interp
from os import listdir
from os.path import join, isfile
from matplotlib import pyplot


def float_comma(string):
    ''' Returns float from string number with comma '''
    return float(string.replace(',', '.'))


def read_csv(file_name, graph_key, sigma3, R_f, color, DATA):
    ''' Reads csv and pastes graph_name in DATA['graphs_initial']
        and DATA['graphs_altered']
    '''

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


def read_folder(path, DATA):
    ''' Opens folder and adds all csv files
        to DATA['gen']['graphs']
    '''

    folder_content = listdir(path)
    # Clear list in case of reopening
    DATA['gen']['graphs'] = []

    # Cycle through every element in folder
    for element in folder_content:
        full_path = join(path, element)

        # Check if it is file with .csv extension
        if (
            isfile(full_path)
            and element[-4:] == '.csv'
        ):
            with open(full_path) as csvfile:
                file = reader(csvfile, delimiter=';')
                DATA['gen']['graphs'].append({
                    'x': [],
                    'y': [],
                    'sigma3': 0,
                    'E50': 0,
                    'filename': element,
                })

                for i, row in enumerate(file):
                    DATA['gen']['graphs'][-1]['x'].append(float_comma(row[1]))
                    DATA['gen']['graphs'][-1]['y'].append(float_comma(row[0]))
                    if i == 0:
                        sigma3 = float_comma(row[2])
                        DATA['gen']['graphs'][-1]['sigma3'] = sigma3
                        if (
                            DATA['gen']['p_ref'] == 0
                            or sigma3 < DATA['gen']['p_ref']
                        ):
                            DATA['gen']['p_ref'] = sigma3


def calculate_m(DATA):
    ''' Calculates m from graphs in DATA['m_graphs']
    '''
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


def calculate_gen_E50(DATA):
    ''' Calculates E50 for every graph in
        DATA gen graphs
    '''
    R_f = DATA['R_f']
    for i in range(len(DATA['gen']['graphs'])):
        y_list = DATA['gen']['graphs'][i]['y']
        x_list = DATA['gen']['graphs'][i]['x']
        max_sigma = max(y_list)
        sigma50 = max_sigma * R_f / 2
        for k in range(len(y_list)):
            if y_list[k] >= sigma50:
                epsilon50 = interp(
                    sigma50,
                    y_list[k - 1:k + 1],
                    x_list[k - 1:k + 1]
                )
                DATA['gen']['graphs'][i]['E50'] = sigma50 / epsilon50
                break


def calculate_ln_data(DATA):
    graphs_list = DATA['gen']['graphs']
    c = DATA['value_c']
    phi = DATA['value_phi']
    p_ref = DATA['gen']['p_ref']

    DATA['gen']['ln_data']['y'] = []
    DATA['gen']['ln_data']['x'] = []

    for i in range(len(graphs_list)):
        sigma3 = graphs_list[i]['sigma3']

        DATA['gen']['ln_data']['y'].append(
            log(graphs_list[i]['E50']))
        DATA['gen']['ln_data']['x'].append(
            log(
                (sigma3 + c / tan(radians(phi)))
                / (p_ref + c / tan(radians(phi)))
            )
        )

    x_list = DATA['gen']['ln_data']['x']
    y_list = DATA['gen']['ln_data']['y']
    n = len(x_list)
    sum_dif_xX2 = 0
    sum_dif_yY2 = 0
    sum_dif_xXyY = 0
    x_avg = sum(x_list) / n
    y_avg = sum(y_list) / n
    for k in range(n):
        dif_xX = x_list[k] - x_avg
        dif_yY = y_list[k] - y_avg
        sum_dif_xX2 += dif_xX ** 2
        sum_dif_yY2 += dif_yY ** 2
        sum_dif_xXyY += dif_xX * dif_yY
    DATA['gen']['m'] = sum_dif_xXyY / sum_dif_xX2
    DATA['gen']['R'] = sum_dif_xXyY / (sum_dif_xX2 * sum_dif_yY2) ** 0.5
    DATA['gen']['b'] = y_avg - DATA['gen']['m'] * x_avg


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
    ''' Cuts beginning of graphs by sigma1_init
    '''
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


def redraw_graph(DATA, axes, figure):
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
            axes.axline(
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
    axes.axvline(0.15, linestyle='--', color='red')
    axes.set_xlim(-0.01, 0.16)
    axes.legend()
    axes.grid(True)


def set_axes_theme(axes, figure, bgColor, txtColor):
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


def trendline(DATA, bgColor, txtColor):
    figure1, axes1 = pyplot.subplots()
    axes1.plot(
        DATA['gen']['ln_data']['x'],
        DATA['gen']['ln_data']['y'],
        'o'
    )
    x1 = min(DATA['gen']['ln_data']['x'])
    x2 = max(DATA['gen']['ln_data']['x'])
    m = DATA['gen']['m']
    b = DATA['gen']['b']
    axes1.plot(
        [
            x1,
            x2
        ],
        [
            x1 * m + b,
            x2 * m + b
        ],
        label=f"y={round(m, 3)}*x+{round(b, 3)}"
    )
    axes1.legend()
    axes1.grid(True)
    set_axes_theme(axes1, figure1, bgColor, txtColor)
