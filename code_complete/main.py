from settings import * 
from level import Level
from pytmx.util_pygame import load_pygame
from os.path import join
from support import * 
from data import Data
from debug import debug
from ui import UI

class Game:
	def __init__(self):
		pygame.init()
		self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
		pygame.display.set_caption('Super Pirate World')
		self.clock = pygame.time.Clock()
		self.import_assets()
		self.bg_music.play(-1)

		self.tmx_maps = {
			0: load_pygame(join('data', 'levels', 'omni.tmx')),
			1: load_pygame(join('data', 'levels', '1.tmx')),
			2: load_pygame(join('data', 'levels', '2.tmx')),
			}
		self.level_sequence = [1,2,0]
		self.current_level_index = 0
		self.game_state = 'start'
		self.ui = None
		self.data = None
		self.current_stage = None

	def prepare_screen(self, surface):
		if surface.get_size() != (WINDOW_WIDTH, WINDOW_HEIGHT):
			surface = pygame.transform.smoothscale(surface, (WINDOW_WIDTH, WINDOW_HEIGHT))
		return surface.convert()

	def start_game(self):
		self.ui = UI(self.font, self.ui_frames)
		self.data = Data(self.ui)
		self.current_level_index = 0
		self.data.current_level = self.level_sequence[self.current_level_index]
		self.current_stage = None
		self.game_state = 'level_intro'

	def start_current_level(self):
		self.current_stage = Level(self.tmx_maps[self.data.current_level], self.level_frames, self.audio_files, self.data, self.switch_stage)
		self.game_state = 'playing'

	def show_start_screen(self):
		self.game_state = 'start'
		self.ui = None
		self.data = None
		self.current_stage = None

	def quit_game(self):
		pygame.quit()
		sys.exit()

	def switch_stage(self, target, unlock = 0):
		if target == 'level_complete':
			self.current_level_index += 1
			if self.current_level_index >= len(self.level_sequence):
				self.game_state = 'win'
				self.current_stage = None
			else:
				self.data.health += 2
				self.data.current_level = self.level_sequence[self.current_level_index]
				self.current_stage = None
				self.game_state = 'level_intro'

		if target == 'game_over':
			self.game_state = 'game_over'
			self.current_stage = None

	def import_assets(self):
		self.level_frames = {
			'flag': import_folder('graphics', 'level', 'flag'),
			'saw': import_folder('graphics', 'enemies', 'saw', 'animation'),
			'floor_spike': import_folder('graphics','enemies', 'floor_spikes'),
			'palms': import_sub_folders('graphics', 'level', 'palms'),
			'candle': import_folder('graphics','level', 'candle'),
			'window': import_folder('graphics','level', 'window'),
			'big_chain': import_folder('graphics','level', 'big_chains'),
			'small_chain': import_folder('graphics','level', 'small_chains'),
			'candle_light': import_folder('graphics','level', 'candle light'),
			'player': import_sub_folders('graphics','player'),
			'saw': import_folder('graphics', 'enemies', 'saw', 'animation'),
			'saw_chain': import_image('graphics', 'enemies', 'saw', 'saw_chain'),
			'helicopter': import_folder('graphics', 'level', 'helicopter'),
			'boat': import_folder('graphics', 'objects', 'boat'),
			'spike': import_image('graphics', 'enemies', 'spike_ball', 'Spiked Ball'),
			'spike_chain': import_image('graphics', 'enemies', 'spike_ball', 'spiked_chain'),
			'tooth': import_folder('graphics','enemies', 'tooth', 'run'),
			'shell': import_sub_folders('graphics','enemies', 'shell'),
			'pearl': import_image('graphics', 'enemies', 'bullets', 'pearl'),
			'items': import_sub_folders('graphics', 'items'),
			'particle': import_folder('graphics', 'effects', 'particle'),
			'water_top': import_folder('graphics', 'level', 'water', 'top'),
			'water_body': import_image('graphics', 'level', 'water', 'body'),
			'bg_tiles': import_folder_dict('graphics', 'level', 'bg', 'tiles'),
			'cloud_small': import_folder('graphics','level', 'clouds', 'small'),
			'cloud_large': import_image('graphics','level', 'clouds', 'large_cloud'),
		}
		self.font = pygame.font.Font(join('graphics', 'ui', 'runescape_uf.ttf'), 40)
		self.ui_frames = {
			'heart': import_folder('graphics', 'ui', 'heart'), 
			'coin':import_image('graphics', 'ui', 'coin')
		}
		self.screen_frames = {
			'start': self.prepare_screen(import_image('img', 'tela_inicio')),
			'instructions': self.prepare_screen(import_image('img', 'tela_instrucoes')),
			'game_over': self.prepare_screen(import_image('img', 'tela_game_over')),
			'win': self.prepare_screen(import_image('img', 'tela_win')),
		}
		self.level_intro_frames = [
			self.prepare_screen(import_image('img', 'fase_01')),
			self.prepare_screen(import_image('img', 'fase_02')),
			self.prepare_screen(import_image('img', 'fase_03')),
		]

		self.audio_files = {
			'coin': pygame.mixer.Sound(join('audio', 'coin.wav')),
			'attack': pygame.mixer.Sound(join('audio', 'attack.wav')),
			'jump': pygame.mixer.Sound(join('audio', 'jump.wav')), 
			'damage': pygame.mixer.Sound(join('audio', 'damage.wav')),
			'pearl': pygame.mixer.Sound(join('audio', 'pearl.wav')),
		}
		self.bg_music = pygame.mixer.Sound(join('audio', 'starlight_city.mp3'))
		self.bg_music.set_volume(0.5)

	def check_game_over(self):
		if self.game_state == 'playing' and self.data.health <= 0:
			self.switch_stage('game_over')

	def handle_keydown(self, key):
		if key == pygame.K_ESCAPE:
			self.quit_game()

		if self.game_state == 'start':
			if key == pygame.K_SPACE:
				self.start_game()
			if key == pygame.K_h:
				self.game_state = 'instructions'

		elif self.game_state == 'instructions':
			if key == pygame.K_i:
				self.show_start_screen()

		elif self.game_state == 'level_intro':
			if key == pygame.K_SPACE:
				self.start_current_level()

		elif self.game_state in ('game_over', 'win'):
			if key == pygame.K_i:
				self.show_start_screen()
			if key == pygame.K_v:
				self.start_game()

	def draw_current_state(self, dt):
		if self.game_state == 'playing':
			self.current_stage.run(dt)
			if self.game_state == 'playing':
				self.ui.update(dt)
				return

		if self.game_state == 'level_intro':
			self.display_surface.blit(self.level_intro_frames[self.current_level_index], (0,0))
		else:
			self.display_surface.blit(self.screen_frames[self.game_state], (0,0))

	def run(self):
		while True:
			dt = self.clock.tick(60) / 1000
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.quit_game()
				if event.type == pygame.KEYDOWN:
					self.handle_keydown(event.key)

			self.check_game_over()
			self.draw_current_state(dt)
			
			pygame.display.update()

if __name__ == '__main__':
	game = Game()
	game.run()
