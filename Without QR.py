import pygame
import random
import time
import os
import sys
import string

# ================= CONFIGURABLE PART =================

# Path to your OTF font file
FONT_PATH = "TypeLightSans-KV84p.otf"

# Output text file where user inputs (free input and question answers) are appended
OUTPUT_FILE = "collected_input.txt"

# List of sentences to display in Waiting Mode
SENTENCES = [
    "Are you there?",
    "Type to me.",
    "What’s the first word that comes to your mind? Type it.",
    "Feel free to type anything!",
    "Try typing without thinking. What happens?",
    "What’s the last thing you typed today?"
]

# List of questions to ask in Question Mode (after free input)
QUESTIONS = [
    "What is your name?",
    "How are you feeling?",
    "Any comments?"
]

# Timing parameters (in seconds)
WAITING_MODE_SENTENCE_INTERVAL = 5  # seconds between sentences in Waiting Mode
INPUT_MODE_TIMEOUT = 2              # seconds with no input in free input phase before saving and transitioning
QUESTION_MODE_TIMEOUT = 2           # seconds with no input in Question Mode before recording answer and moving on
THANK_YOU_DURATION = 15              # seconds to display thank you screen

# ---------------- Custom Keyboard Remap ----------------
def random_custom_layout():
    keyboardLayout = {
        'q': '', 'w': '', 'e': '', 'r': '', 't': '', 'y': '', 'u': '', 'i': '', 'o': '', 'p': '',
        'a': '', 's': '', 'd': '', 'f': '', 'g': '', 'h': '', 'j': '', 'k': '', 'l': '',
        'z': '', 'x': '', 'c': '', 'v': '', 'b': '', 'n': '', 'm': ''
    }

    usedLetters = []
    for key in keyboardLayout.keys():
        # Choose a random letter from a-z that hasn't been used
        letter = random.choice(string.ascii_lowercase)
        while letter in usedLetters:
            letter = random.choice(string.ascii_lowercase)
        keyboardLayout[key] = letter
        usedLetters.append(letter)

    return keyboardLayout


# Remap only the alphabet keys as specified:
# Top row: QWERTYUIOP -> A B C D E F G H I J
# Home row: ASDFGHJKL -> K L M N O P Q R S
# Bottom row: ZXCVBNM -> T U V W X Y Z
# CUSTOM_LAYOUT = {
#     # Top row
#     'q': 'a', 'w': 'b', 'e': 'c', 'r': 'd', 't': 'e', 'y': 'f', 'u': 'g', 'i': 'h', 'o': 'i', 'p': 'j',
#     # Home row
#     'a': 'k', 's': 'l', 'd': 'm', 'f': 'n', 'g': 'o', 'h': 'p', 'j': 'q', 'k': 'r', 'l': 's',
#     # Bottom row
#     'z': 't', 'x': 'u', 'c': 'v', 'v': 'w', 'b': 'x', 'n': 'y', 'm': 'z'
# }

CUSTOM_LAYOUT = random_custom_layout()


# ================= PYGAME PROGRAM =================

