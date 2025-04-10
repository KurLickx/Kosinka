from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QColor, QFont, QPen
from PyQt5.QtCore import Qt, QRect
import sys
import random



CARD_WIDTH, CARD_HEIGHT = 80, 120
SPACING_X = 100
SPACING_Y = 30
MARGIN = 20
SUITS = ['spades', 'hearts', 'diamonds', 'clubs']
RANKS = ['A'] + [str(i) for i in range(2, 11)] + ['J', 'Q', 'K']


class Card:
    def __init__(self, suit, rank, face_up=False):
        self.suit = suit
        self.rank = rank
        self.face_up = face_up
        self.rect = QRect(0, 0, CARD_WIDTH, CARD_HEIGHT)


    def draw(self, painter, x, y):
        self.rect.moveTo(x, y)
        if self.face_up:
            painter.setBrush(Qt.white)
        else:
            painter.setBrush(QColor(0, 0, 128))
        painter.setPen(QPen(Qt.black, 2))
        painter.drawRect(self.rect)
        if self.face_up:
            painter.setFont(QFont('Arial', 12))
            color = Qt.black if self.suit in ['spades', 'clubs'] else Qt.red
            painter.setPen(QPen(color))
            painter.drawText(x + 10, y + 25, f'{self.rank} {self.suit[0].upper()}')


def create_deck():
    deck = [Card(suit, rank) for suit in SUITS for rank in RANKS]
    random.shuffle(deck)
    return deck


def deal_tableau(deck):
    tableau = [[] for _ in range(7)]
    for col in range(7):
        for row in range(col + 1):
            card = deck.pop()
            card.face_up = (row == col)
            tableau[col].append(card)
    return tableau


class Solitaire(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Solitaire - Kosynka (PyQt5)")
        self.setGeometry(100, 100, 1024, 768)
        self.deck = create_deck()
        self.tableau = deal_tableau(self.deck)
        self.show()


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 128, 0))  
        for i, column in enumerate(self.tableau):
            x = MARGIN + i * SPACING_X
            for j, card in enumerate(column):
                y = MARGIN + j * SPACING_Y
                card.draw(painter, x, y)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Solitaire()
    sys.exit(app.exec_())
