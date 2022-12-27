# %%
import enum
import math
from copy import deepcopy
import random
import matplotlib.pyplot as plt
import numpy as np


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def draw_board():
    # create a figure to draw the board
    fig = plt.figure(figsize=[9, 9])
    # set the background color
    fig.patch.set_facecolor((0.85, 0.64, 0.125))
    ax = fig.add_subplot(111)
    # turn off the axes
    ax.set_axis_off()
    return fig, ax


def draw_grids(ax):
    # draw the vertical lines
    for x in range(16):
        ax.plot([x, x], [0, 15], 'k')
    # draw the horizontal lines
    for y in range(16):
        ax.plot([0, 15], [y, y], 'k')

    ax.set_position([0, 0, 1, 1])


def draw_coordinates(ax, x, y):
    ax.text(x + 0.1, y + 0.1, str(14 - y) + "," + str(x), fontsize=9)


def draw_pawn(ax, x, y, color):
    x = x + 0.5
    y = y + 0.5
    markeredgecolor = (0, 0, 0) if color == "noir" else (1, 1, 1)
    markerfacecolor = 'k' if color == "noir" else 'w'
    ax.plot(x, y, 'o', markersize=20,
            markeredgecolor=markeredgecolor,
            markerfacecolor=markerfacecolor,
            markeredgewidth=1)


def render_board(p):
    fig, ax = draw_board()

    for i in range(15):
        for j in range(15):
            draw_coordinates(ax, i, j)
            if p[i][j] == "blanc":
                draw_pawn(ax, j, 14 - i, "blanc")
            elif p[i][j] == "noir":
                draw_pawn(ax, j, 14 - i, "noir")

    draw_grids(ax)
    plt.show()


def get_all_pawns_of_color(p, color):
    pawns = []
    for i in range(15):
        for j in range(15):
            if p[i][j] == color:
                pawns.append([i, j])
    return pawns


def remove_duplicates_groups(groups):
    '''
    Remove a group if it's part of another group
    '''
    # print(groups)
    new_groups = []
    for group in groups:
        subset = False
        for child_group in groups:
            if set(group).issubset(set(child_group)) and group != child_group:
                subset = True
                break
        if not subset:
            new_groups.append(group)
    return new_groups


def find_grouped_aligned_pawns_combinations(p, color):
    '''
    Find all the combinations of aligned pawns of a given color
    It can be horizontal, vertical or diagonal
    '''
    group = []
    for (i, j) in get_all_pawns_of_color(p, color):
        combinations_v = []
        # We check up to 5 pawns in a row
        # Vertical
        is_something = False
        for k in range(1, 6):
            if i + k < 15:
                if p[i + k][j] == color:
                    is_something = True
                    combinations_v.append((i + k, j))
                else:
                    break
        if is_something:
            combinations_v.insert(0, (i, j))
        combinations_h = []
        # Horizontal
        is_something = False
        for k in range(1, 6):
            if j + k < 15:
                if p[i][j + k] == color:
                    is_something = True
                    combinations_h.append((i, j + k))
                else:
                    break
        if is_something:
            combinations_h.insert(0, (i, j))
        combinations_d1 = []
        # Diagonal
        is_something = False
        for k in range(1, 6):
            if i + k < 15 and j + k < 15:
                if p[i + k][j + k] == color:
                    is_something = True
                    combinations_d1.append((i + k, j + k))
                else:
                    break
        if is_something:
            combinations_d1.insert(0, (i, j))
        combinations_d2 = []
        # Diagonal
        is_something = False
        for k in range(1, 6):
            if i - k >= 0 and j + k < 15:
                if p[i - k][j + k] == color:
                    is_something = True
                    combinations_d2.append((i - k, j + k))
                else:
                    break
        if is_something:
            combinations_d2.insert(0, (i, j))

        if combinations_h:
            group.append(combinations_h)
        if combinations_v:
            group.append(combinations_v)
        if combinations_d1:
            group.append(combinations_d1)
        if combinations_d2:
            group.append(combinations_d2)

    group = remove_duplicates_groups(group)
    return group


def gravity_center(p, color):
    gapc = get_all_pawns_of_color(p, color)
    x = [points[0] for points in gapc]
    y = [points[1] for points in gapc]
    return [int(sum(x) / len(gapc)), int(sum(y) / len(gapc))]


