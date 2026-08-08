# gui_game.py
import pygame
import sys
import time
from constants import *
from components import Button
from agent import SudokuAgent
from generator import generate_sudoku
from config import DIFFICULTY_LEVELS
from utils import save_log


class SudokuGameApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("SUDOKU PRO AI")

        try:
            font_name = 'segoeui' if 'segoeui' in pygame.font.get_fonts() else 'arial'
            self.font_num = pygame.font.SysFont(font_name, 38, bold=True)
            self.font_ui = pygame.font.SysFont(font_name, 14, bold=True)
            self.font_msg = pygame.font.SysFont(font_name, 18, bold=False)
        except:
            self.font_num = pygame.font.SysFont('arial', 38, bold=True)
            self.font_ui = pygame.font.SysFont('arial', 14, bold=True)
            self.font_msg = pygame.font.SysFont('arial', 18, bold=False)

        self.start_x = (WIDTH - GRID_SIZE) // 2
        self.start_y = 50  # Khoảng cách vừa đủ đẹp từ đỉnh máy

        self.board = None
        self.original_board = None
        self.agent = SudokuAgent()

        self.running = True
        self.solving = False
        self.finished = False
        self.message = "SẴN SÀNG"
        self.current_diff_name = "DỄ"
        self.use_heuristic = True

        self.setup_ui()
        self.reset_game('1')

    def setup_ui(self):
        # Thiết kế lại cụm nút: Chia làm 2 bên trái - phải cân xứng
        btn_w, btn_h = 90, 35
        gap = 10
        y_btns = 720  # Đẩy cao lên để không sát mép 800

        # Nhóm bên trái: Chọn độ khó
        self.buttons = [
            Button(self.start_x, y_btns, btn_w, btn_h, "DỄ", self.font_ui, lambda: self.reset_game('1')),
            Button(self.start_x + btn_w + gap, y_btns, btn_w, btn_h, "VỪA", self.font_ui, lambda: self.reset_game('2')),
            Button(self.start_x + (btn_w + gap) * 2, y_btns, btn_w, btn_h, "KHÓ", self.font_ui,
                   lambda: self.reset_game('3')),

            # Nhóm bên phải: Điều khiển AI (Căn lề phải của grid)
            Button(self.start_x + GRID_SIZE - (btn_w * 3 + gap * 2), y_btns, btn_w, btn_h, "AI: BẬT", self.font_ui,
                   self.toggle_mode),
            Button(self.start_x + GRID_SIZE - (btn_w * 2 + gap), y_btns, btn_w, btn_h, "DỪNG", self.font_ui,
                   self.toggle_pause),
            Button(self.start_x + GRID_SIZE - btn_w, y_btns, btn_w, btn_h, "GIẢI", self.font_ui, self.start_agent)
        ]
        self.btn_mode = self.buttons[3]
        self.btn_pause = self.buttons[4]

    def toggle_pause(self):
        if self.solving:
            self.agent.is_paused = not self.agent.is_paused
            self.btn_pause.text = "TIẾP TỤC" if self.agent.is_paused else "DỪNG"
            self.message = "ĐÃ TẠM DỪNG" if self.agent.is_paused else "ĐANG GIẢI..."

    def toggle_mode(self):
        if self.solving: return
        self.use_heuristic = not self.use_heuristic
        self.btn_mode.text = "AI: BẬT" if self.use_heuristic else "AI: TẮT"
        self.message = "CHẾ ĐỘ: " + ("THÔNG MINH" if self.use_heuristic else "VÉT CẠN")

    def reset_game(self, level_key):
        if self.solving: return
        names = {'1': "DỄ", '2': "VỪA", '3': "KHÓ"}
        self.current_diff_name = names[level_key]
        self.message = f"LEVEL: {self.current_diff_name}"
        self.finished = False
        self.agent.steps_taken = 0
        self.board = generate_sudoku(DIFFICULTY_LEVELS[level_key])
        self.original_board = [row[:] for row in self.board]
        self.agent.is_paused = False
        self.btn_pause.text = "DỪNG"

    def start_agent(self):
        if self.solving or self.finished: return
        self.solving = True
        self.agent.is_paused = False
        self.btn_pause.text = "DỪNG"
        self.message = "AI ĐANG TƯ DUY..."

        start_t = time.time()
        success = self.agent.act_solve(self.board, visualizer_func=self.render, use_heuristic=self.use_heuristic)

        duration = round(time.time() - start_t, 2)
        self.solving = False
        if success:
            self.finished = True
            self.message = f"OK! {duration}s - {self.agent.steps_taken} STEPS"
        else:
            self.message = "KHÔNG CÓ ĐÁP ÁN!"

    def draw_grid(self):
        # Vẽ khung chính tinh tế hơn
        for i in range(10):
            thick = 3 if i % 3 == 0 else 1
            color = BLACK if i % 3 == 0 else GRAY
            pygame.draw.line(self.screen, color,
                             (self.start_x, self.start_y + i * CELL_SIZE),
                             (self.start_x + GRID_SIZE, self.start_y + i * CELL_SIZE), thick)
            pygame.draw.line(self.screen, color,
                             (self.start_x + i * CELL_SIZE, self.start_y),
                             (self.start_x + i * CELL_SIZE, self.start_y + GRID_SIZE), thick)

    def draw_numbers(self):
        for i in range(9):
            for j in range(9):
                val = self.board[i][j]
                if val != 0:
                    color = RED if self.original_board[i][j] != 0 else BLUE
                    text = self.font_num.render(str(val), True, color)
                    x = self.start_x + j * CELL_SIZE + (CELL_SIZE - text.get_width()) // 2
                    y = self.start_y + i * CELL_SIZE + (CELL_SIZE - text.get_height()) // 2
                    self.screen.blit(text, (x, y))

    def render(self, board=None, current_cell=None):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit();
                sys.exit()
            if self.solving:
                for btn in self.buttons:
                    if btn.text in ["DỪNG", "TIẾP TỤC"]: btn.handle_event(event)

        self.screen.fill(WHITE)

        if current_cell:
            r, c = current_cell
            # Vẽ highlight mỏng nhẹ hơn (chỉ ô hiện tại) thay vì cả hàng/cột để đỡ rối mắt
            hl_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            hl_surf.fill(HIGHLIGHT_COLOR)
            self.screen.blit(hl_surf, (self.start_x + c * CELL_SIZE, self.start_y + r * CELL_SIZE))

        self.draw_grid()
        self.draw_numbers()

        # Thanh Status Bar ở trên cùng (y=20)
        stt_color = GREEN if self.finished else (ORANGE if self.agent.is_paused else (200, 200, 220))
        msg_surf = self.font_msg.render(self.message, True, stt_color)
        self.screen.blit(msg_surf, (self.start_x, 20))

        for btn in self.buttons:
            btn.draw(self.screen)

        pygame.display.update()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                if not self.solving:
                    for btn in self.buttons: btn.handle_event(event)
            self.render()
        pygame.quit()


if __name__ == "__main__":
    app = SudokuGameApp()
    app.run()