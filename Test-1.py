import pygame
import random
import time
import sys

########################
# CONFIGURABLE SECTION #
########################

# Name of the font file and the output text file (all in the same folder)
FONT_FILE = "TypeLightSans-KV84p.otf"
OUTPUT_FILE = "collected_input.txt"

# Lists of sentences
WAITING_SENTENCES = [
    "This is a random waiting sentence 1.",
    "This is a random waiting sentence 2.",
    "We are waiting for your input...",
    "Type something to begin."
]

QUESTIONS = [
    "What is your name?",
    "How are you feeling today?",
    "What is your favorite color?"
]

# Timing constants (in seconds)
WAITING_MODE_SENTENCE_INTERVAL = 5  # cycle random waiting sentence every 5 seconds
INACTIVITY_LIMIT = 5                # if no input for 5s => save text / move on
THANK_YOU_DISPLAY_TIME = 5          # show 'thank you' message for 5 seconds

# Text sizes
WAITING_FONT_SIZE = 48
QUESTION_FONT_SIZE = 40
PROMPT_FONT_SIZE = 30

# Colors
BG_COLOR = (0, 0, 0)       # black background
TEXT_COLOR = (255, 255, 255)  # white text

######################
# STATE DEFINITIONS  #
######################

WAITING_MODE = "waiting"
INPUT_MODE = "input"

# Sub-states of INPUT_MODE
PHASE_CAPTURE_WAITING_SENTENCE = 0  # user typed something after waiting sentence
PHASE_QUESTION_PROMPT = 1          # user is answering the question list
PHASE_THANK_YOU = 2                # after last question, show thank you

