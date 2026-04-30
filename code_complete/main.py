from settings import * 
from level import Level
from pytmx.util_pygame import load_pygame
from os.path import join
from support import * 
from data import Data
from debug import debug
from ui import UI
import json

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
		self.elapsed_time = 0
		self.final_time = 0
		self.player_name = ''
		self.ranking_path = join('data', 'ranking.json')
		self.ranking_entries = self.load_ranking()

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
		self.elapsed_time = 0
		self.final_time = 0
		self.player_name = ''
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
				self.final_time = self.elapsed_time
				self.player_name = ''
				self.game_state = 'name_entry'
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
		self.small_font = pygame.font.Font(join('graphics', 'ui', 'runescape_uf.ttf'), 28)
		self.title_font = pygame.font.Font(join('graphics', 'ui', 'runescape_uf.ttf'), 72)
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

	def load_ranking(self):
		try:
			with open(self.ranking_path, 'r', encoding = 'utf-8') as file:
				entries = json.load(file)
		except (FileNotFoundError, json.JSONDecodeError):
			return []

		valid_entries = []
		for entry in entries:
			if isinstance(entry, dict) and 'name' in entry and 'time' in entry:
				try:
					valid_entries.append({'name': str(entry['name']), 'time': float(entry['time'])})
				except (TypeError, ValueError):
					pass
		return sorted(valid_entries, key = lambda entry: entry['time'])

	def save_ranking(self):
		self.ranking_entries = sorted(self.ranking_entries, key = lambda entry: entry['time'])
		with open(self.ranking_path, 'w', encoding = 'utf-8') as file:
			json.dump(self.ranking_entries, file, indent = 2)

	def save_player_score(self):
		name = self.player_name.strip() or 'Jogador'
		self.ranking_entries.append({'name': name[:16], 'time': round(self.final_time, 2)})
		self.save_ranking()
		self.game_state = 'ranking'

	def format_time(self, seconds):
		minutes = int(seconds // 60)
		remaining_seconds = seconds % 60
		return f'{minutes:02}:{remaining_seconds:05.2f}'

	def check_game_over(self):
		if self.game_state == 'playing' and self.data.health <= 0:
			self.switch_stage('game_over')

	def handle_keydown(self, event):
		key = event.key

		if key == pygame.K_ESCAPE:
			self.quit_game()

		if key == pygame.K_r and self.game_state != 'name_entry':
			self.game_state = 'ranking'
			return

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

		elif self.game_state == 'name_entry':
			if key == pygame.K_RETURN:
				self.save_player_score()
			elif key == pygame.K_BACKSPACE:
				self.player_name = self.player_name[:-1]
			elif len(self.player_name) < 16 and getattr(event, 'unicode', '') and event.unicode.isprintable():
				self.player_name += event.unicode

		elif self.game_state in ('game_over', 'win'):
			if key == pygame.K_i:
				self.show_start_screen()
			if key == pygame.K_v:
				self.start_game()

		elif self.game_state == 'ranking':
			if key == pygame.K_i:
				self.show_start_screen()
			if key == pygame.K_v:
				self.start_game()

	def draw_text(self, text, font, color, pos, anchor = 'topleft'):
		surf = font.render(text, False, color)
		rect = surf.get_rect(**{anchor: pos})
		self.display_surface.blit(surf, rect)
		return rect

	def draw_name_entry_screen(self):
		self.display_surface.blit(self.screen_frames['win'], (0,0))
		panel_rect = pygame.Rect(250, 170, 780, 360)
		pygame.draw.rect(self.display_surface, '#111827', panel_rect, border_radius = 6)
		pygame.draw.rect(self.display_surface, '#f5f1de', panel_rect, 4, border_radius = 6)

		self.draw_text('VITORIA!', self.title_font, '#f5f1de', (WINDOW_WIDTH / 2, 220), 'center')
		self.draw_text(f'Tempo final: {self.format_time(self.final_time)}', self.font, '#f5f1de', (WINDOW_WIDTH / 2, 290), 'center')
		self.draw_text('Digite seu nome:', self.font, '#f5f1de', (WINDOW_WIDTH / 2, 355), 'center')

		input_rect = pygame.Rect(390, 385, 500, 58)
		pygame.draw.rect(self.display_surface, '#f5f1de', input_rect, border_radius = 4)
		pygame.draw.rect(self.display_surface, '#33323d', input_rect, 3, border_radius = 4)
		name_text = self.player_name if self.player_name else 'Jogador'
		self.draw_text(name_text, self.font, '#33323d', input_rect.center, 'center')

		self.draw_text('Enter - salvar no ranking', self.small_font, '#f5f1de', (WINDOW_WIDTH / 2, 475), 'center')
		self.draw_text('Backspace - apagar', self.small_font, '#f5f1de', (WINDOW_WIDTH / 2, 510), 'center')

	def draw_ranking_screen(self):
		self.display_surface.fill('#151925')
		self.draw_text('RANKING', self.title_font, '#f5f1de', (WINDOW_WIDTH / 2, 72), 'center')
		self.draw_text('Melhores tempos', self.font, '#f5f1de', (WINDOW_WIDTH / 2, 132), 'center')

		table_rect = pygame.Rect(250, 175, 780, 390)
		pygame.draw.rect(self.display_surface, '#20283a', table_rect, border_radius = 6)
		pygame.draw.rect(self.display_surface, '#f5f1de', table_rect, 3, border_radius = 6)

		if self.ranking_entries:
			self.draw_text('POS', self.small_font, '#f5f1de', (300, 210))
			self.draw_text('NOME', self.small_font, '#f5f1de', (420, 210))
			self.draw_text('TEMPO', self.small_font, '#f5f1de', (835, 210))

			for index, entry in enumerate(self.ranking_entries[:10], 1):
				y = 250 + (index - 1) * 30
				self.draw_text(f'{index:02}', self.small_font, '#f5f1de', (310, y))
				self.draw_text(entry['name'][:16], self.small_font, '#f5f1de', (420, y))
				self.draw_text(self.format_time(entry['time']), self.small_font, '#f5f1de', (835, y))
		else:
			self.draw_text('Nenhum tempo registrado ainda.', self.font, '#f5f1de', table_rect.center, 'center')

		self.draw_text('I - Tela Inicial   |   V - Reiniciar   |   Esc - Sair', self.small_font, '#f5f1de', (WINDOW_WIDTH / 2, 640), 'center')

	def draw_game_timer(self):
		timer_text = self.format_time(self.elapsed_time)
		text_surf = self.font.render(timer_text, False, '#f5f1de')
		text_rect = text_surf.get_rect(topright = (WINDOW_WIDTH - 18, 12))
		bg_rect = text_rect.inflate(22, 14)
		pygame.draw.rect(self.display_surface, '#33323d', bg_rect, border_radius = 4)
		pygame.draw.rect(self.display_surface, '#f5f1de', bg_rect, 2, border_radius = 4)
		self.display_surface.blit(text_surf, text_rect)

	def draw_current_state(self, dt):
		if self.game_state == 'playing':
			self.elapsed_time += dt
			self.current_stage.run(dt)
			if self.game_state == 'playing':
				self.ui.update(dt)
				self.draw_game_timer()
				return

		if self.game_state == 'level_intro':
			self.display_surface.blit(self.level_intro_frames[self.current_level_index], (0,0))
		elif self.game_state == 'name_entry':
			self.draw_name_entry_screen()
		elif self.game_state == 'ranking':
			self.draw_ranking_screen()
		else:
			self.display_surface.blit(self.screen_frames[self.game_state], (0,0))

	def run(self):
		while True:
			dt = self.clock.tick(60) / 1000
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.quit_game()
				if event.type == pygame.KEYDOWN:
					self.handle_keydown(event)

			self.check_game_over()
			self.draw_current_state(dt)
			
			pygame.display.update()

if __name__ == '__main__':
	game = Game()
	game.run()
