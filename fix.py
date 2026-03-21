with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

old = '''    def on_enter_guess(self):
        if self.game_data is None:
            return
        if self.game_data.get("status") != "playing":
            return
        if self.game_data.get("turn") != self.role:
            self.ids.message_label.text = t(self.language, "opponent_turn")
            return
        if len(self.current_guess) != WORD_LENGTH:
            self.ids.message_label.text = t(self.language, "not_enough")
            return
        if not is_valid_word_offline(self.current_guess, self.language):
            self.ids.message_label.text = t(self.language, "not_valid")
            return
        from online_game import submit_guess, set_winner
        opponent_word = self.game_data.get(
            "word_p2" if self.role == "p1" else "word_p1", ""
        )
        feedback = check_guess(opponent_word, self.current_guess)
        attempts = len(self.game_data.get(f"guesses_{self.role}", [])) + 1
        submit_guess(self.game_code, self.role, self.current_guess, feedback)
        if all(f == CORRECT for f in feedback):
            set_winner(self.game_code, self.role)
        elif attempts >= MAX_ATTEMPTS:
            l = letter.lower() if self.language == "en" else letter
            if fb == "green":
                self.used_letters[l] = "correct"
            elif fb == "yellow" and self.used_letters.get(l) != "correct":
                self.used_letters[l] = "misplaced"
            elif fb == "gray" and l not in self.used_letters:
                self.used_letters[l] = "wrong"
        build_keyboard_widget(
            self, self.language,
            self.on_key_press, self.on_backspace,
            self.on_enter_guess, used_letters=self.used_letters
        )
        self.current_guess = ""
            other_guesses = self.game_data.get(f"guesses_{other_role}", [])
            if len(other_guesses) >= MAX_ATTEMPTS:
                set_winner(self.game_code, "draw")
        self.current_guess = ""'''

new = '''    def on_enter_guess(self):
        if self.game_data is None:
            return
        if self.game_data.get("status") != "playing":
            return
        if self.game_data.get("turn") != self.role:
            self.ids.message_label.text = t(self.language, "opponent_turn")
            return
        if len(self.current_guess) != WORD_LENGTH:
            self.ids.message_label.text = t(self.language, "not_enough")
            return
        if not is_valid_word_offline(self.current_guess, self.language):
            self.ids.message_label.text = t(self.language, "not_valid")
            return
        from online_game import submit_guess, set_winner
        opponent_word = self.game_data.get(
            "word_p2" if self.role == "p1" else "word_p1", ""
        )
        feedback = check_guess(opponent_word, self.current_guess)
        submit_guess(self.game_code, self.role, self.current_guess, feedback)
        for letter, fb in zip(self.current_guess, feedback):
            l = letter.lower() if self.language == "en" else letter
            if fb == "gray" and l not in self.used_letters:
                self.used_letters[l] = "wrong"
        if all(f == CORRECT for f in feedback):
            set_winner(self.game_code, self.role)
        build_keyboard_widget(
            self, self.language,
            self.on_key_press, self.on_backspace,
            self.on_enter_guess, used_letters=self.used_letters
        )
        self.current_guess = ""'''

if old in content:
    content = content.replace(old, new)
    with open("main.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("SUCCESS: Method replaced.")
else:
    print("FAILED: Old method not found. No changes made.")