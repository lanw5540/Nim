from __future__ import annotations

import random
from typing import cast

from nim import Action, Board, Nim, Player, Probability, new_random_board
from nim.ai import QLearning

type Step = tuple[Board, Action]
"""
Un tour de jeu.

Un tour de jeu est la paire :math:`s, a`
telle que math `s` est l'état ou le plateau du jeu 
avant d'y poser l'action math `a`.

Exemples:
    >>> ( coup_final := ((0, 2, 0, 0), (1, 2)) )
    ((0, 2, 0, 0), (1, 2))
"""


def play(
    game: Nim | None = None,
    ai: QLearning | None = None,
    human_player: Player | None = None,
    ui: UserInterface | None = None,
):
    """Joue une partie de Nim.

    Args:
        game:
            Un jeu de nim avec un plateau neuf.
            Si `None`, une instance est créé avec les paramètres par défaut.
        ai:
            Une intelligence artificielle de Q-Apprentissage.
            Dans le cas c'est deux intelligences artificielles qui
            s'affrontent, la même instance est utilisée.
            Si `None`, une instance est créé avec les paramètres par défaut.
        human_player:
            Le numéro de joueur du joueur humain.
            Si `None`, alors on considère que deux agents s'affrontent.
        ui:
            L'interface utilisateur.
            Si `None`, une instance est créé avec les paramètres par défaut.
    """
    game = game or Nim()
    ai = ai or QLearning()
    ui = ui or UserInterface()

    # On conserve le dernier tour de chaque joueur
    last_step: dict[Player, Step] = {}

    while True:
        old_board = game.board
        current_player = game.player

        ui.show_board(old_board)
        ui.show_thinking(
            current_player, old_board, is_human=current_player == human_player
        )

        if current_player == human_player:
            action = ui.select_action(current_player, old_board)
        else:
            action = ai.choose_action(game.board)

        new_board = game.move(action)
        ui.show_transition(old_board, action, new_board)
        ui.show_board(new_board)
        last_step[current_player] = (old_board, action)

        if game.winner is not None:
            try:
                player = cast(Player, game.winner)
                board, action = last_step[player]
                ai.update(board, action, new_board, 1)
            except KeyError:
                pass
            try:
                player = cast(Player, game.loser)
                board, action = last_step[player]
                ai.update(board, action, new_board, -1)
            except KeyError:
                pass

            ui.show_gameover(human_player, game.winner, old_board)
            break
        else:
            try:
                ai.update(*last_step[current_player], new_board, 0)
            except KeyError:
                pass


def train(ai: QLearning, num_train_iterations: int):
    """Fait jouer un nombre de parties à l'IA pour s'entraîner

    Args:
        ai:
           L'intelligence à entraîner
        num_train_iterations:
            Le nombre de partie à jouer pendant l'entraînement.
    """
    for i in range(num_train_iterations):
        play(ai=ai)
    return ai


def run(
    human_player: Player | None,
    num_train_iterations: int = 0,
    initial_board: Board | None = None,
    epsilon: Probability | None = None,
    alpha: Probability | None = None,
    gamma: Probability | None = None,
):
    """Entraïne l'adversaire et lance une partie contre lui.

    Args:
        human_player:
            Détermine si le joueur joue premier ou deuxième.
            Si `None`, l'humain joue premier.
        num_train_iterations:
            Le nombre de partie que l'agent va jouer pour s'entrainer.
        initial_board:
            Un plateau de jeu initial.
            Si `None`, un plateau aléatoire est généré.
        epsilon:
            Le taux d'exploration de l'agent.
            Si `None`, une probabilité aléatoire est utilisée.
        alpha:
            Le facteur d'apprentissage.
            Si `None`, une probabilité aléatoire est utilisée.
        gamma:
            Le facteur d'actualisation.
            Si `None`, une probabilité aléatoire est utilisée.
    """
    human_player = human_player or 0
    epsilon = epsilon or random.randint(0, 100) / 100
    alpha = alpha or random.randint(0, 100) / 100
    gamma = gamma or random.randint(0, 100) / 100
    initial_board = initial_board or new_random_board()

    ai = QLearning(epsilon=epsilon, alpha=alpha, gamma=gamma)
    train(ai, num_train_iterations=num_train_iterations)

    game = Nim(board=initial_board)

    play(game=game, ai=ai, human_player=human_player)


class UserInterface:
    def show_board(self, board: Board) -> None:
        print()
        print("Plateau :")
        for i, count in enumerate(board):
            print(f"Tas {i} : {count}")
        print()

    def show_thinking(self, player: Player, board: Board, is_human: bool) -> None:
        if is_human:
            print(f"Au tour du joueur {player} (Humain).")
        else:
            print(f"Au tour du joueur {player} (IA)...")

    def select_action(self, player: Player, board: Board) -> Action:
        while True:
            try:
                heap = int(input("Choisissez une heap : "))
                count = int(input("Nombre d'objets à retirer : "))

                if 0 <= heap < len(board) and 1 <= count <= board[heap]:
                    return (heap, count)

                print("Mouvement invalide. Réessayez.")
            except ValueError:
                print("Veuillez entrer des nombres entiers.")

    def show_transition(
        self, old_board: Board, action: Action, new_board: Board
    ) -> None:
        heap, count = action[0], action[1]
        print(f"-> Action : {count} objet(s) retiré(s) du tas {heap}.")

    def show_gameover(
        self, human_player: Player | None, winner: Player, board: Board
    ) -> None:
        print("\n=== PARTIE TERMINÉE ===")
        type_joueur = "Humain" if winner == human_player else "IA"
        print(f"Le gagnant est le joueur {winner} ({type_joueur}).")