def main():
    # Initialize pygame
    pygame.init()

    # Fullscreen setup
    display_info = pygame.display.Info()
    screen_width, screen_height = display_info.current_w, display_info.current_h
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    pygame.display.set_caption("Fullscreen Text")

    # Load the OTF font (main font)
    try:
        main_font_waiting = pygame.font.Font(FONT_FILE, WAITING_FONT_SIZE)
        main_font_question = pygame.font.Font(FONT_FILE, QUESTION_FONT_SIZE)
    except:
        print(f"Error: Could not load font '{FONT_FILE}'. Make sure it is in the same folder.")
        pygame.quit()
        sys.exit()

    # Standard font for the fixed prompt at the bottom
    bottom_font = pygame.font.SysFont(None, PROMPT_FONT_SIZE)

    # Clock to control frame rate
    clock = pygame.time.Clock()

    # Initial state
    mode = WAITING_MODE
    input_phase = PHASE_CAPTURE_WAITING_SENTENCE  # used only in INPUT_MODE
    current_waiting_sentence = random.choice(WAITING_SENTENCES)
    last_sentence_time = time.time()

    # For input capturing
    typed_text = ""
    last_input_time = None

    # For question list
    current_question_index = 0

    running = True
    while running:
        # ----------------------------------------
        # Handle events
        # ----------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # If ESC is pressed, optionally exit
                if event.key == pygame.K_ESCAPE:
                    # Exit the program gracefully
                    running = False
                else:
                    # No backspace at any time
                    if event.key != pygame.K_BACKSPACE:
                        # Convert the keystroke to a character and append
                        char = event.unicode
                        typed_text += char
                        last_input_time = time.time()

                    # If in WAITING_MODE, switch to INPUT_MODE on first key pressed
                    if mode == WAITING_MODE:
                        mode = INPUT_MODE
                        input_phase = PHASE_CAPTURE_WAITING_SENTENCE
                        # typed_text is now capturing user input after waiting sentence

        # ----------------------------------------
        # Update Logic
        # ----------------------------------------
        screen.fill(BG_COLOR)

        if mode == WAITING_MODE:
            # Display the current waiting-mode sentence
            sentence_surface = main_font_waiting.render(current_waiting_sentence, True, TEXT_COLOR)
            sentence_rect = sentence_surface.get_rect(center=(screen_width // 2, screen_height // 2))
            screen.blit(sentence_surface, sentence_rect)

            # Cycle to a new waiting sentence every WAITING_MODE_SENTENCE_INTERVAL seconds
            if time.time() - last_sentence_time >= WAITING_MODE_SENTENCE_INTERVAL:
                current_waiting_sentence = random.choice(WAITING_SENTENCES)
                last_sentence_time = time.time()

            # Prompt at the bottom
            prompt_str = "Press any key to start typing. (ESC to quit)"
            prompt_surface = bottom_font.render(prompt_str, True, TEXT_COLOR)
            prompt_rect = prompt_surface.get_rect(midbottom=(screen_width // 2, screen_height - 10))
            screen.blit(prompt_surface, prompt_rect)

        else:
            # mode == INPUT_MODE
            if input_phase == PHASE_CAPTURE_WAITING_SENTENCE:
                # Show the last waiting sentence on top
                waiting_surface = main_font_waiting.render(current_waiting_sentence, True, TEXT_COLOR)
                waiting_rect = waiting_surface.get_rect(center=(screen_width // 2, screen_height // 3))
                screen.blit(waiting_surface, waiting_rect)

                # Display the user-typed text below the waiting sentence
                typed_surface = main_font_waiting.render(typed_text, True, TEXT_COLOR)
                typed_rect = typed_surface.get_rect(center=(screen_width // 2, (screen_height // 3) + 100))
                screen.blit(typed_surface, typed_rect)

                # Prompt at the bottom
                prompt_str = "Type your response... (ESC to quit)"
                prompt_surface = bottom_font.render(prompt_str, True, TEXT_COLOR)
                prompt_rect = prompt_surface.get_rect(midbottom=(screen_width // 2, screen_height - 10))
                screen.blit(prompt_surface, prompt_rect)

                # Check inactivity (5 seconds)
                if typed_text and last_input_time is not None:
                    if time.time() - last_input_time >= INACTIVITY_LIMIT:
                        # Append typed text to file
                        append_to_file(OUTPUT_FILE, typed_text)
                        # Move to question list
                        typed_text = ""
                        input_phase = PHASE_QUESTION_PROMPT
                        current_question_index = 0
                        last_input_time = None

            elif input_phase == PHASE_QUESTION_PROMPT:
                # If we still have questions to ask
                if current_question_index < len(QUESTIONS):
                    question_text = QUESTIONS[current_question_index]
                    # Show the question
                    question_surface = main_font_question.render(question_text, True, TEXT_COLOR)
                    question_rect = question_surface.get_rect(center=(screen_width // 2, screen_height // 3))
                    screen.blit(question_surface, question_rect)

                    # Show typed text for the current answer
                    typed_surface = main_font_question.render(typed_text, True, TEXT_COLOR)
                    typed_rect = typed_surface.get_rect(center=(screen_width // 2, (screen_height // 3) + 70))
                    screen.blit(typed_surface, typed_rect)

                    # Bottom prompt
                    prompt_str = f"Question {current_question_index+1}/{len(QUESTIONS)}: Type your answer... (ESC to quit)"
                    prompt_surface = bottom_font.render(prompt_str, True, TEXT_COLOR)
                    prompt_rect = prompt_surface.get_rect(midbottom=(screen_width // 2, screen_height - 10))
                    screen.blit(prompt_surface, prompt_rect)

                    # Check inactivity
                    if typed_text and last_input_time is not None:
                        if time.time() - last_input_time >= INACTIVITY_LIMIT:
                            # Append typed answer to file
                            append_to_file(OUTPUT_FILE, typed_text)

                            # Move to next question
                            typed_text = ""
                            current_question_index += 1
                            last_input_time = None

                else:
                    # No more questions left -> show thank you message
                    input_phase = PHASE_THANK_YOU
                    last_input_time = time.time()  # reuse this as a timer for the thank you display
                    typed_text = ""

            elif input_phase == PHASE_THANK_YOU:
                # Show 'thank you' message for THANK_YOU_DISPLAY_TIME seconds
                thank_you_surface = main_font_question.render("Thank you!", True, TEXT_COLOR)
                thank_you_rect = thank_you_surface.get_rect(center=(screen_width // 2, screen_height // 2))
                screen.blit(thank_you_surface, thank_you_rect)

                if time.time() - last_input_time >= THANK_YOU_DISPLAY_TIME:
                    # Return to waiting mode
                    mode = WAITING_MODE
                    last_sentence_time = time.time()
                    current_waiting_sentence = random.choice(WAITING_SENTENCES)
                    typed_text = ""

        # ----------------------------------------
        # Refresh the display and tick
        # ----------------------------------------
        pygame.display.flip()
        clock.tick(30)

    # Clean up
    pygame.quit()

def append_to_file(filename, text):
    """
    Appends the given text to a file, each entry on its own line.
    """
    with open(filename, "a", encoding="utf-8") as f:
        f.write(text + "\n")

if __name__ == "__main__":
    main()