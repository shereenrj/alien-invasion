import pygame
from pygame.sprite import Sprite

# Class to represent a single alien in the fleet 
# Initialize the alien and set its starting position
class Alien(Sprite):
    def __init__(self, ai_game):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        # Load the alien image and set its rect attribute
        self.image = pygame.image.load('ufofinal.png')
        self.rect = self.image.get_rect()
        # Start each new alien near the top left of the screen
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height
        # Store the alien's exact horizontal position
        self.x = float(self.rect.x)
        
    #Checking if an alien has hit an edge 
    def check_edges(self):
        screen_rect = self.screen.get_rect()
        if self.rect.right >= screen_rect.right or self.rect.left <= 0:
            return True
    
    
    #Moving the alien to the right 
    def update(self):
        self.x += (self.settings.alien_speed * self.settings.fleet_direction)
        self.rect.x = self.x
        
