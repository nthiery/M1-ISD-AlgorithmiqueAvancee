from typing import List, Tuple, Union

import numpy
import copy

Position = numpy.array

# Une position est représentée par un tableau numpy (i,j)
# - i: la ligne
# - j: la colonne

directions = {'R': (0,1), 'L': (0,-1),
              'U': (-1,0), 'D': (1,0)}

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
    def __init__(self, voitures: List[str]):
        '''
            >>> from RushHour import Plateau
            >>> plateau = Plateau(['A2R00','X2R21','C2R44','R3R52','O3D05','P3D10','Q3D13','B2D40'])
            >>> len(plateau.voitures)
            8
        '''
        self.dimension = 6
        self.ligne_sortie = 2
        voitures = [Voiture(s) for s in voitures]
        self.voitures = { voiture.lettre: voiture for voiture in voitures }

    def tableau(self) -> Tuple[str]:
        '''
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

        '''
        tableau = [ [' ' for j in range(self.dimension)]
                    for i in range(self.dimension) ]
        for voiture in self.voitures.values():
            for (i,j) in voiture.cases():
                tableau[i][j] = voiture.lettre;
        return tuple(''.join(ligne) for ligne in tableau)

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

            >>> from RushHour import Plateau
            >>> plateau = Plateau(['A2R00','X2R21','C2R44','R3R52','O3D05','P3D10','Q3D13','B2D40'])
            >>> hash(plateau) == hash(plateau)
            True
        '''
        return hash(str(self.tableau()))

    def avance(self, lettre: str, distance:int=1) -> Union['Plateau', None]:
        """
        Renvoie le nouveau plateau obtenu en faisant avancer la voiture `lettre`.

        Renvoie `None` si la voiture ne peux pas avancer.

        Si `distance` vaut `-1`, fait reculer la voiture.

            >>> plateau0 = Plateau(['A2R00','X2R21','C2R44','R3R52','O3D05','P3D10','Q3D13','B2D40'])
            >>> plateau1 = plateau0.avance("A")
            >>> plateau2 = plateau1.avance("Q")
            >>> plateau3 = plateau2.recule("R")
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
            >>> plateau0.avance("X")
            >>> plateau0.avance("C")
            >>> plateau0.avance("B")
            >>> plateau0.avance("A", -1)
            >>> plateau2.avance("Q")
        """
        tableau = self.tableau()
        voiture = copy.copy(self.voitures[lettre])
        for step in range(abs(distance)):
            (i,j) = voiture.case_devant() if distance > 0 else voiture.case_derriere()
            if i < 0 or i >= self.dimension or j < 0 or j >= self.dimension:
                return None
            if tableau[i][j] != " ":
                return None
            voiture.avance(1 if distance > 0 else -1)
        plateau = copy.copy(self)
        plateau.voitures = copy.copy(self.voitures)
        plateau.voitures[lettre] = voiture
        return plateau

    def recule(self, lettre: str) -> Union['Plateau', None]:
        """
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
            >>> plateau.recule("Q")
            +------+
            |AA Q O|
            |P  Q O|
            |PXXQ O 
            |P     |
            |B   CC|
            |B RRR |
            +------+
            >>> plateau.recule("X")
        """
        return self.avance(lettre, -1)
