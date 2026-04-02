import random
import tkinter as tk
from tkinter import messagebox

words = ["python", "college", "programming", "language", "computer", "science"]
word = random.choice(words)

display = ["_"] * len(word)
lives = 5
guessed_letters = []

def guess_letter():
    global lives
    
    guess = entry.get().lower()
    entry.delete(0, tk.END)

    if len(guess) != 1 or not guess.isalpha():
        messagebox.showwarning("Invalid", "Enter a single letter")
        return

    if guess in guessed_letters:
        messagebox.showinfo("Info", "Letter already guessed")
        return

    guessed_letters.append(guess)

    if guess in word:
        for i in range(len(word)):
            if word[i] == guess:
                display[i] = guess
    else:
        lives -= 1

    word_label.config(text=" ".join(display))
    lives_label.config(text=f"Lives: {lives}")

    if "_" not in display:
        messagebox.showinfo("Winner", "Congratulations! You guessed the word!")
        root.destroy()

    if lives == 0:
        messagebox.showinfo("Game Over", f"Bummer! The word was {word}")
        root.destroy()


root = tk.Tk()
root.title("Guess the Word Game")
root.geometry("360x200")

word_label = tk.Label(root, text=" ".join(display), font=("Arial", 24))
word_label.pack(pady=10)

lives_label = tk.Label(root, text=f"Lives: {lives}", font=("Arial", 14))
lives_label.pack()

entry = tk.Entry(root, font=("Arial", 14))
entry.pack(pady=10)

guess_button = tk.Button(root, text="Guess", command=guess_letter)
guess_button.pack()

root.mainloop()
