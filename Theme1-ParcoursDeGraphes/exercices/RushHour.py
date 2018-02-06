from typing import List, Tuple, Union
from collections import deque
import tqdm
from tqdm import tqdm_notebook
import copy, numpy, io

Position = numpy.array

# Une position est représentée par un tableau numpy (i,j)
# - i: la ligne
# - j: la colonne

directions = {'R': (0,1), 'L': (0,-1),
              'U': (-1,0), 'D': (1,0)}

couleurs = {'X': 'red',
            'A': 'lightgreen',
            'B': 'orange',
            'C': 'lightblue',
            'D': 'pink',
            'E': 'violet',
            'F': 'green',
            'G': 'gray',
            'H': 'khaki',
            'I': 'yellow',
            'J': 'brown',
            'K': 'darkkhaki',
            'O': 'yellow',
            'P': 'purple',
            'Q': 'blue',
            'R': 'green'}

class Voiture:
    '''
    Un objet mutable représentant une voiture
    '''
    def __init__(self, s=None, lettre=None, position=None, direction=None, longueur=None):
        '''
            >>> from RushHour import Voiture
            >>> voiture = Voiture('O3D32'); voiture
            O3D32
            >>> voiture.lettre
            'O'
            >>> voiture.longueur
            3
            >>> voiture.position
            array([3, 2])
            >>> voiture.direction
            array([1, 0])
            >>> Voiture(lettre='O', position=(3,2), longueur=3, direction='D')
            O3D32
        '''
        if s is not None:
            lettre = s[0]
            longueur = int(s[1])
            direction = s[2]
            position = (int(s[3]), int(s[4]))
        if isinstance(direction, str):
            direction = directions[direction]

        assert isinstance(lettre, str) and len(lettre) == 1
        assert isinstance(longueur, int) and 0 <= longueur and longueur <= 3

        assert isinstance(position, tuple)
        assert len(position) == 2
        i = position[0]
        assert isinstance(i, int) and 0 <= i # and x < 6
        j = position[0]
        assert isinstance(j, int) and 0 <= j # and x < 6
        position = Position(position)

        assert direction in directions.values()
        direction = Position(direction)

        self.lettre = lettre
        self.longueur = longueur
        self.position = position
        self.direction = direction

    def cases(self) -> List[Position]:
        '''
        Renvoie les cases occupées par la voiture

            >>> from RushHour import Voiture
            >>> voiture = Voiture('O3D32')
            >>> voiture.cases()
            [array([3, 2]), array([4, 2]), array([5, 2])]

            >>> from RushHour import Voiture
            >>> voiture = Voiture('O2L32')
            >>> voiture.cases()
            [array([3, 2]), array([3, 1])]
        '''
        return [self.position + i * self.direction for i in range(self.longueur)]

    def case_devant(self) -> Position:
        '''
        Renvoie la case devant la voiture

            >>> from RushHour import Voiture
            >>> voiture = Voiture('O3R32')
            >>> voiture.case_devant()
            array([3, 5])
        '''
        return self.position + self.direction * self.longueur

    def case_derriere(self) -> Position:
        '''
        Renvoie la case derrière la voiture

            >>> from RushHour import Voiture
            >>> voiture = Voiture('O3R32')
            >>> voiture.case_devant()
            array([3, 5])

            >>> from RushHour import Voiture
            >>> voiture = Voiture('O3L32')
            >>> voiture.case_devant()
            array([ 3, -1])
        '''
        return self.position - self.direction

    def avance(self, distance: int = 1) -> None:
        '''
        Fait avancer la voiture de `distance` cases

            >>> from RushHour import Voiture
            >>> voiture = Voiture('O3R32')
            >>> original = copy.copy(voiture)
            >>> voiture.cases()
            [array([3, 2]), array([3, 3]), array([3, 4])]
            >>> voiture.avance()
            >>> voiture.cases()
            [array([3, 3]), array([3, 4]), array([3, 5])]
            >>> voiture.avance(2)
            >>> voiture.cases()
            [array([3, 5]), array([3, 6]), array([3, 7])]

        Vérifions qu'il n'y a pas d'effet de reference::

            >>> original.cases()
            [array([3, 2]), array([3, 3]), array([3, 4])]
        '''
        # Don't use += !
        self.position = self.position + self.direction*distance

    def recule(self) -> None:
        '''
        Fait reculer la voiture d'une case

            >>> from RushHour import Voiture
            >>> voiture = Voiture('I3D32')
            >>> voiture.cases()
            [array([3, 2]), array([4, 2]), array([5, 2])]
            >>> voiture.recule()
            >>> voiture.cases()
            [array([2, 2]), array([3, 2]), array([4, 2])]
        '''
        return self.avance(-1);

    def __repr__(self):
        '''
            >>> from RushHour import Voiture
            >>> Voiture('I3D32')
            I3D32
        '''
        for direction_lettre, direction in directions.items():
            if numpy.array_equal(direction, self.direction):
                break
        return '{}{}{}{}{}'.format(self.lettre, self.longueur,
                                   direction_lettre,
                                   self.position[0], self.position[1])