def main():
    pygame.init()

    # Set up fullscreen display with black background
    info_object = pygame.display.Info()
    screen_width, screen_height = info_object.current_w, info_object.current_h
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    pygame.display.set_caption("### Fullscreen Text Display ###")

    # Create a clock to control the frame rate
    clock = pygame.time.Clock()

    # Load the provided OTF font for dynamic text (waiting, free input, questions)
    try:
        main_font = pygame.font.Font(FONT_PATH, 48)
    except Exception as e:
        print(f"Could not load font from {FONT_PATH}. Exiting.")
        pygame.quit()
        sys.exit()

    # Load the system font for the fixed prompt and Q&A text
    bottom_font = pygame.font.SysFont(None, 36)

    # Define text color and background color
    text_color = (255, 255, 255)  # white
    bg_color = (0, 0, 0)          # black

    # ================= STATE DEFINITIONS =================
    WAITING_MODE = "waiting"
    INPUT_MODE = "input_free"      # Free input phase (user types freely)
    QUESTION_MODE = "question"     # Answering prompted questions one at a time
    THANK_YOU_MODE = "thank_you"   # Thank you screen after finishing questions

    mode = WAITING_MODE

    # ---------------- Session Variables ----------------
    # Record the Q&A pairs for this session.
    session_q_and_a = []

    # ---------------- Waiting Mode Variables ----------------
    last_sentence_time = time.time()
    current_sentence = random.choice(SENTENCES)

    # ---------------- Input Mode (Free Input) Variables ----------------
    free_input_text = ""
    free_input_last_time = None
    base_sentence = ""

    # ---------------- Question Mode Variables ----------------
    question_index = 0
    question_input_text = ""
    question_last_time = None

    # ---------------- Thank You Mode Variable ----------------
    thank_you_start_time = None

    running = True
    while running:
        # ---------------- Event Handling ----------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                # Allow ESC key to quit at any time
                if event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    # Function to remap key based on custom layout.
                    def remap_key(char):
                        if char.lower() in CUSTOM_LAYOUT:
                            return CUSTOM_LAYOUT[char.lower()].upper() if char.isupper() else CUSTOM_LAYOUT[char.lower()]
                        return char

                    if mode == WAITING_MODE:
                        # On any key press in Waiting Mode, switch to free input mode.
                        mode = INPUT_MODE
                        free_input_text = ""
                        free_input_last_time = time.time()
                        base_sentence = current_sentence
                    elif mode == INPUT_MODE:
                        # In free input mode, capture characters (ignoring backspace)
                        if event.key == pygame.K_BACKSPACE:
                            pass  # No backspace allowed
                        else:
                            char = event.unicode
                            char = remap_key(char)
                            free_input_text += char
                            free_input_last_time = time.time()
                    elif mode == QUESTION_MODE:
                        # In question mode, capture input for the current question (ignoring backspace)
                        if event.key == pygame.K_BACKSPACE:
                            pass
                        else:
                            char = event.unicode
                            char = remap_key(char)
                            question_input_text += char
                            question_last_time = time.time()

        # ---------------- Clear Screen ----------------
        screen.fill(bg_color)

        # ---------------- Mode-specific Logic and Rendering ----------------
        if mode == WAITING_MODE:
            # Display a random sentence (centered) that changes every 5 seconds
            sentence_surface = main_font.render(current_sentence, True, text_color)
            sentence_rect = sentence_surface.get_rect(center=(screen_width // 2, screen_height // 2))
            screen.blit(sentence_surface, sentence_rect)

            if time.time() - last_sentence_time >= WAITING_MODE_SENTENCE_INTERVAL:
                current_sentence = random.choice(SENTENCES)
                last_sentence_time = time.time()

        elif mode == INPUT_MODE:
            # Display the base waiting sentence (above center)
            base_surface = main_font.render(base_sentence, True, text_color)
            base_rect = base_surface.get_rect(center=(screen_width // 2, screen_height // 2 - 75))
            screen.blit(base_surface, base_rect)

            # Display the extra line "Don't worry" below the base sentence
            worry_surface = main_font.render("Don't worry, the keyboard is weird, I know...", True, text_color)
            worry_rect = worry_surface.get_rect(center=(screen_width // 2, screen_height - 75))
            screen.blit(worry_surface, worry_rect)

            # Display the free input text (below the two lines)
            input_surface = main_font.render(free_input_text, True, text_color)
            input_rect = input_surface.get_rect(center=(screen_width // 2, screen_height // 2 + 50))
            screen.blit(input_surface, input_rect)

            if free_input_last_time and (time.time() - free_input_last_time >= INPUT_MODE_TIMEOUT):
                if free_input_text.strip() != "":
                    append_to_file(OUTPUT_FILE, free_input_text)
                mode = QUESTION_MODE
                question_index = 0
                question_input_text = ""
                question_last_time = time.time()

        elif mode == QUESTION_MODE:
            if question_index < len(QUESTIONS):
                current_question = QUESTIONS[question_index]
                # Display the current question (above center)
                question_surface = main_font.render(current_question, True, text_color)
                question_rect = question_surface.get_rect(center=(screen_width // 2, screen_height // 2 - 50))
                screen.blit(question_surface, question_rect)

                # Display the user's answer input (below the question)
                answer_surface = main_font.render(question_input_text, True, text_color)
                answer_rect = answer_surface.get_rect(center=(screen_width // 2, screen_height // 2 + 50))
                screen.blit(answer_surface, answer_rect)

                if question_last_time and (time.time() - question_last_time >= QUESTION_MODE_TIMEOUT):
                    if question_input_text.strip() != "":
                        append_to_file(OUTPUT_FILE, question_input_text)
                        session_q_and_a.append((current_question, question_input_text))
                        question_index += 1
                        question_input_text = ""
                        question_last_time = time.time()
            else:
                mode = THANK_YOU_MODE
                thank_you_start_time = time.time()

        elif mode == THANK_YOU_MODE:
            # Display a "thank you" message (above center)
            thank_you_surface = main_font.render("Thank you for talking with me", True, text_color)
            thank_you_rect = thank_you_surface.get_rect(center=(screen_width // 2, screen_height // 2 - 150))
            screen.blit(thank_you_surface, thank_you_rect)

            # Display the Q&A text using the system font for clarity
            qna_lines = []
            for q, a in session_q_and_a:
                qna_lines.append(q)
                qna_lines.append("Your input: " + a)
                qna_lines.append("")  # blank line for spacing

            y_text = screen_height // 2  # Starting vertical position for Q&A text
            for line in qna_lines:
                line_surface = bottom_font.render(line, True, text_color)
                line_rect = line_surface.get_rect(center=(screen_width // 2, y_text))
                screen.blit(line_surface, line_rect)
                y_text += line_surface.get_height() + 5

            # Countdown Timer
            remaining = int(THANK_YOU_DURATION - (time.time() - thank_you_start_time))
            if remaining > 1:
                countdown_text = f"Your session will end in {remaining} seconds"
            else:
                countdown_text = f"Your session will end in {remaining} second"
            countdown_surface = bottom_font.render(countdown_text, True, text_color)
            countdown_rect = countdown_surface.get_rect(center=(screen_width // 2, screen_height - 40))
            screen.blit(countdown_surface, countdown_rect)

            if time.time() - thank_you_start_time >= THANK_YOU_DURATION:
                mode = WAITING_MODE
                last_sentence_time = time.time()
                current_sentence = random.choice(SENTENCES)
                session_q_and_a = []

        # ---------------- Fixed Prompt at the Bottom ----------------
        '''
        if mode == WAITING_MODE:
            prompt_text = "WAITING_MODE"
        elif mode == INPUT_MODE:
            prompt_text = "INPUT_MODE"
        elif mode == QUESTION_MODE:
            prompt_text = "QUESTION_MODE"
        elif mode == THANK_YOU_MODE:
            prompt_text = "END SCREEN"
        prompt_surface = bottom_font.render(prompt_text, True, text_color)
        prompt_rect = prompt_surface.get_rect(midbottom=(screen_width // 2, screen_height - 10))
        screen.blit(prompt_surface, prompt_rect)
        '''

        pygame.display.flip()
        clock.tick(30)  # Limit to 30 FPS

    pygame.quit()


def append_to_file(filename, text):
    """
    Appends the given text to the specified file, followed by a newline.
    """
    with open(filename, "a", encoding="utf-8") as f:
        f.write(text + "\n")


if __name__ == "__main__":
    main()