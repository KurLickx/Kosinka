import pygame
import random

WIDTH, HEIGHT = 1024, 768
CARD_WIDTH, CARD_HEIGHT = 80, 120
FPS = 60
MARGIN = 20
SPACING_X = 100
SPACING_Y = 30
FOUNDATION_X = 650
FOUNDATION_Y = MARGIN
STOCKPILE_X = 850
STOCKPILE_Y = MARGIN
SUITS = ['spades', 'hearts', 'diamonds', 'clubs']
RANKS = ['A'] + [str(i) for i in range(2, 11)] + ['J', 'Q', 'K']
WHITE = (255, 255, 255)
GREEN = (0, 128, 0)
BLACK = (0, 0, 0)
RED = (200, 0, 0)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Solitaire - Kosynka")
clock = pygame.time.Clock()
font = pygame.font.SysFont('arial', 20)

class Card:
    def __init__(self, suit, rank, face_up=False):
        self.suit = suit
        self.rank = rank
        self.face_up = face_up
        self.image = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        self.rect = self.image.get_rect()


    def draw(self, surface, x, y):
        self.rect.topleft = (x, y)
        if self.face_up:
            self.image.fill(WHITE)
            text = font.render(f'{self.rank} {self.suit[0].upper()}', True, BLACK if self.suit in ['spades', 'clubs'] else RED)
            self.image.blit(text, (10, 10))
        else:
            self.image.fill((0, 0, 128))
        pygame.draw.rect(self.image, BLACK, self.image.get_rect(), 2)
        surface.blit(self.image, self.rect)


    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


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


def is_valid_move(card, target_stack):
    if not target_stack:
        return card.rank == 'K'
    top_card = target_stack[-1]
    if card.suit in ['hearts', 'diamonds']:
        valid_color = top_card.suit in ['spades', 'clubs']
    else:
        valid_color = top_card.suit in ['hearts', 'diamonds']
    return valid_color and RANKS.index(card.rank) == RANKS.index(top_card.rank) - 1

deck = create_deck()
tableau = deal_tableau(deck)
foundation = {suit: [] for suit in SUITS}
stockpile = deck[:24]
selected_card = None
dragging = False
running = True
while running:
    screen.fill(GREEN)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if selected_card is None:
                for i, column in enumerate(tableau):
                    for card in column:
                        if card.is_clicked(mouse_pos) and card.face_up:
                            selected_card = card
                            dragging = True
                            column.remove(card)
                            break
            elif dragging:
                if selected_card.rect.collidepoint(mouse_pos):
                    for i, column in enumerate(tableau):
                        if column == tableau[i] and is_valid_move(selected_card, column):
                            column.append(selected_card)
                            dragging = False
                            selected_card = None
                            break
        if event.type == pygame.MOUSEBUTTONUP:
            if dragging:
                mouse_pos = pygame.mouse.get_pos()
                if mouse_pos[0] > FOUNDATION_X: 
                    for suit, foundation_pile in foundation.items():
                        if mouse_pos[1] > FOUNDATION_Y and mouse_pos[1] < FOUNDATION_Y + CARD_HEIGHT:
                            foundation_pile.append(selected_card)
                            dragging = False
                            selected_card = None
                            break

    for i, column in enumerate(tableau):
        x = MARGIN + i * SPACING_X
        for j, card in enumerate(column):
            y = MARGIN + j * SPACING_Y
            card.draw(screen, x, y)

    for i, suit in enumerate(SUITS):
        x = FOUNDATION_X + i * (CARD_WIDTH + 10)
        if foundation[suit]:
            top_card = foundation[suit][-1]
            top_card.draw(screen, x, FOUNDATION_Y)
        else:
            pygame.draw.rect(screen, BLACK, (x, FOUNDATION_Y, CARD_WIDTH, CARD_HEIGHT), 2)
    pygame.draw.rect(screen, BLACK, (STOCKPILE_X, STOCKPILE_Y, CARD_WIDTH, CARD_HEIGHT), 2)
    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()