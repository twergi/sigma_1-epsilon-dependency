from csv import reader
from math import tan, log, radians
from numpy import interp


def float_comma(string):
    ''' Returns float from string number with comma '''
    return float(string.replace(',', '.'))


def read_csv(file_name, graph_key, sigma3, R_f, color, DATA):
    ''' Reads csv and pastes graph_name in dic, then calls split_graph
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