def possible_moves(p, position, margin):
    '''
    Find all the possible move of a pawn around a given position
    '''
    moves = []
    for i in range(position[0] - margin, position[0] + margin + 1):
        for j in range(position[1] - margin, position[1] + margin + 1):
            if i >= 0 and i < 15 and j >= 0 and j < 15:
                if p[i][j] == "vide":
                    moves.append([i, j])
    return moves


def closest_empty_positions(p, from_position):
    '''
    Find the closest empty position to a given position
    '''
    positions = []
    for margin in range(15):
        moves = possible_moves(p, from_position, margin)
        for move in moves:
            if p[move[0]][move[1]] == "vide":
                positions.append(move)
        if positions:
            break
    print("closest empty positions", positions)
    return positions


def minmax(position, depth, alpha, beta, maximizingPlayer, maximazingPlayerColor, p):
    print(position)
    # deep copy of the board
    p_copy = deepcopy(p)
    if depth == 0:
        pf = find_grouped_aligned_pawns_combinations(
            p_copy, maximazingPlayerColor)
        print("pf", pf)
        return len(max(pf, key=len)) if pf else 0

    if maximizingPlayer:
        p_copy[position[0]][position[1]] = maximazingPlayerColor
        best_score = -math.inf
        for move in possible_moves(p_copy, position, 2):
            score = minmax(move, depth - 1, alpha, beta,
                           False, maximazingPlayerColor, p_copy)
            best_score = max(best_score, score)
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break
        return best_score
    else:
        p_copy[position[0]][position[1]
                            ] = "noir" if maximazingPlayerColor == "blanc" else "blanc"
        best_score = math.inf
        for move in possible_moves(p_copy, position, 2):
            score = minmax(move, depth - 1, alpha, beta,
                           True, maximazingPlayerColor, p_copy)
            best_score = min(best_score, score)
            beta = min(beta, best_score)
            if beta <= alpha:
                break
        return best_score


def is_threat_ok(position, p):
    agir = False
    print("Doit on neutralise cette menace", position)
    if position[0] < 0 or position[1] < 0:
        agir = False
    elif p[position[0]][position[1]] == "vide":
        agir = True
    print("résultat ", agir)
    return agir


