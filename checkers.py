import pygame
import sys
import random

pygame.init()

# Constants
WIDTH, HEIGHT = 650, 650
ROWS, COLS = 8, 8
SQUARE_SIZE = 650 // COLS

# Colors
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
BEIGE = (245, 245, 220)
HIGHLIGHT = (0, 255, 0)
BUTTON_BG = (70, 130, 180)
BUTTON_HOVER = (100, 160, 210)
BUTTON_BORDER_RADIUS = 25

# Board offset to center horizontally; vertical offset always 0 so board is at top
BOARD_OFFSET_X = (WIDTH - (SQUARE_SIZE * COLS)) // 2
BOARD_OFFSET_Y = 0

# Button positioning (overlay on board)
BUTTON_Y = 290
BUTTON_HEIGHT = 70
BUTTON_SPACING = 70

# Pygame setup
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Checkers")
font = pygame.font.SysFont(None, 40)

class Button:
    def __init__(self, x, y, w, h, text, color, hover_color):
        self.rect = pygame.Rect(x, y, 170, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color

    def draw(self, win):
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color

        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, (*color, 220), s.get_rect(), border_radius=BUTTON_BORDER_RADIUS)
        win.blit(s, (self.rect.x, self.rect.y))

        pygame.draw.rect(win, BLACK, self.rect, 2, border_radius=BUTTON_BORDER_RADIUS)

        txt_surface = font.render(self.text, True, BLACK)
        txt_rect = txt_surface.get_rect(center=self.rect.center)
        win.blit(txt_surface, txt_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def draw_board(win):
    for row in range(ROWS):
        for col in range(COLS):
            color = BEIGE if (row + col) % 2 == 0 else BROWN
            pygame.draw.rect(win, color, (BOARD_OFFSET_X + col * SQUARE_SIZE, BOARD_OFFSET_Y + row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces(win, board, selected=None):
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece:
                color = RED if piece in (1, 3) else WHITE
                is_king = piece in (3, 4)
                x = BOARD_OFFSET_X + col * SQUARE_SIZE + SQUARE_SIZE // 2
                y = BOARD_OFFSET_Y + row * SQUARE_SIZE + SQUARE_SIZE // 2
                radius = SQUARE_SIZE // 2 - 10
                pygame.draw.circle(win, BLACK, (x, y), radius + 2)
                pygame.draw.circle(win, color, (x, y), radius)
                if is_king:
                    crown_text = font.render("K", True, (255, 215, 0))
                    win.blit(crown_text, crown_text.get_rect(center=(x, y)))
    if selected:
        row, col = selected
        pygame.draw.rect(win, HIGHLIGHT, (BOARD_OFFSET_X + col * SQUARE_SIZE, BOARD_OFFSET_Y + row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 4)

def create_board():
    board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    for row in range(ROWS):
        for col in range(COLS):
            if (row + col) % 2 != 0:
                if row < 3:
                    board[row][col] = 1
                elif row > 4:
                    board[row][col] = 2
    return board

def get_row_col_from_mouse(pos):
    x, y = pos
    x -= BOARD_OFFSET_X
    y -= BOARD_OFFSET_Y
    if x < 0 or y < 0:
        return None
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    if 0 <= row < ROWS and 0 <= col < COLS:
        return row, col
    return None

def explore_captures(board, row, col, piece, path=None, captured=None):
    if path is None:
        path = [(row, col)]
    if captured is None:
        captured = []

    directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # all diagonals
    enemy = {1: (2, 4), 2: (1, 3), 3: (2, 4), 4: (1, 3)}[piece]

    longest_paths = []
    max_length = 0

    for dr, dc in directions:
        r, c = row, col

        if piece in (3, 4):  # King: can move multiple steps diagonally, like bishop
                        r1, c1 = row + dr, col + dc
                        while 0 <= r1 < ROWS and 0 <= c1 < COLS:
                            if board[r1][c1] == 0:
                                r1 += dr
                                c1 += dc
                                continue  # Empty square, keep searching
                            elif board[r1][c1] in enemy:
                                r2, c2 = r1 + dr, c1 + dc
                                while 0 <= r2 < ROWS and 0 <= c2 < COLS and board[r2][c2] == 0:
                                    new_board = [r.copy() for r in board]
                                    new_board[row][col] = 0
                                    new_board[r1][c1] = 0
                                    new_board[r2][c2] = piece
                                    sub_paths = explore_captures(new_board, r2, c2, piece, path + [(r2, c2)], captured + [(r1, c1)])
                                    for p, cpts in sub_paths:
                                        if len(cpts) > max_length:
                                            longest_paths = [(p, cpts)]
                                            max_length = len(cpts)
                                        elif len(cpts) == max_length:
                                            longest_paths.append((p, cpts))
                                    r2 += dr
                                    c2 += dc
                                break  # only one piece can be captured in a direction per jump
                            else:
                                break  # blocked by own piece or other obstacle


        else:
            # Regular piece: only jump 2 steps diagonally
            r1, c1 = row + dr, col + dc
            r2, c2 = row + 2 * dr, col + 2 * dc
            if 0 <= r2 < ROWS and 0 <= c2 < COLS:
                if board[r1][c1] in enemy and board[r2][c2] == 0:
                    new_board = [row.copy() for row in board]
                    new_board[row][col] = 0
                    new_board[r1][c1] = 0
                    new_board[r2][c2] = piece
                    sub_paths = explore_captures(new_board, r2, c2, piece, path + [(r2, c2)], captured + [(r1, c1)])

                    for p, cpts in sub_paths:
                        if len(cpts) > max_length:
                            longest_paths = [(p, cpts)]
                            max_length = len(cpts)
                        elif len(cpts) == max_length:
                            longest_paths.append((p, cpts))

    if not longest_paths:
        return [(path, captured)]
    return longest_paths


def valid_moves(board, row, col):
    piece = board[row][col]
    if not piece:
        return {}

    all_moves = {}

    # 1. Explore captures first (for kings and normal pieces)
    captures = explore_captures(board, row, col, piece, path=[(row, col)], captured=[])
    max_capture_len = 0

    for path, captured in captures:
        capture_len = len(captured)
        if capture_len > max_capture_len:
            max_capture_len = capture_len
            all_moves = {path[-1]: captured}
        elif capture_len == max_capture_len and capture_len > 0:
            all_moves[path[-1]] = captured

    # Filter only max-length captures if any
    if max_capture_len > 0:
        all_moves = {move: caps for move, caps in all_moves.items() if len(caps) == max_capture_len}
        return all_moves


    # 2. No captures found, generate normal moves
    directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

    if piece in (3, 4):  # King: can slide freely diagonally
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < ROWS and 0 <= c < COLS:
                if board[r][c] == 0:
                    all_moves[(r, c)] = []
                else:
                    break
                r += dr
                c += dc
    else:
        # Normal pieces move one step diagonally forward only
        forward_dirs = [(-1, -1), (-1, 1)] if piece == 2 else [(1, -1), (1, 1)]
        for dr, dc in forward_dirs:
            r, c = row + dr, col + dc
            if 0 <= r < ROWS and 0 <= c < COLS and board[r][c] == 0:
                all_moves[(r, c)] = []

    return all_moves


def move(board, from_row, from_col, to_row, to_col, captured_positions):
    piece = board[from_row][from_col]
    board[from_row][from_col] = 0
    board[to_row][to_col] = piece

    for r, c in captured_positions:
        board[r][c] = 0

    king_if_needed(board, to_row, to_col)


def any_capture_available(board, player):
    player_pieces = [player, player + 2]
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] in player_pieces:
                for cap in valid_moves(board, r, c).values():
                    if cap:
                        return True
    return False

def king_if_needed(board, row, col):
    if board[row][col] == 1 and row == ROWS - 1:
        board[row][col] = 3
    elif board[row][col] == 2 and row == 0:
        board[row][col] = 4

def get_king_captures(board, r, c):
    captures = []
    directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # all diagonal directions
    n = len(board)
    piece = board[r][c]
    enemy = {3: (1, 2), 4: (1, 2)}[piece]

    for dr, dc in directions:
        found_opponent = False
        opponent_pos = None
        row, col = r + dr, c + dc

        while 0 <= row < n and 0 <= col < n:
            cell = board[row][col]
            if cell == 0:
                if found_opponent:
                    captures.append({
                        'start': (r, c),
                        'captured': [opponent_pos],
                        'end': (row, col)
                    })
                    break
            elif cell in enemy:
                if found_opponent:
                    break  # Cannot capture more than one piece in a straight line without landing
                found_opponent = True
                opponent_pos = (row, col)
            else:
                break  # Blocked by own piece or invalid
            row += dr
            col += dc

    return captures

def get_king_moves(self, piece):
    moves = {}
    directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # 4 diagonal directions
    row, col = piece.row, piece.col

    for dr, dc in directions:
        r, c = row + dr, col + dc
        has_captured = False
        skipped = []

        while 0 <= r < 8 and 0 <= c < 8:
            current = self.board[r][c]

            if current == 0:
                if has_captured:
                    moves[(r, c)] = skipped
                r += dr
                c += dc

            elif current.color != piece.color:
                if not has_captured:
                    skipped = [current]
                    has_captured = True
                    r += dr
                    c += dc
                else:
                    break  # can't capture two in one direction

            else:
                break  # blocked by same color

    return moves

def get_piece_captures(board, row, col, piece, enemy):
    captures = []  # Will hold tuples of landing squares where captures happen

    directions = []
    if piece in (1, 2):  # Normal pawn: define directions
        # Example: black pawns move down, white pawns move up
        directions = [(-1, -1), (-1, 1)] if piece == 1 else [(1, -1), (1, 1)]
    elif piece in (3, 4):  # King: moves diagonally any distance
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

    for dr, dc in directions:
        r, c = row + dr, col + dc

        if piece in (1, 2):  # Normal pawn capture check
            # Check adjacent diagonal for enemy and next diagonal for empty
            r2, c2 = row + 2*dr, col + 2*dc
            if 0 <= r < ROWS and 0 <= c < COLS and board[r][c] in enemy:
                if 0 <= r2 < ROWS and 0 <= c2 < COLS and board[r2][c2] == 0:
                    captures.append((r2, c2))

        elif piece in (3, 4):  # King capture (multi-step)
            # Move along diagonal until enemy found, then check next for empty
            steps = 1
            while True:
                r = row + dr*steps
                c = col + dc*steps
                if not (0 <= r < ROWS and 0 <= c < COLS):
                    break
                if board[r][c] == 0:
                    steps += 1
                    continue
                elif board[r][c] in enemy:
                    r2 = r + dr
                    c2 = c + dc
                    if 0 <= r2 < ROWS and 0 <= c2 < COLS and board[r2][c2] == 0:
                        captures.append((r2, c2))
                    break
                else:
                    break
    return captures


def main():
    board = create_board()
    selected = None
    valid_move_positions = {}
    turn = None
    start_message = ""
    game_started = False
    game_over = False
    winner = None
    clock = pygame.time.Clock()

    button_width = 140
    button_start_x = (WIDTH - (button_width * 3 + BUTTON_SPACING * 2)) // 2
    buttons = [
        Button(button_start_x, BUTTON_Y, button_width, BUTTON_HEIGHT, "Red First", (255, 0, 0), (179, 1, 1)),
        Button(button_start_x + button_width + BUTTON_SPACING, BUTTON_Y, button_width, BUTTON_HEIGHT, "White First", (218, 218, 218), (169, 169, 169)),
        Button(button_start_x + 2 * (button_width + BUTTON_SPACING), BUTTON_Y, button_width, BUTTON_HEIGHT, "Random", (78, 255, 70), (34, 139, 34)),
    ]

    def check_game_over():
        for player in (1, 2):
            pieces = [(r, c) for r in range(ROWS) for c in range(COLS) if board[r][c] in (player, player + 2)]
            if not pieces:
                return 2 if player == 1 else 1
            moves_exist = any(valid_moves(board, r, c) for r, c in pieces)
            if not moves_exist:
                return 2 if player == 1 else 1
        return None

    run = True
    while run:
        clock.tick(60)
        WIN.fill(BEIGE)
        draw_board(WIN)
        draw_pieces(WIN, board, selected)

        for (r, c) in valid_move_positions:
            pygame.draw.rect(WIN, (0, 255, 255), (BOARD_OFFSET_X + c * SQUARE_SIZE, BOARD_OFFSET_Y + r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

        if not game_started:
            for btn in buttons:
                btn.draw(WIN)
        if start_message:
            msg_surface = font.render(start_message, True, BLACK)
            WIN.blit(msg_surface, (WIDTH // 2 - msg_surface.get_width() // 2, BUTTON_Y - 40))
        else:
            if game_over:
                msg = f"Game Over! {'Red' if winner == 1 else 'White'} wins!"
                text_surface = font.render(msg, True, BLACK)
                WIN.blit(text_surface, text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

                if not game_started:
                    # Check which start button clicked
                    for idx, btn in enumerate(buttons):
                        if btn.is_clicked(pos):
                            if idx == 0:
                                turn = 1
                            elif idx == 1:
                                turn = 2
                            else:
                                turn = random.choice([1, 2])
                                start_message = "Red starts first!" if turn == 1 else "White starts first!"
                            game_started = True
                            selected = None
                            valid_move_positions = {}
                            game_over = False
                            winner = None
                            board = create_board()
                            break
                else:
                    # Clear start_message on first player interaction
                    if start_message:
                        start_message = ""

                    if game_over:
                        continue  # Ignore clicks after game ended

                    clicked = get_row_col_from_mouse(pos)
                    if clicked:
                        r, c = clicked
                        piece = board[r][c]


                        # If selecting own piece
                        if selected is None:
                            if piece in (turn, turn + 2):
                                # Enforce mandatory capture
                                player_pieces = [(rr, cc) for rr in range(ROWS) for cc in range(COLS) if board[rr][cc] in (turn, turn + 2)]
                                capture_available = any(any(valid_moves(board, rr, cc)[dest] for dest in valid_moves(board, rr, cc)) for rr, cc in player_pieces)
                                moves = valid_moves(board, r, c)
                                if capture_available:
                                    moves = {k: v for k, v in moves.items() if v}  # filter only capturing moves
                                if moves:
                                    selected = (r, c)
                                    valid_move_positions = moves
                                else:
                                    selected = None
                                    valid_move_positions = {}

                        else:
                            # Move attempt if clicking on valid move square
                            if (r, c) in valid_move_positions:
                                captured = valid_move_positions[(r, c)]
                                move(board, selected[0], selected[1], r, c, captured)

                                # Check for additional jumps if capture happened
                                if captured:
                                    new_captures = valid_moves(board, r, c)
                                    # Filter to only capturing moves
                                    new_captures = {k: v for k, v in new_captures.items() if v}
                                    if new_captures:
                                        selected = (r, c)
                                        valid_move_positions = new_captures
                                    else:
                                        # End turn
                                        turn = 2 if turn == 1 else 1
                                        selected = None
                                        valid_move_positions = {}
                                else:
                                    # No capture move, end turn
                                    turn = 2 if turn == 1 else 1
                                    selected = None
                                    valid_move_positions = {}

                                # Check game over after move
                                winner = check_game_over()
                                if winner:
                                    game_over = True

                            else:
                                # Clicking on another piece resets selection
                                if piece in (turn, turn + 2):
                                    moves = valid_moves(board, r, c)
                                    player_pieces = [(rr, cc) for rr in range(ROWS) for cc in range(COLS) if board[rr][cc] in (turn, turn + 2)]
                                    capture_available = any(any(valid_moves(board, rr, cc)[dest] for dest in valid_moves(board, rr, cc)) for rr, cc in player_pieces)
                                    if capture_available:
                                        moves = {k: v for k, v in moves.items() if v}
                                    if moves:
                                        selected = (r, c)
                                        valid_move_positions = moves
                                    else:
                                        selected = None
                                        valid_move_positions = {}
                                else:
                                    selected = None
                                    valid_move_positions = {}

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