class Plateau:
    '''
    Un objet immutable représentant l'état d'un plateau de Rush Hour
    '''
    def __init__(self, voitures: Union[List, List[str],int,None]):
        '''
        Construit un plateau à partir d'une liste de descriptions de
        voitures, d'un nom de fichier contenant le niveau ou du numéro
        de niveau

            >>> from RushHour import Plateau
            >>> plateau = Plateau(['A2R00','X2R21','C2R44','R3R52','O3D05','P3D10','Q3D13','B2D40'])
            >>> len(plateau.voitures)
            8
            >>> plateau.dimension
            6
            >>> plateau.ligne_sortie
            2
            >>> plateau
            +------+
            |AA   O|
            |P  Q O|
            |PXXQ O 
            |P  Q  |
            |B   CC|
            |B RRR |
            +------+
            >>> Plateau('RushHourDefis/Defi01.txt')
            +------+
            |AA   O|
            |P  Q O|
            |PXXQ O 
            |P  Q  |
            |B   CC|
            |B RRR |
            +------+
            >>> Plateau(3)
            +------+
            |      |
            |      |
            | XXO   
            | AAO P|
            | B O P|
            | BCC P|
            +------+
            '''
        self.dimension = 6
        self.ligne_sortie = 2
        if isinstance(voitures,int):
            voitures = 'RushHourDefis/Defi{:02d}.txt'.format(voitures)
        if isinstance(voitures,str):
            with open(voitures) as file:
                voitures = file.readlines()
        voitures = [Voiture(s) for s in voitures]
        self.voitures = { voiture.lettre: voiture for voiture in voitures }

    def tableau(self) -> Tuple[str]:
        '''
        Renvoie une représentation du plateau sous forme
        d'une liste de chaînes de caractères

            >>> from RushHour import Plateau
            >>> plateau = Plateau(['A2R00','X2R21','C2R44','R3R52','O3D05','P3D10','Q3D13','B2D40'])
            >>> plateau.tableau()
            ('AA   O', 'P  Q O', 'PXXQ O', 'P  Q  ', 'B   CC', 'B RRR ')
            >>> print('\\n'.join(ligne for ligne in plateau.tableau()))
            AA   O
            P  Q O
            PXXQ O
            P  Q  
            B   CC
            B RRR 

        Mémoization::

            >>> plateau.tableau() is plateau.tableau()
            True
        '''
        if not hasattr(self, '_tableau'):
            tableau = [ [' ' for j in range(self.dimension)]
                            for i in range(self.dimension) ]
            for voiture in self.voitures.values():
                for (i,j) in voiture.cases():
                    tableau[i][j] = voiture.lettre;
            self._tableau = tuple(''.join(ligne) for ligne in tableau)
        return self._tableau

    def __repr__(self) -> str:
        '''
        Renvoie un affichage de ce plateau

            >>> from RushHour import Plateau
            >>> Plateau(['A2R00','X2R21','C2R44','R3R52','O3D05','P3D10','Q3D13','B2D40'])
            +------+
            |AA   O|
            |P  Q O|
            |PXXQ O 
            |P  Q  |
            |B   CC|
            |B RRR |
            +------+
        '''
        s = '+' + '-'*self.dimension + '+\n'
        for i,ligne in enumerate(self.tableau()):
            s += '|' + ligne
            if i == self.ligne_sortie:
                s += ' '
            else:
                s += '|'
            s += '\n'
        s += '+' + '-'*self.dimension + '+'
        return s

    def __hash__(self) -> int:
        '''
        Fonction de hachage

            >>> from RushHour import Plateau
            >>> plateau = Plateau(['A2R00','X2R21','C2R44','R3R52','O3D05','P3D10','Q3D13','B2D40'])
            >>> hash(plateau) == hash(plateau)
            True
        '''
        return hash(str(self.tableau()))

    def __eq__(self, other) -> bool:
        '''
        Teste si `self` est egal à other

            >>> from RushHour import Plateau
            >>> plateau1 = Plateau(['A2R00','X2R21'])
            >>> plateau2 = Plateau(['B2R00','X2R21'])
            >>> plateau1 == plateau1
            True
            >>> plateau2 == plateau1
            False
        '''
        return other.__class__ == self.__class__ and other.tableau() == self.tableau()

    def est_gagnant(self):
        '''
        Teste si ce plateau est gagnant

        c'est à dire que la sortie est juste devant la voiture `X`

            >>> plateau = Plateau(['A2R04','X2R21']); plateau
            +------+
            |    AA|
            |      |
            | XX    
            |      |
            |      |
            |      |
            +------+
            >>> plateau.est_gagnant()
            False
            >>> plateau = Plateau(['A2R00','X2R24']); plateau
            +------+
            |AA    |
            |      |
            |    XX 
            |      |
            |      |
            |      |
            +------+
            >>> plateau.est_gagnant()
            True
        '''
        return self.voitures['X'].case_devant()[1] == self.dimension

    def avance(self, lettre: str, distance:int=1) -> Union['Plateau', None]:
        '''
        Renvoie le nouveau plateau obtenu en faisant avancer la voiture `lettre`.

        Renvoie `None` si la voiture ne peux pas avancer.

        Si `distance` vaut `-1`, fait reculer la voiture.

            >>> plateau0 = Plateau(['A2R00','X2R21','C2R44','R3R52','O3D05','P3D10','Q3D13','B2D40'])
            >>> plateau1 = plateau0.avance('A')
            >>> plateau2 = plateau1.avance('Q')
            >>> plateau3 = plateau2.recule('R')
            >>> plateau0
            +------+
            |AA   O|
            |P  Q O|
            |PXXQ O 
            |P  Q  |
            |B   CC|
            |B RRR |
            +------+
            >>> plateau1
            +------+
            | AA  O|
            |P  Q O|
            |PXXQ O 
            |P  Q  |
            |B   CC|
            |B RRR |
            +------+
            >>> plateau2
            +------+
            | AA  O|
            |P    O|
            |PXXQ O 
            |P  Q  |
            |B  QCC|
            |B RRR |
            +------+
            >>> plateau3
            +------+
            | AA  O|
            |P    O|
            |PXXQ O 
            |P  Q  |
            |B  QCC|
            |BRRR  |
            +------+
            >>> plateau0.avance('X')
            >>> plateau0.avance('C')
            >>> plateau0.avance('B')
            >>> plateau0.avance('A', -1)
            >>> plateau2.avance('Q')
        '''
        tableau = self.tableau()
        voiture = copy.copy(self.voitures[lettre])
        for step in range(abs(distance)):
            (i,j) = voiture.case_devant() if distance > 0 else voiture.case_derriere()
            if i < 0 or i >= self.dimension or j < 0 or j >= self.dimension:
                return None
            if tableau[i][j] != ' ':
                return None
            voiture.avance(1 if distance > 0 else -1)
        plateau = copy.copy(self)
        del plateau._tableau # TODO: Define a copy operator instead
        plateau.voitures = copy.copy(self.voitures)
        plateau.voitures[lettre] = voiture
        return plateau

    def recule(self, lettre: str) -> Union['Plateau', None]:
        '''
        Renvoie le nouveau plateau obtenu en faisant reculer la voiture `lettre`

            >>> plateau = Plateau(['A2R00','X2R21','C2R44','R3R52','O3D05','P3D10','Q3D13','B2D40'])
            >>> plateau
            +------+
            |AA   O|
            |P  Q O|
            |PXXQ O 
            |P  Q  |
            |B   CC|
            |B RRR |
            +------+
            >>> plateau.recule('Q')
            +------+
            |AA Q O|
            |P  Q O|
            |PXXQ O 
            |P     |
            |B   CC|
            |B RRR |
            +------+
            >>> plateau.recule('X')
        '''
        return self.avance(lettre, -1)

    def deplace(self, lettre: str, direction: Union[str,None]=None, distance: int=1) -> Union['Plateau',None]:
        '''
            >>> plateau = Plateau(['A2R00','X2R21','C2R44','R3R52','O3D05','P3D10','Q3D13','B2D40'])
            >>> plateau
            +------+
            |AA   O|
            |P  Q O|
            |PXXQ O 
            |P  Q  |
            |B   CC|
            |B RRR |
            +------+
            >>> plateau.deplace('CL3')
            +------+
            |AA   O|
            |P  Q O|
            |PXXQ O 
            |P  Q  |
            |BCC   |
            |B RRR |
            +------+
            >>> plateau.deplace('OD1')
            +------+
            |AA    |
            |P  Q O|
            |PXXQ O 
            |P  Q O|
            |B   CC|
            |B RRR |
            +------+
            >>> plateau.deplace('R', 'R', 1)
            +------+
            |AA   O|
            |P  Q O|
            |PXXQ O 
            |P  Q  |
            |B   CC|
            |B  RRR|
            +------+
            >>> plateau.deplace('QR3')
            >>> plateau.deplace('R', 'L', 2)
            >>> plateau.deplace('A', 'L', 1)
        '''
        if len(lettre) == 3:
            direction = lettre[1]
            distance = int(lettre[2])
            lettre = lettre[0]
        direction = Position(directions[direction])
        if (abs(direction) != abs(self.voitures[lettre].direction)).any():
            return None
        if (direction != self.voitures[lettre].direction).any():
            distance = -distance
        return self.avance(lettre, distance)

    def voisins(self):
        '''
        Renvoie les voisins de ce plateau.

        C'est-à-dire ceux qui peuvent être atteints en un seul déplacement.

            >>> from pprint import pprint
            >>> plateau = Plateau(40); plateau
            +------+
            |OAA B |
            |OCD BP|
            |OCDXXP 
            |QQQE P|
            |  FEKK|
            |HHFII |
            +------+
            >>> pprint(plateau.voisins()) # doctest: +NORMALIZE_WHITESPACE
            {'AR1': +------+
                    |O AAB |
                    |OCD BP|
                    |OCDXXP 
                    |QQQE P|
                    |  FEKK|
                    |HHFII |
                    +------+,
            'IR1':  +------+
                    |OAA B |
                    |OCD BP|
                    |OCDXXP 
                    |QQQE P|
                    |  FEKK|
                    |HHF II|
                    +------+,
            'PU1':  +------+
                    |OAA BP|
                    |OCD BP|
                    |OCDXXP 
                    |QQQE  |
                    |  FEKK|
                    |HHFII |
                    +------+}
        '''
        voisins = {}
        for lettre in self.voitures.keys():
            for direction in directions.keys():
                for distance in range(1, self.dimension):
                    voisin = self.deplace(lettre, direction, distance)
                    if not voisin:
                        break
                    deplacement = "{}{}{}".format(lettre, direction, distance)
                    voisins[deplacement] = voisin
        return voisins