def find_threats(groupAdv, pointsAdv, p):
    print("Recherche de menace")
    print("à partir des groupes de pions :", groupAdv)

    solo_pawns = [[x] for x in pointsAdv]
    combined = groupAdv + solo_pawns
    threat = []
    for index, ligne in enumerate(combined):
        # 3 tuples
        if len(ligne) == 3:
            # horizontal colonnes qui changent
            if ligne[0][0] == ligne[1][0] and ligne[0][0] == ligne[2][0]:
                agirpositionDroit = (ligne[0][0], ligne[2][1]+1)
                agirDroit = is_threat_ok(agirpositionDroit, p)
                agirpositionGauche = (ligne[0][0], ligne[0][1]-1)
                agirGauche = is_threat_ok(agirpositionGauche, p)
                if agirDroit:
                    threat.append((*agirpositionDroit, len(ligne) + 1))
                    threat.append
                if agirGauche:
                    threat.append((*agirpositionGauche, len(ligne) + 1))
            # vertical points qui changent
            elif ligne[0][1] == ligne[1][1] and ligne[0][1] == ligne[2][1]:
                agirpositionHaut = (ligne[2][0]+1, ligne[0][1])
                agirHaut = is_threat_ok(agirpositionHaut, p)
                agirpositionBas = (ligne[0][0]-1, ligne[0][1])
                agirBas = is_threat_ok(agirpositionBas, p)
                if agirHaut:
                    threat.append((*agirpositionHaut, len(ligne) + 1))
                if agirBas:
                    threat.append((*agirpositionBas, len(ligne) + 1))
             # diagonale
            else:
                if ligne[0][0]+1 == ligne[1][0]:
                    agirpositionDiagBas = (ligne[2][0]+1, ligne[2][1]+1)
                    agirDiagBas = is_threat_ok(agirpositionDiagBas, p)
                    agirpositionDiagHaut = (ligne[0][0]-1, ligne[0][1]-1)
                    agirDiagHaut = is_threat_ok(agirpositionDiagHaut, p)
                    if agirDiagBas:
                        threat.append((*agirpositionDiagBas, len(ligne) + 1))
                    if agirDiagHaut:
                        threat.append((*agirpositionDiagHaut, len(ligne) + 1))
                else:
                    agirpositionDiagBas = (ligne[0][0]+1, ligne[0][1]-1)
                    agirDiagBas = is_threat_ok(agirpositionDiagBas, p)
                    agirpositionDiagHaut = (ligne[2][0]-1, ligne[2][1]+1)
                    agirDiagHaut = is_threat_ok(agirpositionDiagHaut, p)
                    if agirDiagBas:
                        threat.append((*agirpositionDiagBas, len(ligne) + 1))
                    if agirDiagHaut:
                        threat.append((*agirpositionDiagHaut, len(ligne) + 1))
        if len(ligne) == 4:
            # horizontal colonnes qui changent
            if ligne[0][0] == ligne[1][0] and ligne[0][0] == ligne[2][0] and ligne[0][0] == ligne[3][0]:
                agirpositionDroit = (ligne[0][0], ligne[3][1]+1)
                agirDroit = is_threat_ok(agirpositionDroit, p)
                agirpositionGauche = (ligne[0][0], ligne[0][1]-1)
                agirGauche = is_threat_ok(agirpositionGauche, p)
                if agirDroit:
                    threat.append((*agirpositionDroit, len(ligne) + 1))
                if agirGauche:
                    threat.append((*agirpositionGauche, len(ligne) + 1))
            # vertical points qui changent
            elif ligne[0][1] == ligne[1][1] and ligne[0][1] == ligne[2][1] and ligne[0][1] == ligne[3][1]:
                agirpositionHaut = (ligne[3][0]+1, ligne[0][1])
                agirHaut = is_threat_ok(agirpositionHaut, p)
                agirpositionBas = (ligne[0][0]-1, ligne[0][1])
                agirBas = is_threat_ok(agirpositionBas, p)
                if agirHaut:
                    threat.append((*agirpositionHaut, len(ligne) + 1))
                if agirBas:
                    threat.append((*agirpositionBas, len(ligne) + 1))
             # diagonale
            else:
                if ligne[0][0]+1 == ligne[1][0]:
                    agirpositionDiagBas = (ligne[3][0]+1, ligne[3][1]+1)
                    agirDiagBas = is_threat_ok(agirpositionDiagBas, p)
                    agirpositionDiagHaut = (ligne[0][0]-1, ligne[0][1]-1)
                    agirDiagHaut = is_threat_ok(agirpositionDiagHaut, p)
                    if agirDiagBas:
                        threat.append((*agirpositionDiagBas, len(ligne) + 1))
                    if agirDiagHaut:
                        threat.append((*agirpositionDiagHaut, len(ligne) + 1))
                else:
                    agirpositionDiagBas = (ligne[0][0]+1, ligne[0][1]-1)
                    agirDiagBas = is_threat_ok(agirpositionDiagBas, p)
                    agirpositionDiagHaut = (ligne[3][0]-1, ligne[3][1]+1)
                    agirDiagHaut = is_threat_ok(agirpositionDiagHaut, p)
                    if agirDiagBas:
                        threat.append((*agirpositionDiagBas, len(ligne) + 1))
                    if agirDiagHaut:
                        threat.append((*agirpositionDiagHaut, len(ligne) + 1))
        if len(ligne) == 2:
            # horizontal colonnes qui changent
            if ligne[0][0] == ligne[1][0]:
                agirpositionDroit = (ligne[0][0], ligne[1][1]+1)
                agirDroit = is_threat_ok(agirpositionDroit, p)
                agirpositionGauche = (ligne[0][0], ligne[0][1]-1)
                agirGauche = is_threat_ok(agirpositionGauche, p)
                if agirDroit:
                    threat.append((*agirpositionDroit, len(ligne) + 1))
                if agirGauche:
                    threat.append((*agirpositionGauche, len(ligne) + 1))
            # vertical points qui changent
            elif ligne[0][1] == ligne[1][1]:
                agirpositionHaut = (ligne[1][0]+1, ligne[0][1])
                agirHaut = is_threat_ok(agirpositionHaut, p)
                agirpositionBas = (ligne[0][0]-1, ligne[0][1])
                agirBas = is_threat_ok(agirpositionBas, p)
                if agirHaut:
                    threat.append((*agirpositionHaut, len(ligne) + 1))
                if agirBas:
                    threat.append((*agirpositionBas, len(ligne) + 1))
                # diagonale
                else:
                    if ligne[0][0]+1 == ligne[1][0]:
                        agirpositionDiagBas = (ligne[1][0]+1, ligne[1][1]+1)
                        agirDiagBas = is_threat_ok(agirpositionDiagBas, p)
                        agirpositionDiagHaut = (ligne[0][0]-1, ligne[0][1]-1)
                        agirDiagHaut = is_threat_ok(
                            agirpositionDiagHaut, p)
                        if agirDiagBas:
                            threat.append(
                                (*agirpositionDiagBas, len(ligne) + 1))
                        if agirDiagHaut:
                            threat.append(
                                (*agirpositionDiagHaut, len(ligne) + 1))
                    else:
                        agirpositionDiagBas = (ligne[0][0]+1, ligne[0][1]-1)
                        agirDiagBas = is_threat_ok(agirpositionDiagBas, p)
                        agirpositionDiagHaut = (ligne[1][0]-1, ligne[1][1]+1)
                        agirDiagHaut = is_threat_ok(
                            agirpositionDiagHaut, p)
                        if agirDiagBas:
                            threat.append(
                                (*agirpositionDiagBas, len(ligne) + 1))
                        if agirDiagHaut:
                            threat.append(
                                (*agirpositionDiagHaut, len(ligne) + 1))
        #
        # Can we create a threat by adding a point between two points
        #
        for index2, ligne2 in enumerate(combined):
            # Are the two lignes on the same line
            if ligne[0][0] == ligne2[0][0]:
                # Are they separated by only one point
                if ligne[0][1] == ligne2[0][1] + 2:
                    print("Menace entre deux lignes (1)")
                    agirposition = (ligne[0][0], ligne[0][1]-1)
                    agir = is_threat_ok(agirposition, p)
                    if agir:
                        # Count the number of points on the same line connected by the threat
                        pawn_count = 1
                        for i, point in enumerate(ligne):
                            if i < len(ligne2):
                                if point[0] == ligne2[i][0]:
                                    pawn_count += 1
                        for i, point in enumerate(ligne2):
                            if i < len(ligne):
                                if point[0] == ligne[i][0]:
                                    pawn_count += 1
                        threat.append(
                            (*agirposition, pawn_count))
                elif ligne[0][1] == ligne2[0][1] - 2:
                    print("Menace entre deux lignes (2)")
                    agirposition = (ligne[0][0], ligne[0][1]+1)
                    agir = is_threat_ok(agirposition, p)
                    if agir:
                        # Count the number of points on the same line connected by the threat
                        pawn_count = 1
                        for i, point in enumerate(ligne):
                            if i < len(ligne2):
                                if point[0] == ligne2[i][0]:
                                    pawn_count += 1
                        for i, point in enumerate(ligne2):
                            if i < len(ligne):
                                if point[0] == ligne[i][0]:
                                    pawn_count += 1
                        threat.append(
                            (*agirposition, pawn_count))
            # Are the two lignes on the same column
            elif ligne[0][1] == ligne2[0][1]:
                # Are they separated by only one point
                if ligne[0][0] == ligne2[0][0] + 2:
                    print("Menace entre deux lignes (3)")
                    agirposition = (ligne[0][0]-1, ligne[0][1])
                    agir = is_threat_ok(agirposition, p)
                    if agir:
                        # Count the number of points on the same line connected by the threat
                        pawn_count = 1
                        for i, point in enumerate(ligne):
                            if i < len(ligne2):
                                if point[0] == ligne2[i][0]:
                                    pawn_count += 1
                        for i, point in enumerate(ligne2):
                            if i < len(ligne):
                                if point[0] == ligne[i][0]:
                                    pawn_count += 1
                        threat.append(
                            (*agirposition, pawn_count))
                elif ligne[0][0] == ligne2[0][0] - 2:
                    print("Menace entre deux lignes (4)")
                    agirposition = (ligne[0][0]+1, ligne[0][1])
                    agir = is_threat_ok(agirposition, p)
                    if agir:
                        # Count the number of points on the same line connected by the threat
                        pawn_count = 1
                        for i, point in enumerate(ligne):
                            if i < len(ligne2):
                                if point[0] == ligne2[i][0]:
                                    pawn_count += 1
                        for i, point in enumerate(ligne2):
                            if i < len(ligne):
                                if point[0] == ligne[i][0]:
                                    pawn_count += 1
                        threat.append(
                            (*agirposition, pawn_count))
            # Are the two lignes on the same diagonal
            elif ligne[0][0] == ligne2[0][0] + 2 and ligne[0][1] == ligne2[0][1] + 2:
                print("Menace entre deux lignes (5)")
                agirposition = (ligne[0][0]-1, ligne[0][1]-1)
                agir = is_threat_ok(agirposition, p)
                if agir:
                    # Count the number of points on the same diagonal connected by the threat
                    pawn_count = 2
                    for i, point in enumerate(ligne):
                        if i < len(ligne2):
                            if abs(point[0] - point[1]) == abs(ligne2[i][0] - ligne2[i][1]):
                                pawn_count += 1
                    for i, point in enumerate(ligne2):
                        if i < len(ligne):
                            if abs(point[0] - point[1]) == abs(ligne[i][0] - ligne[i][1]):
                                pawn_count += 1
                    threat.append(
                        (*agirposition, pawn_count))
            elif ligne[0][0] == ligne2[0][0] - 2 and ligne[0][1] == ligne2[0][1] - 2:
                print("Menace entre deux lignes (6)")
                agirposition = (ligne[0][0]+1, ligne[0][1]+1)
                agir = is_threat_ok(agirposition, p)
                if agir:
                    # Count the number of points on the same diagonal connected by the threat
                    pawn_count = 2
                    for i, point in enumerate(ligne):
                        if i < len(ligne2):
                            if abs(point[0] - point[1]) == abs(ligne2[i][0] - ligne2[i][1]):
                                pawn_count += 1
                    for i, point in enumerate(ligne2):
                        if i < len(ligne):
                            if abs(point[0] - point[1]) == abs(ligne[i][0] - ligne[i][1]):
                                pawn_count += 1
                    threat.append(
                        (*agirposition, pawn_count))
            elif ligne[0][0] == ligne2[0][0] - 2 and ligne[0][1] == ligne2[0][1] + 2:
                print("Menace entre deux lignes (7)")
                agirposition = (ligne[0][0]+1, ligne[0][1]-1)
                agir = is_threat_ok(agirposition, p)
                if agir:
                    # Count the number of points on the same diagonal connected by the threat
                    pawn_count = 2
                    for i, point in enumerate(ligne):
                        if i < len(ligne2):
                            if abs(point[0] + point[1]) == abs(ligne2[i][0] + ligne2[i][1]):
                                pawn_count += 1
                    for i, point in enumerate(ligne2):
                        if i < len(ligne):
                            if abs(point[0] + point[1]) == abs(ligne[i][0] + ligne[i][1]):
                                pawn_count += 1
                    threat.append(
                        (*agirposition, pawn_count))
            elif ligne[0][0] == ligne2[0][0] + 2 and ligne[0][1] == ligne2[0][1] - 2:
                print("Menace entre deux lignes (8)")
                agirposition = (ligne[0][0]-1, ligne[0][1]+1)
                agir = is_threat_ok(agirposition, p)
                if agir:
                    # Count the number of points on the same line diagonal by the threat
                    pawn_count = 2
                    for i, point in enumerate(ligne):
                        if i < len(ligne2):
                            if abs(point[0] + point[1]) == abs(ligne2[i][0] + ligne2[i][1]):
                                pawn_count += 1
                    for i, point in enumerate(ligne2):
                        if i < len(ligne):
                            if abs(point[0] + point[1]) == abs(ligne[i][0] + ligne[i][1]):
                                pawn_count += 1
                    threat.append(
                        (*agirposition, pawn_count))

    # Sort threat by the value of the 3rd element of the inner list
    threat.sort(key=lambda x: x[2], reverse=True)
    # Remove duplicates
    threat = list(dict.fromkeys(threat))
    print("Threats : ", threat)
    return threat

