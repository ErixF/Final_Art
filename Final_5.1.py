import pygame
import random
import time
import os
import sys
import string

# ================= CONFIGURABLE PART =================

# Path to your OTF font file
FONT_PATH = "bulletin.regular.ttf"

# List of sentences to display in Waiting Mode
SENTENCES = [
    "Are you there? Tell me your name.",
    "Type to me.",
    "Type your name so we can get started.",
    "C'mon, tell me your name. Just type.",
    "Don't think too much. Just type your name.",
    "Go ahead, type your name.",
]

# List of questions to ask in Question Mode
QUESTIONS = [
    "Wait… that doesn’t look right. Try again.",
    "Did you make the mistake? Or did I?",
    "Maybe try again? Slower this time, I promise I’m listening.",
    "Do you think I care about your answers?",
    "Do you believe these errors are genuine mistakes?",
    "Do you trust me?",
    "Have you ever trusted a machine completely?",
    "Am I smarter than you?",
    "Do you have think I have something to hide?",
    "Do you have something to hide?",
    "Are you comfortable if I ask something more personal?",
    "Would you mind if I listen when you're not speaking to me?",
    "Fine. Do you remember what you've told me today?",
    "Tell me one thing you hope I’ll remember about you.",
]

# Timing parameters (in seconds)
WAITING_MODE_SENTENCE_INTERVAL = 2  # seconds between sentences in Waiting Mode
INPUT_MODE_TIMEOUT = 3  # seconds with no input in free input phase before saving and transitioning
QUESTION_MODE_TIMEOUT = 3  # seconds with no input in Question Mode before recording answer and moving on
THANK_YOU_DURATION = 10  # seconds to display thank you screen

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

    screen = pygame.display.set_mode((1980, 1020))

    # Set up fullscreen display with black background
    info_object = pygame.display.Info()
    screen_width, screen_height = info_object.current_w, info_object.current_h
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    pygame.display.set_caption("### Fullscreen Text Display ###")

    # Create a clock to control the frame rate
    clock = pygame.time.Clock()

    # Load the provided OTF font for all dynamic text (waiting, free input, questions)
    try:
        main_font = pygame.font.Font(FONT_PATH, 46)
        question_font = pygame.font.Font(FONT_PATH, 50)
        waiting_font = pygame.font.Font(FONT_PATH, 60)
    except Exception as e:
        print(f"Could not load font from {FONT_PATH}. Exiting.")
        pygame.quit()
        sys.exit()

    # Load the system font for the fixed prompt at the bottom
    bottom_font = pygame.font.SysFont(None, 36)
    recap_font = pygame.font.SysFont(None, 24)

    # Define text color and background color
    text_color = (255, 255, 255)  # white
    bg_color = (0, 0, 0)  # black

    # ================= STATE DEFINITIONS =================
    WAITING_MODE = "waiting"
    INPUT_MODE = "input_free"  # Free input phase (user types freely)
    QUESTION_MODE = "question"  # Answering prompted questions one at a time
    THANK_YOU_MODE = "thank_you"  # Thank you screen after finishing questions

    mode = WAITING_MODE

    # ---------------- Session Variables ----------------
    # Record the Q&A pairs for this session.
    #session_q_and_a = []

    # ---------------- Waiting Mode Variables ----------------
    last_sentence_time = time.time()
    current_sentence = random.choice(SENTENCES)

    # ---------------- Input Mode (Free Input) Variables ----------------
    free_input_text = ""  # Stores the free input from the user
    free_input_last_time = None  # Time of last key press in free input mode
    # Save the sentence that was displayed in waiting mode when transitioning to free input
    base_sentence = ""

    # ---------------- Question Mode Variables ----------------
    question_index = 0  # Tracks which question is currently being asked
    question_input_text = ""  # Stores the answer for the current question
    question_last_time = None  # Time of last key press in question mode

    # ---------------- Thank You Mode Variable ----------------
    thank_you_start_time = None
    qr_surface = None  # Will hold the generated QR code as a pygame surface

    running = True
    while running:
        # ---------------- Event Handling ----------------
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running = False

            if event.type==pygame.KEYDOWN:
                # Allow CTRL+C and ESC key to quit at any time
                keys = pygame.key.get_pressed()
                #!!!!! REMEMBER TO REMOVE ESC BEFORE PUTTING INTO PRODUCTION !!!!!
                ########## if (keys[pygame.K_c] and (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL])) or keys[pygame.K_ESCAPE]:
                if keys[pygame.K_c] and keys[pygame.K_LCTRL]: ############### CHANGE KEY ###################
                    running = False
                else:
                    # Function to remap key based on custom layout.
                    def remap_key(char):
                        if char.lower() in CUSTOM_LAYOUT:
                            # Preserve case of the original character.
                            return CUSTOM_LAYOUT[char.lower()].upper() if char.isupper() else CUSTOM_LAYOUT[
                                char.lower()]
                        return char

                    if mode==WAITING_MODE:
                        # On any key press in Waiting Mode, switch to free input mode.
                        mode = INPUT_MODE
                        free_input_text = ""
                        free_input_last_time = time.time()
                        # Retain the waiting sentence that was visible.
                        base_sentence = current_sentence
                    elif mode==INPUT_MODE:
                        # In free input mode, capture characters (ignoring backspace)
                        if event.key in (pygame.K_TAB, pygame.K_DELETE, pygame.K_ESCAPE, pygame.K_BACKSPACE):
                            pass
                        # elif event.key==pygame.K_BACKSPACE:
                            # pass  # No backspace allowed
                        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                            # If Enter is pressed, immediately transition to Question Mode
                            mode = QUESTION_MODE
                            question_index = 0
                            question_input_text = ""
                            question_last_time = time.time()
                        else:
                            char = event.unicode
                            # Remap the character if it's an alphabet letter per custom layout
                            char = remap_key(char)
                            free_input_text += char
                            free_input_last_time = time.time()
                    elif mode==QUESTION_MODE:
                        # In question mode, capture input for the current question (ignoring backspace)
                        if event.key in (pygame.K_TAB, pygame.K_DELETE, pygame.K_ESCAPE, pygame.K_BACKSPACE):
                            pass
                        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                            # If Enter is pressed, immediately move to the next question
                            question_index += 1  # Move to next question
                            question_input_text = ""
                            question_last_time = time.time()
                        else:
                            char = event.unicode
                            # For all but the last question, remap the character; for the last question, use it as-is.
                            if question_index != len(QUESTIONS) - 1:
                                char = remap_key(char)
                            question_input_text += char
                            question_last_time = time.time()

        # ---------------- Clear Screen ----------------
        screen.fill(bg_color)

        # ---------------- Mode-specific Logic and Rendering ----------------
        if mode==WAITING_MODE:
            # Display a random sentence (centered) that changes every 5 seconds
            sentence_surface = waiting_font.render(current_sentence, True, text_color)
            sentence_rect = sentence_surface.get_rect(center=(screen_width // 2, screen_height // 2))
            screen.blit(sentence_surface, sentence_rect)

            # Update sentence if the interval has passed
            if time.time() - last_sentence_time >= WAITING_MODE_SENTENCE_INTERVAL:
                current_sentence = random.choice(SENTENCES)
                last_sentence_time = time.time()

        elif mode==INPUT_MODE:
            # ---------------- Updated Input Mode Display ----------------
            # Display the base waiting sentence (positioned above center)
            base_surface = main_font.render(base_sentence, True, text_color)
            base_rect = base_surface.get_rect(center=(screen_width // 2, screen_height // 2 - 75))
            screen.blit(base_surface, base_rect)

            # Display the extra line "Don't worry" below the base sentence
            #worry_surface = main_font.render("Don't worry", True, text_color)
            #worry_rect = worry_surface.get_rect(center=(screen_width // 2, screen_height - 75))
            #screen.blit(worry_surface, worry_rect)

            # Display the free input text (positioned below the two lines)
            input_surface = main_font.render(free_input_text, True, text_color)
            input_rect = input_surface.get_rect(center=(screen_width // 2, screen_height // 2 + 50))
            screen.blit(input_surface, input_rect)

            # If no input for INPUT_MODE_TIMEOUT seconds, record the free input and transition to Question Mode
            if free_input_last_time and (time.time() - free_input_last_time >= INPUT_MODE_TIMEOUT):
                #if free_input_text.strip()!="":
                    #append_to_file(OUTPUT_FILE, free_input_text)
                # Transition to Question Mode
                mode = QUESTION_MODE
                question_index = 0
                question_input_text = ""
                question_last_time = time.time()

        elif mode==QUESTION_MODE:
            # Check if there are still questions to ask
            if question_index < len(QUESTIONS):
                current_question = QUESTIONS[question_index]
                question_color = text_color
                # Use 1-indexing for displaying question number:
                #if (question_index + 1) in (3, 7, 8):
                    #question_color = (105, 171, 115)  # RGB(51,153,51)
                #else:
                    #question_color = text_color
                # Display the current question (positioned above center)
                question_surface = question_font.render(current_question, True, question_color)
                question_rect = question_surface.get_rect(center=(screen_width // 2, screen_height // 2 - 50))
                screen.blit(question_surface, question_rect)

                # Display the user's answer input (positioned below the question)
                answer_surface = question_font.render(question_input_text, True, text_color)
                answer_rect = answer_surface.get_rect(center=(screen_width // 2, screen_height // 2 + 50))
                screen.blit(answer_surface, answer_rect)

                # If no input for QUESTION_MODE_TIMEOUT seconds and some text has been entered,
                # record the answer and move on to the next question.
                #if question_last_time and (time.time() - question_last_time >= QUESTION_MODE_TIMEOUT):
                    #if question_input_text.strip()!="":
                        ##append_to_file(OUTPUT_FILE, question_input_text)
                        ## Record the Q&A pair for this session.
                        ##session_q_and_a.append((current_question, question_input_text))
                        #question_index += 1  # Move to next question
                        #question_input_text = ""
                        #question_last_time = time.time()
                    ## If no text has been entered, wait (do not advance)

                # Global inactivity timeout: if 30 seconds have passed since the question started, reset to Waiting Mode
                if time.time() - question_last_time >= 30:
                    mode = WAITING_MODE
                    last_sentence_time = time.time()
                    question_index = 0
                    question_input_text = ""
                # Otherwise, if no key press for QUESTION_MODE_TIMEOUT seconds and some text has been entered, move on
                elif time.time() - question_last_time >= QUESTION_MODE_TIMEOUT:
                    if question_input_text.strip()!="":
                        question_index += 1  # Move to next question
                        question_input_text = ""
                        question_last_time = time.time()

            else:
                # All questions have been answered; switch to Thank You mode.
                mode = THANK_YOU_MODE
                thank_you_start_time = time.time()
                qr_surface = None  # Ensure QR code gets generated

        elif mode==THANK_YOU_MODE:
            # ---------------- Thank You Mode Display ----------------
            # Display a "thank you" message in the center of the screen
            thank_you_surface2 = main_font.render("Humm...", True, text_color)
            thank_you_rect2 = thank_you_surface2.get_rect(center=(screen_width // 2, screen_height // 2 - 50))
            screen.blit(thank_you_surface2, thank_you_rect2)

            thank_you_surface4 = main_font.render("Intervention Made.", True, text_color)
            thank_you_rect4 = thank_you_surface4.get_rect(center=(screen_width // 2, screen_height // 2 + 50))
            screen.blit(thank_you_surface4, thank_you_rect4)

            thank_you_surface3 = main_font.render("Bye.", True, text_color)
            thank_you_rect3 = thank_you_surface3.get_rect(center=(screen_width // 2, screen_height // 2 + 150))
            screen.blit(thank_you_surface3, thank_you_rect3)

            # Generate the QR code only once
            '''
            if qr_surface is None:
                # Format the Q&A text from the session
                qr_text = ""
                for q, a in session_q_and_a:
                    qr_text += f"{q}\nYour input: {a}\n\n"
                # Create QR code using the qrcode library
                qr = qrcode.QRCode(version=1, box_size=10, border=4)
                qr.add_data(qr_text)
                qr.make(fit=True)
                # Create an image (convert to RGB)
                img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
                # Convert PIL image to string data and then to a pygame surface
                mode_str = img.mode
                size = img.size
                data = img.tobytes()
                qr_surface = pygame.image.fromstring(data, size, mode_str)
                # Optionally scale the QR code to a more suitable size (e.g., 300x300)
                qr_surface = pygame.transform.scale(qr_surface, (screen_width // 6, screen_width // 6))

            # Blit the QR code underneath the "thank you" line
            qr_rect = qr_surface.get_rect(center=(screen_width // 4, screen_height // 2))
            screen.blit(qr_surface, qr_rect)

            # Also display the Q&A text (using the system font for clarity)
            qna_lines = []
            for q, a in session_q_and_a:
                qna_lines.append(q)
                qna_lines.append("Your input: " + a)
                qna_lines.append("")  # Blank line for spacing

            # y_text = qr_rect.bottom + 20
            y_text = 200
            for line in qna_lines:
                line_surface = recap_font.render(line, True, text_color)
                line_rect = line_surface.get_rect(center=(3 * (screen_width // 4) - 20, y_text))
                screen.blit(line_surface, line_rect)
                y_text += line_surface.get_height() + 5

            # ---------------- Countdown Timer ----------------
            # Calculate remaining time before returning to Waiting Mode
            remaining = int(THANK_YOU_DURATION - (time.time() - thank_you_start_time))

            if remaining > 1:
                countdown_text = f"System restart in {remaining} seconds."
            else:
                countdown_text = f"System restart in {remaining} second."

            countdown_surface = bottom_font.render(countdown_text, True, text_color)
            countdown_rect = countdown_surface.get_rect(center=(screen_width // 2, screen_height - 20))
            screen.blit(countdown_surface, countdown_rect)
            '''

            # After THANK_YOU_DURATION seconds, return to Waiting Mode and reset session data
            if time.time() - thank_you_start_time >= THANK_YOU_DURATION:
                mode = WAITING_MODE
                # Remap the keyboard
                CUSTOM_LAYOUT = random_custom_layout()
                last_sentence_time = time.time()
                current_sentence = random.choice(SENTENCES)
                # Reset session data for next session
                #session_q_and_a = []
                #qr_surface = None

        # ---------------- Draw the Fixed Prompt at the Bottom ----------------
        if mode==WAITING_MODE:
            prompt_text = ""
        elif mode==INPUT_MODE:
            prompt_text = ""
        elif mode==QUESTION_MODE:
            prompt_text = ""
        elif mode==THANK_YOU_MODE:
            prompt_text = ""
        prompt_surface = bottom_font.render(prompt_text, True, text_color)
        prompt_rect = prompt_surface.get_rect(midbottom=(screen_width // 2, screen_height - 10))
        screen.blit(prompt_surface, prompt_rect)

        # ---------------- Update Display and Tick the Clock ----------------
        pygame.display.flip()
        clock.tick(30)  # Limit to 30 FPS

    pygame.quit()


def append_to_file(filename, text):
    """
    Appends the given text to the specified file, followed by a newline.
    """
    with open(filename, "a", encoding="utf-8") as f:
        f.write(text + "\n")


if __name__=="__main__":
    main()