import sys
from time import sleep
import pygame
from settings import Settings
from game_stats import GameStats
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien
from scoreboard import Scoreboard



# Create the screen
# screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
# pygame.display.set_caption("Alien Invasion")


# Main class to manage the game
class AlienInvasion:
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        self.clock = pygame.time.Clock()
        self.settings = Settings()
        # self.screen = screen  # Assign the screen object here
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("Alien Invasion")
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        
        self._create_fleet()
        self.game_active = False
        self.play_button = Button(self, "Play")
        
        
        


    # Run the game loop
    def run_game(self):
        while True:
            self._check_events()
            
            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
            self._update_screen()

    # Respond to keypresses and events
    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
                
    def _check_play_button(self, mouse_pos):
        if self.play_button.rect.collidepoint(mouse_pos):
            button_clicked = self.play_button.rect.collidepoint(mouse_pos)
            if button_clicked and not self.stats.game_active:
                self.settings.initialize_dynamic_settings()
                self.stats.reset_stats()
                self.stats.game_active = True
                self.sb.prep_score()
                self.sb.prep_level()
                self.sb.prep_ships()
                self.aliens.empty()
                self.bullets.empty()
                self._create_fleet()
                self.ship.center_ship()
                pygame.mouse.set_visible(False)

                
    def _update_bullets(self):
        self.bullets.update()
        for bullet in self.bullets.copy():
                if bullet.rect.bottom <= 0:
                    self.bullets.remove(bullet)
        self._check_bullet_alien_collisions()
        
    #Respond to bullet-alien collisions
    def _check_bullet_alien_collisions(self):
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()
        #Destroy existing bullets and create new fleet
        if not self.aliens:
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
            self.stats.level += 1
            self.sb.prep_level()
                  
    #Update the positions of all aliens in the fleet  
    def _update_aliens(self):
        self._check_fleet_edges()
        self.aliens.update()
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
            
        self._check_aliens_bottom()
            
            
    #Create a fleet of aliens 
    def _create_fleet(self):
        #Creating an alien and find the number of aliens in a row.
        #Spacing between each alien is equal to one alien width.
        alien = Alien(self)
        alien_width = alien.rect.width
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)
        #Determining the number of rows of aliens that fit on the screen
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)
        
        #Creating the full fleet of aliens.
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)
                
                

    def _create_alien(self, alien_number, row_number):
        alien = Alien(self)
        alien_width = alien.rect.width
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)
        
    #Respond appropriately if any aliens have reached an edge
    def _check_fleet_edges(self):
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break
            
            
            
    #Drop the entire fleet and change the fleet's direction.
    def _change_fleet_direction(self):
            for alien in self.aliens.sprites():
                alien.rect.y += self.settings.fleet_drop_speed
            self.settings.fleet_direction *= -1
        
    #Responding to the ship being compromised (hit by an alien)
    def _ship_hit(self):
        if self.stats.ships_left > 0:
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            self.aliens.empty()
            self.bullets.empty()
            self._create_fleet()
            self.ship.center_ship()
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    #Check if aliens reach the bottom of the screen 
    def _check_aliens_bottom(self):
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                self._ship_hit()
                break
        
    # Update the screen
    def _update_screen(self):
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        self.sb.show_score()
        if not self.stats.game_active:
            self.play_button.draw_button()
        pygame.display.flip()
        
        
    #Responding to key presses 
    def _check_keydown_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
            
    #Responding to key releases 
    def _check_keyup_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
            
    #Create a new bullet and add it to the bullets group
    def _fire_bullet(self):
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

# Create an instance of the game and run it
if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()
