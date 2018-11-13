class Hangman:

    seven_lives = '**   **___\n  |\n  |\n  |\n  |\n/\\'
    six_lives   = '**   **___\n  |     |\n  |\n  |\n  |\n/\\'
    five_lives  = '**   **___\n  |     |\n  |    O\n  |\n  |\n/\\'
    four_lives  = '**   **___\n  |     |\n  |    O\n  |     |\n  |\n/\\'
    three_lives = '**   **___\n  |     |\n  |    O\n  |     |\\\n  |\n/\\'
    two_lives   = '**   **___\n  |     |\n  |    O\n  |  / |\\\n  |\n/\\'
    one_life    = '**   **___\n  |     |\n  |    O\n  |  / |\\\n  |      \\\n/\\'
    dead        = '**   **___\n  |     |\n  |    O\n  |  / |\\\n  |   /\\\n/\\'
    dead_left   = '**   **___\n  |    |\n  |  O\n  |/ |\\\n  | /\\\n/\\'
    dead_right  = '**   **___\n  |      |\n  |      O\n  |    / |\\\n  |      /\\\n/\\'
    life_drawing = {7 : seven_lives, 6 : six_lives, 5 : five_lives, 4 : four_lives, 3 : three_lives, 2 : two_lives, 1 : one_life, 0 : dead}
    
    rules = "-----\n_***Hangman rules***_\n- You have **7** lives.\n- You can type `a single character` to submit a guess.\n- Type `solve your_word` if you believe you know the word. Fail to do so and you will lose **3** lives.\n- To be reminded of the current state of the game, type `state`.\n- To see these rules again anytime, type `rules`.\nHave fun!\n-----"
    
    def __init__(self, word, channel):
        self.word = word
        self.channel = channel
        self.unsolved = list(self.word)
        self.lives = 7
        self.solved = ['_'] * len(self.word)
        self.wrong_chars = []
            
    def already_wrong_character(self, char):
        return char in self.wrong_chars
            
    def update(self, char):
        if char in self.wrong_chars or char in self.solved:
            return ["'" + char + "' was already checked!" + self.get_default_reply() , False]
        if self.check_for_character(char):
            if ''.join(self.solved) == self.word:
                return ["Congratulations! :v:\nYou solved: " + self.word , "Win"]
            else:
                return ["Nice guess " + self.author_sign() + "!" + self.get_default_reply() , False]
        else:
            if self.lives == 0:
                return [":sob: :sob: :sob: :sob: :sob:\nYou failed to guess: " + self.word, "Lose"]
            elif self.lives >= 0 and self.lives <= 7:
                return ["Tough luck " + self.author_sign() + "! Try again..." + self.get_default_reply() , False]
            else:
                return False
            
    def solve(self, word):
        if self.word == word:
            return ["Congratulations! :v:\nYou solved: " + self.word , "Win"]
        else:
            self.lives -= 3
            if self.lives <= 0:
                return [":sob: :sob: :sob: :sob: :sob:\nYou failed to guess: " + self.word, "Lose"]
            else:
                return ["BZZT!!! Too bad " + self.author_sign() + ", wrong guess..." + self.get_default_reply() , False]
            
    def get_state(self):
        return "*Current state of Hangman*" + self.get_default_reply()
            
    def author_sign(self):
        return '_author_'
            
    def get_default_reply(self):
        return "\n" + self.get_life_drawing() + "\nWrong characters: " + ','.join(self.get_wrong_chars()) + "\n\n" + self.get_solved()
            
    def check_for_character(self, char):
        indexes =  [i for i,c in enumerate(self.word) if c == char]
        if indexes:
            for i in indexes:
                self.solved[i] = char
                self.unsolved[i] = '_'
            return True
        else:
            self.wrong_chars.append(char)
            self.lives -= 1
            return False
        
    def get_wrong_chars(self):
        return self.wrong_chars
        
    def get_solved(self):
        solved_str = ''
        for char in self.solved:
            if char == '_':
                solved_str += '\_ '
            else:
                solved_str += char + ' '
        return solved_str
        
    def get_life_drawing(self):
        return Hangman.life_drawing.get(self.lives)
        
    def get_channel(self):
        return self.channel
        
#TODO: add solving directly