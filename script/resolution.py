#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import numpy as np
from copy import copy
import threading as th


class Resolution(th.Thread):
    """
    Classe permettant de résoudre un sudoku grâce à différentes méthodes, à savoir :
        - inclusion
        - exclusion
        - bactracking
        - ...
    Si le sudoku n'est pas résoluble, lève une erreur
    """

    def __init__(self, boss):
        th.Thread.__init__(self)
        self.boss = boss
        self.sleep = 0.01
        self.power = True
        self.process = False
        self.resolution = False
        self.back_tracking = False
        self.methode_resolution = None
        self.taille = self.boss.taille
        self.sudoku = self.boss.sudoku
        self.nb_cases = self.boss.nb_cases
        self.carre = []
        self.ligne = []
        self.colonne = []
        self.possibilities = []
        self.starting_possibilities = []

    def run(self):
        while self.power:
            if self.process:
                self.begin()
                self.process = False
            else:
                time.sleep(0.1)

    def update(self, sudoku, methode):
        self.sudoku = copy(sudoku)
        self.methode_resolution = methode

    def checkBeforeStart(self):
        for i in range(self.nb_cases):
            liste_ligne = []
            liste_colonne = []
            liste_carre = []
            x = 3 * (i // 3)
            y = 3 * (i % 3)
            for j in range(self.nb_cases):
                if self.sudoku[x + j // 3, y + j % 3] in liste_carre \
                        or self.sudoku[j, i] in liste_colonne \
                        or self.sudoku[i, j] in liste_ligne:
                    return False
                if self.sudoku[i, j] != 0:
                    liste_ligne.append(self.sudoku[i, j])
                if self.sudoku[j, i] != 0:
                    liste_colonne.append(self.sudoku[j, i])
                if self.sudoku[x + j // 3, y + j % 3] != 0:
                    liste_carre.append(self.sudoku[x + j // 3, y + j % 3])
        return True

    def beforeStart(self):
        self.possibilities = []
        self.carre = []
        self.ligne = []
        self.colonne = []
        for i in range(self.nb_cases):
            values = [i + 1 for i in range(self.nb_cases)]
            self.carre.append(copy(values))
            self.ligne.append(copy(values))
            self.colonne.append(copy(values))
            x = 3 * (i // 3)
            y = 3 * (i % 3)
            for j in range(self.nb_cases):
                if self.sudoku[x + j // 3, y + j % 3] != 0 \
                        and self.sudoku[x + j // 3, y + j % 3] in self.carre[i]:
                    self.carre[i].remove(self.sudoku[x + j // 3, y + j % 3])
                if self.sudoku[i, j] != 0 and self.sudoku[i, j] in self.ligne[i]:
                    self.ligne[i].remove(self.sudoku[i, j])
                if self.sudoku[j, i] != 0 and self.sudoku[j, i] in self.colonne[i]:
                    self.colonne[i].remove(self.sudoku[j, i])
                if not self.sudoku[i][j] and (i, j) not in self.possibilities:
                    self.possibilities.append((i, j))
        self.starting_possibilities = copy(self.possibilities)

    def begin(self):
        self.beforeStart()
        if not self.checkBeforeStart():
            self.boss.setError("sudoku_insoluble")
        else:
            zero_time = time.time()
            n = 0
            print(self.methode_resolution)
            if self.methode_resolution == "Backtracking":
                self.backTracking()
            else:
                self.resolution = True
                while self.resolution:
                    n += 1
                    sudoku = copy(self.sudoku)
                    if self.methode_resolution == "Inclusion":
                        self.inclusion()
                    if self.methode_resolution == "Exclusion":
                        self.exclusion()
                    if self.methode_resolution == "Globale":
                        self.inclusion()
                        self.exclusion()
                    if np.all(self.sudoku == sudoku):
                        self.resolution = False
                    sudoku = copy(self.sudoku)
                if np.any(self.sudoku == np.zeros((self.nb_cases, self.nb_cases), int)) and \
                                self.methode_resolution == "Globale":
                    self.methode_resolution = "Backtracking"
                    print("Backtracking")
                    self.backTracking()
            print(time.time() - zero_time, n, '\n')
        return self.sudoku, self.starting_possibilities

    def checkListe(self, x, y):
        """
        Renvoie la liste des valeurs possibles pour la case de coordonnées x et y
        :param x: int: ligne
        :param y: int: colonne
        :return: liste: list
        """
        liste = []
        if self.sudoku[x][y] == 0:
            liste = [i + 1 for i in range(self.nb_cases)]
            block_x = x - x % self.taille[0]
            block_y = y - y % self.taille[1]
            for i in range(self.nb_cases):
                if self.sudoku[x, i] in liste:
                    liste.remove(self.sudoku[x, i])
                if self.sudoku[i, y] in liste:
                    liste.remove(self.sudoku[i, y])
                if self.sudoku[block_x + i % self.taille[1], block_y + i // self.taille[0]] in liste:
                    liste.remove(self.sudoku[block_x + i % self.taille[1], block_y + i // self.taille[0]])
        return liste

    def inclusion(self):
        for x in range(self.nb_cases):
            for y in range(self.nb_cases):
                self.checkValues(x, y)

    def exclusion(self):
        for n in range(self.nb_cases):
            for k in self.carre[n]:
                x, y = 3 * (n // 3), 3 * (n % 3)
                x_possible = []
                y_possible = []
                for i in range(self.taille[0]):
                    if k in self.ligne[x + i]: x_possible.append(x + i)
                    if k in self.colonne[y + i]: y_possible.append(y + i)
                case_possible = []
                for x in x_possible:
                    for y in y_possible:
                        if (x, y) in self.possibilities: case_possible.append((x, y))
                self.setValuesExclusion(case_possible, k)

            j = n
            for k in self.colonne[j]:
                carre_possible = []
                case_possible = []
                for i in range(self.taille[0]):
                    if k in self.carre[3 * i + j // 3]:
                        carre_possible.append(3 * i + j // 3)
                for i in range(self.nb_cases):
                    if (i, j) in self.possibilities:
                        if k in self.ligne[i] and (i, j) not in case_possible and \
                                                        3 * (i // 3) + j // 3 in carre_possible:
                            case_possible.append((i, j))
                self.setValuesExclusion(case_possible, k)

            i = n
            for k in self.ligne[i]:
                carre_possible = []
                case_possible = []
                for j in range(self.taille[0]):
                    if k in self.carre[3 * (i // 3) + j]:
                        carre_possible.append(3 * (i // 3) + j)
                for j in range(self.nb_cases):
                    if (i, j) in self.possibilities:
                        if k in self.colonne[j] and (i, j) not in case_possible and \
                                                        3 * (i // 3) + j // 3 in carre_possible:
                            case_possible.append((i, j))
                self.setValuesExclusion(case_possible, k)

    def backTracking(self, start=True):
        """
        Résoud un sudoku selon la méthode de backtracking
        :return: None or -1
        """
        self.back_tracking = start
        liste_sudoku = []
        i = 0
        while self.back_tracking:
            time.sleep(self.sleep)
            x, y = self.possibilities[i]
            liste = self.checkListe(x, y)
            if liste:
                self.sudoku[x][y] = liste.pop(0)
                liste_sudoku.append(liste)
                i += 1
            else:
                while not liste:
                    i -= 1
                    x, y = self.possibilities[i]
                    try:
                        liste = liste_sudoku[i]
                    except IndexError:
                        self.sudoku = self.boss.sudoku
                        self.boss.setError("sudoku_insoluble")
                        return -1
                    if liste:
                        self.sudoku[x][y] = liste.pop(0)
                        liste_sudoku[i] = liste
                        i += 1
                        break
                    else:
                        liste_sudoku.pop(i)
                        self.sudoku[x][y] = 0
            if i >= len(self.possibilities): self.back_tracking = False

    def checkValues(self, x, y):
        if (x, y) in self.possibilities:
            possibilities = []
            n = 3 * (x // 3) + y // 3
            for i in range(1, self.nb_cases + 1):
                if i in self.ligne[x] and i in self.colonne[y] and i in self.carre[n]:
                    possibilities.append(i)
            self.setValues(possibilities, x, y)

    def setValuesExclusion(self, case_possible, k):
        if len(case_possible) == 1:
            x, y = case_possible[0][0], case_possible[0][1]
            n = 3 * (x // 3) + y // 3
            self.sudoku[x, y] = k
            self.possibilities.remove((x, y))
            self.ligne[x].remove(k)
            self.colonne[y].remove(k)
            self.carre[n].remove(k)

    def setValues(self, possibilities, x, y):
        if len(possibilities) == 1:
            k = possibilities[0]
            n = 3 * (x // 3) + y // 3
            self.sudoku[x, y] = k
            if (x, y) in self.possibilities: self.possibilities.remove((x, y))
            self.ligne[x].remove(k)
            self.colonne[y].remove(k)
            self.carre[n].remove(k)

    def wait(self):
        pass


if __name__ == "__main__":
    class Boss:
        def __init__(self):
            self.taille = (3, 3)
            self.nb_cases = 9
            self.sudoku = np.array([[3, 0, 0, 2, 0, 9, 0, 0, 5],
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0],
                                    [0, 7, 8, 0, 0, 0, 2, 4, 0],
                                    [0, 5, 0, 4, 0, 7, 0, 9, 0],
                                    [0, 6, 0, 0, 2, 0, 0, 8, 0],
                                    [0, 9, 0, 5, 0, 3, 0, 1, 0],
                                    [0, 8, 1, 0, 0, 0, 6, 3, 0],
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0],
                                    [7, 0, 0, 8, 0, 5, 0, 0, 1]])
            self.Resolution = Resolution(self)
            self.Resolution.start()
            self.Resolution.update(self.sudoku, "Globale")
            print(self.sudoku)


    Boss()
