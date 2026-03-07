import random

print("Welcome to Number Guessing Game!")

number = random.randint(1, 50)

guess = 0
attempts = 0

while guess != number:
    guess = int(input("Guess a number between 1 and 50: "))
    attempts += 1

    if guess < number:
        print("Too Low! Try again.")
    elif guess > number:
        print("Too High! Try again.")
    else:
        print("Correct! You guessed the number.")
        print("Total attempts:", attempts)