class RushHour:
    solutions = {
        1: ['CL3', 'OD3', 'AR1', 'PU1', 'BU1', 'RL2', 'QD2', 'XR3'],
        2: ['EL1', 'PD2', 'XR1', 'AD1', 'OL3', 'CU2', 'BU1', 'XR3'],
        3: ['PU3', 'OU2', 'CR2', 'AR3', 'OD3', 'XR1', 'BU4', 'XL1', 'OU3', 'CL3', 'AL3', 'PD3', 'OD3', 'XR3']
        }

    @staticmethod
    def niveaux():
        '''
        Renvoie la liste des niveaux disponibles

            >>> RushHour.niveaux()
            [1, 3, 7, 8, 11, 15, 21, 38, 40]
        '''
        niveaux = []
        for i in range(1,41):
            try:
                Plateau(i)
                niveaux.append(i)
            except:
                pass
        return niveaux

    @staticmethod
    def est_solution(niveau, coups):
        '''
        Teste si une liste de coup est une solution pour ce niveau

            >>> RushHour.est_solution(1, ['CL3', 'OD3', 'AR1', 'PU1', 'BU1', 'RL2', 'QD2', 'XR3'])
            True
            >>> RushHour.est_solution(1, ['CL3', 'OD3', 'AR1', 'PU1', 'BU1', 'RL2', 'QD2'])
            False
            >>> RushHour.est_solution(1, ['XR3'])
            False

            >>> RushHour.est_solution(1, RushHour.solutions[1])
            True
            >>> RushHour.est_solution(3, RushHour.solutions[3])
            True
            >>> RushHour.est_solution(1, RushHour.solutions[3])
            False
            >>> RushHour.est_solution(3, RushHour.solutions[1])
            False
        '''
        plateau = Plateau(niveau)
        for coup in coups:
            #print(plateau)
            plateau = plateau.deplace(coup)
            if not plateau:
                return False
        #print(plateau)
        return plateau.est_gagnant()

    @staticmethod
    def solution(niveau, return_graph=False, verbeux=False):
        '''
        Renvoie une solution optimale pour ce niveau

            >>> RushHour.solution(1) # doctest: +SKIP
            ['AR1', 'CL3', 'OD3', 'PU1', 'BU1', 'RL2', 'QD2', 'XR3']
        '''
        ### BEGIN SOLUTION
        if verbeux:
            progressbar = tqdm.tqdm() # tqdm.tqdm_notebook()
        plateau = Plateau(defi)
        afaire = deque([plateau])
        predecesseurs = {plateau: None}
        if plateau.est_gagnant():
            return []
        while afaire:
            sommet = afaire.popleft()
            for label, voisin in sommet.voisins().items():
                if voisin in predecesseurs:
                    continue
                if verbeux:
                    progressbar.update()
                    progressbar.set_postfix({'afaire': len(afaire)})
                predecesseurs[voisin] = label, sommet
                afaire.append(voisin)
                if voisin.est_gagnant():
                    if return_graph:
                        return predecesseurs
                    sommet = voisin
                    chemin = []
                    while predecesseurs[sommet] != None:
                        label, sommet = predecesseurs[sommet]
                        chemin.append(label)
                    chemin.reverse()
                    return chemin
        if return_grpah:
            return predecesseurs
        return None
        ### END SOLUTION
