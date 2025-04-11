from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QComboBox
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QPixmap
from PyQt5.QtCore import Qt, QRect, QPoint, QTimer, QPropertyAnimation, QEasingCurve
import sys
import random
import os


CARD_WIDTH, CARD_HEIGHT = 80, 120
SPACING_X = 100
SPACING_Y = 30
MARGIN = 20
SUITS = ['spades', 'hearts', 'diamonds', 'clubs']
RANKS = ['A'] + [str(i) for i in range(2, 11)] + ['J', 'Q', 'K']
ASSETS_PATH = 'assets/textures'

class Card:
    def __init__(self, suit, rank, face_up=False):
        self.suit = suit
        self.rank = rank
        self.face_up = face_up
        self.rect = QRect(0, 0, CARD_WIDTH, CARD_HEIGHT)
        self.front_image = QPixmap(os.path.join(ASSETS_PATH, f"{rank}_of_{suit}.png"))
        self.back_image = QPixmap(os.path.join(ASSETS_PATH, "back.png"))


    def draw(self, painter, x, y):
        self.rect.moveTo(x, y)
        if self.face_up and not self.front_image.isNull():
            painter.drawPixmap(self.rect, self.front_image)
        elif not self.face_up and not self.back_image.isNull():
            painter.drawPixmap(self.rect, self.back_image)
        else:
            painter.setBrush(Qt.white if self.face_up else QColor(0, 0, 128))
            painter.setPen(QPen(Qt.black, 2))
            painter.drawRect(self.rect)
            if self.face_up:
                painter.setFont(QFont('Arial', 12))
                color = Qt.black if self.suit in ['spades', 'clubs'] else Qt.red
                painter.setPen(QPen(color))
                painter.drawText(x + 10, y + 25, f'{self.rank} {self.suit[0].upper()}')


    def can_stack_on(self, other):
        if not other or not other.face_up:
            return False
        color1 = self.suit in ['hearts', 'diamonds']
        color2 = other.suit in ['hearts', 'diamonds']
        return color1 != color2 and RANKS.index(self.rank) + 1 == RANKS.index(other.rank)


    def can_move_to_foundation(self, top_card):
        if not top_card:
            return self.rank == 'A'
        return self.suit == top_card.suit and RANKS.index(self.rank) == RANKS.index(top_card.rank) + 1


    def is_ace(self):
        return self.rank == 'A'


    def is_king(self):
        return self.rank == 'K'


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
        self.score = 0
        self.score_label = QLabel(self)
        self.score_label.setGeometry(800, 20, 200, 30)
        self.score_label.setFont(QFont('Arial', 14))
        self.new_game_button = QPushButton("New Game", self)
        self.new_game_button.setGeometry(800, 60, 100, 30)
        self.new_game_button.clicked.connect(self.reset_game)
        self.theme_box = QComboBox(self)
        self.theme_box.setGeometry(800, 100, 120, 30)
        self.theme_box.addItems(["Green", "Wood", "Blue"])
        self.theme_box.currentIndexChanged.connect(self.update)
        self.score_timer = QTimer(self)
        self.score_timer.timeout.connect(self.decrease_score)
        self.score_timer.start(4440)
        self.reset_game()
        self.show()


    def reset_game(self):
        self.deck = create_deck()
        self.tableau = deal_tableau(self.deck)
        self.stock = self.deck[:]
        self.waste = []
        self.foundations = [[] for _ in range(4)]
        self.dragging_card = None
        self.drag_stack = []
        self.drag_offset = QPoint()
        self.drag_column = None
        self.drag_pos = QPoint()
        self.score = 0
        self.update_score()
        self.update()


    def decrease_score(self):
        self.score -= 1
        self.update_score()


    def update_score(self):
        self.score_label.setText(f"Score: {self.score}")


    def get_background_image(self):
        theme = self.theme_box.currentText().lower()
        file = f"table_{theme}.png"
        path = os.path.join(ASSETS_PATH, file)
        if os.path.exists(path):
            return QPixmap(path)
        return None


    def paintEvent(self, event):
        painter = QPainter(self)
        bg_image = self.get_background_image()
        if bg_image:
            painter.drawPixmap(self.rect(), bg_image)
        else:
            painter.fillRect(self.rect(), QColor(0, 128, 0))
        for i in range(4):
            x = MARGIN + i * (CARD_WIDTH + 10)
            y = MARGIN
            painter.setBrush(Qt.NoBrush)
            painter.setPen(QPen(Qt.white, 2, Qt.DashLine))
            painter.drawRect(x, y, CARD_WIDTH, CARD_HEIGHT)
            if self.foundations[i]:
                self.foundations[i][-1].draw(painter, x, y)
        stock_x = MARGIN + 6 * (CARD_WIDTH + 10)
        stock_y = MARGIN
        if self.stock:
            painter.drawPixmap(stock_x, stock_y, CARD_WIDTH, CARD_HEIGHT, QPixmap(os.path.join(ASSETS_PATH, "back.png")))
        elif not self.stock and self.waste:
            painter.setBrush(QColor(0, 128, 0))
            painter.setPen(QPen(Qt.white, 2, Qt.DashLine))
            painter.drawRect(stock_x, stock_y, CARD_WIDTH, CARD_HEIGHT)
        if self.waste:
            self.waste[-1].draw(painter, stock_x - CARD_WIDTH - 10, stock_y)
        for i, column in enumerate(self.tableau):
            x = MARGIN + i * SPACING_X
            for j, card in enumerate(column):
                y = MARGIN + CARD_HEIGHT + 40 + j * SPACING_Y
                card.draw(painter, x, y)
        if self.drag_stack:
            for idx, card in enumerate(self.drag_stack):
                card.draw(painter, self.drag_pos.x(), self.drag_pos.y() + idx * SPACING_Y)


    def mousePressEvent(self, event):
        stock_x = MARGIN + 6 * (CARD_WIDTH + 10)
        stock_y = MARGIN
        stock_rect = QRect(stock_x, stock_y, CARD_WIDTH, CARD_HEIGHT)
        if stock_rect.contains(event.pos()):
            if self.stock:
                self.waste.append(self.stock.pop())
                self.waste[-1].face_up = True
                self.score += 5
                self.update_score()
            elif not self.stock and self.waste:
                self.stock = self.waste[::-1]
                for card in self.stock:
                    card.face_up = False
                self.waste = []
            self.update()
            return
        if self.waste:
            last = self.waste[-1]
            if last.rect.contains(event.pos()):
                self.dragging_card = last
                self.drag_offset = event.pos() - last.rect.topLeft()
                self.drag_stack = [self.waste.pop()]
                return
        for col_index, column in enumerate(self.tableau):
            if column:
                for i in reversed(range(len(column))):
                    card = column[i]
                    if card.face_up and card.rect.contains(event.pos()):
                        self.dragging_card = card
                        self.drag_column = col_index
                        self.drag_offset = event.pos() - card.rect.topLeft()
                        self.drag_stack = column[i:]
                        self.tableau[col_index] = column[:i]
                        return


    def mouseMoveEvent(self, event):
        if self.dragging_card:
            self.drag_pos = event.pos() - self.drag_offset
            self.update()


    def mouseReleaseEvent(self, event):
        if self.dragging_card:
            dropped = False
            for i in range(4):
                x = MARGIN + i * (CARD_WIDTH + 10)
                y = MARGIN
                rect = QRect(x, y, CARD_WIDTH, CARD_HEIGHT)
                if rect.contains(event.pos()) and len(self.drag_stack) == 1:
                    foundation = self.foundations[i]
                    top_card = foundation[-1] if foundation else None
                    if self.dragging_card.can_move_to_foundation(top_card):
                        foundation.append(self.dragging_card)
                        self.score += 10
                        dropped = True
                        break
            if not dropped:
                for i, column in enumerate(self.tableau):
                    x = MARGIN + i * SPACING_X
                    y = MARGIN + CARD_HEIGHT + 40 + len(column) * SPACING_Y
                    if QRect(x, y, CARD_WIDTH, CARD_HEIGHT).contains(event.pos()):
                        if not column or self.drag_stack[0].can_stack_on(column[-1]):
                            self.tableau[i].extend(self.drag_stack)
                            dropped = True
                            break
            if not dropped:
                if self.drag_column is not None:
                    self.tableau[self.drag_column].extend(self.drag_stack)
                else:
                    self.waste.extend(self.drag_stack)
            if self.drag_column is not None and self.tableau[self.drag_column]:
                top = self.tableau[self.drag_column][-1]
                if not top.face_up:
                    top.face_up = True
                    self.score += 5
            self.dragging_card = None
            self.drag_stack = []
            self.drag_column = None
            self.update_score()
            self.update()
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Solitaire()
    sys.exit(app.exec_())