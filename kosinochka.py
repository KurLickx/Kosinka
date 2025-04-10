import pygame
import random

WIDTH, HEIGHT = 1024, 1024
CARD_WIDTH, CARD_HEIGHT = 60, 100
FPS = 30
MARGIN = 20
SPACING_X = 100
SPACING_Y = 30
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
            self.image.fill((0, 0, 128))  # Back of card
        pygame.draw.rect(self.image, BLACK, self.image.get_rect(), 2)
        surface.blit(self.image, self.rect)

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
deck = create_deck()
tableau = deal_tableau(deck)

running = True
while running:
    screen.fill(GREEN)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    for i, column in enumerate(tableau):
        x = MARGIN + i * SPACING_X
        for j, card in enumerate(column):
            y = MARGIN + j * SPACING_Y
            card.draw(screen, x, y)

    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()