# %%


def __main__():
    notre_couleur = input("Couleur de notre pion : ")
    plateau = [["vide" for _ in range(15)] for _ in range(15)]

    au_tour_de = "noir"

    #plateau[0][0] = "noir"
    #plateau[0][1] = "noir"
    #plateau[0][2] = "noir"
    #plateau[0][3] = "noir"
    #plateau[0][5] = "noir"
    #plateau[0][6] = "noir"
    #plateau[1][6] = "noir"
    #plateau[2][6] = "noir"
    #plateau[2][7] = "noir"

    render_board(plateau)
    #print(find_grouped_aligned_pawns_combinations(plateau, "noir"))

    terminer = False
    history = []
    history_adv = []
    if (notre_couleur == "noir"):
        # On place notre pion au centre
        plateau[7][7] = "noir"
        au_tour_de = "blanc"
        history.append((7, 7))
    while(not terminer):
        render_board(plateau)
        if au_tour_de != notre_couleur:
            position_adv_y = input("Choix de l'adversaire en vertical : ")
            position_adv_x = input(
                "Choix de l'adversaire en horizontal : ")
            plateau[int(position_adv_y)][int(position_adv_x)] = au_tour_de
            au_tour_de = "noir" if au_tour_de == "blanc" else "blanc"
            history_adv.append((int(position_adv_y), int(position_adv_x)))
        else:
            best_position = [None, None]

            n_group_pions_adv = find_grouped_aligned_pawns_combinations(
                plateau, "blanc" if notre_couleur == "noir" else "noir")
            n_group_pions_notre = find_grouped_aligned_pawns_combinations(
                plateau, notre_couleur)

            n_pions_adv = get_all_pawns_of_color(
                plateau, "noir" if notre_couleur == "blanc" else "blanc")
            n_pions_adv_tuple = [tuple(x) for x in n_pions_adv]

            n_pions_notre = get_all_pawns_of_color(plateau, notre_couleur)
            n_pions_notre_tuple = [tuple(x) for x in n_pions_notre]

            # Si on est au 2 premier tours et qu'on commence en deuxieme
            # TOUJOURS PLACER LORS DU DEUXIEME TOUR UN PIONS QUI N'EST PAS
            # AUTOUR D'UN CARRE 7x7 AUTOUR DU CENTRE
            # placer les pionts de notre couleur autour de l'énnemi
            if len(history) < 2 and notre_couleur == "noir":
                print("Placement initial")
                available_range_ligne = [0, 1, 2, 3, 4, 11, 12, 13, 14]
                available_range_colonne = [0, 1, 2, 3, 4, 11, 12, 13, 14]
                # Select random combination
                position_ok = False
                while not position_ok:
                    random_ligne = random.choice(available_range_ligne)
                    random_colonne = random.choice(available_range_colonne)
                    if (plateau[random_ligne][random_colonne] == "vide"):
                        best_position = (random_ligne, random_colonne)
                        position_ok = True
            else:
                # On regarde si on peut créer une menace
                # TODO
                # On regarde si on doit absolument défendre SI NOTRE MENACE EST PLUS GRANDE QUE LA DEFENSE
                # ATTAQUER
                our_thread = find_threats(
                    n_group_pions_notre, n_pions_notre_tuple, plateau)
                # TODO: NE NOUS DONNE PAS LES THREADS LES PLUS IMPORTANTES CAR C QUE DES TUPLES DE COORDONNEES
                threads = find_threats(
                    n_group_pions_adv, n_pions_adv_tuple, plateau)

                # Si notre menace est plus grande que la menace adverse
                if ((len(our_thread) > 0 and len(threads) > 0 and our_thread[0][2] > threads[0][2]) or (len(our_thread) > 0 and len(threads) == 0)):
                    print("On attaque")
                    # On attaque
                    best_position = our_thread[0][0:2]
                # Si on a pas de menace plus élévée mais que la menace adverse n'est pas très élevée (< 2 pions alignés)
                elif (len(threads) > 0 and threads[0][2] <= 2):
                    print("On cherche une attaque")
                    best_score = -math.inf
                    # On essaye de trouver une attaque
                    if len(n_pions_notre) > 0:
                        search_point = history[-1]
                    else:
                        search_point = tuple(gravity_center(
                            plateau, "noir" if notre_couleur == "blanc" else "blanc"))

                    for position in closest_empty_positions(plateau, search_point):
                        score = minmax(position, 4, -math.inf,
                                       math.inf, True, notre_couleur, plateau)
                        if score > best_score:
                            best_score = score
                            best_position = position
                            if score == 5:
                                break

                # Si une menace >= 3 est trouvée on la défend en plaçant un pion
                elif (len(threads) > 0 and threads[0][2] >= 3):
                    print("On neutralise la menace")
                    best_position = threads[0][0:2]
                # Sinon on défend en utilisant le minmax à partir du dernier coup joué par l'adversaire
                else:
                    print("On défend")
                    best_score = +math.inf
                    # On essaye de trouver une attaque
                    if len(n_group_pions_adv) > 0:
                        search_point = history_adv[-1]
                    else:
                        search_point = tuple(gravity_center(
                            plateau, "noir" if notre_couleur == "blanc" else "blanc"))

                    for position in closest_empty_positions(plateau, search_point):
                        score = minmax(position, 4, -math.inf,
                                       math.inf, False, notre_couleur, plateau)
                        if score < best_score:
                            best_score = score
                            best_position = position
                            if score == 5:
                                break

            plateau[best_position[0]][best_position[1]] = notre_couleur
            history.append(best_position)
            au_tour_de = "noir" if au_tour_de == "blanc" else "blanc"


# %%
__main__()

# %%
# %%