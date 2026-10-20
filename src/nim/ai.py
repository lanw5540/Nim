from __future__ import annotations

from typing import Literal
import random

from nim import Action, Board, Probability, QValue,available_actions

type Algorithm = Literal["greedy", "epsilon-greedy"]


class QLearning:
    def __init__(
            self,
            epsilon: Probability = 0.1,
            alpha: Probability = 0.5,
            gamma: Probability = 0.9,
    ):
        """Initialise l'IA.

        Une IA nouvellement initialisée possède
        un dictionnaire d'apprentissage Q vide,
        un taux d'apprentissage (alpha)
        et un taux d'exploration (epsilon).

        Args:
            epsilon:
                Le taux d'exploration.
                Epsilon est la probabilité que l'agent
                choisisse une action au hasard plutôt que la meilleure action
                connue pendant l'entraînement.
                Avec math `\epsilon = 0` ,l'agent n'explore jamais et risque
                de rester bloqué sur les premières actions qui ont fonctionné ;
                avec math`\epsilon = 1`, il joue toujours au hasard et
                n'exploite jamais ce qu'il a appris.
                La valeur par défaut de 0.1 est une bonne option par default.
                l'agent exploite ses connaissances 90 % du temps et explore
                assez pour découvrir les autres actions.
                TODO: epsilon (5 points)
                    Identifier une valeur par défaut
                    et documenter le paramètre alpha de manière à expliquer
                    le sens du paramètre et le choix de sa valeur.
            alpha:
                Le facteur d'apprentissage.
                Alpha (math`\alpha`) détermine à quel point une nouvelle
                estimation remplace l'ancienne valeur-Q
                (math`0 \leq \alpha \leq 1`).
                Avec math`\alpha = 0`, la valeur-Q ne change jamais et
                l'agent n'apprend rien ; avec math`\alpha = 1`, l'ancienne
                valeur est entièrement remplacée par la dernière expérience.
                La valeur par défaut de 0.5 accorde autant d'importance à
                l'expérience passée qu'à la nouvelle information.
                TODO: alpha (5 points)
                    Identifier une valeur par défaut
                    et documenter le paramètre alpha de manière à expliquer
                    le sens du paramètre et le choix de sa valeur.
            gamma:
                Le facteur d'actualisation.

                Dans le Q-learning, γ (math`\gamma`) multiplie l'estimation
                de la valeur future optimale.
                L'importance accordée à la récompense suivante est définie
                par le paramètre gamma.

                Gamma est un nombre réel compris entre 0 et 1
                (math`0 \leq \gamma \leq 1`).
                Si l'on fixe gamma à zéro, l'agent ignore totalement les
                récompenses futures ;
                de tels agents ne prennent en compte que les récompenses
                immédiates.
                En revanche, si l'on fixe gamma à 1,
                l'algorithme recherche des récompenses élevées à long terme.

                La valeur par défaut de 0.9 s'explique parce qu'au Nim,
                seule la dernière action d'une partie reçoit une récompense
                non nulle. Un gamma élevé permet à cette récompense de se
                propager jusqu'aux premiers coups de la partie.
                TODO: gamma (2 points)
                    Identifier une valeur par défaut


        Le dictionnaire d'apprentissage Q associe les paires (état, action) à
        une valeur-Q.

        """
        self.q: dict[tuple[Board, Action], QValue] = {}
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma

    def update(
        self, old_state: Board, action: Action, new_state: Board, reward: QValue
    ) -> None:
        """Met à jour le modèle Q-learning.

        Args:
            old_state:
                L'état avant l'action.
            action:
                L'action entreprise.
            new_state:
                L'état résultant de l'action.
            reward:
                La récompense obtenue.

        """
        old = self.get_q_value(old_state, action)
        best_future = self.best_future_reward(new_state)
        self.update_q_value(old_state, action, old, reward, best_future)

    def get_q_value(self, state: Board, action: Action) -> QValue:
        """Retourne la valeur-Q pour un état et une action donnés.

        Si aucune valeur-Q n'existe encore dans `self.q`, retourne 0.
        """
        return self.q.get((state, action),0)
        # TODO: get_q_value (10 points)
        #   Tester et implémenter get_q_value

    def update_q_value(
        self,
        state: Board,
        action: Action,
        old_q: QValue,
        reward: QValue,
        future_rewards: QValue,
    ) -> None:
        r"""Met à jour le Q-value.

        Args:
            state:
                L'état actuellement mis à jour.
            action:
                L'action qui met à jour l'état.
            old_q:
                L'ancienne valeur-Q pour cette paire état-action.
            reward:
                La récompense actuelle.
            future_rewards:
                L'estimation des récompenses futures.

        Utilise la formule:

        .. math::

            Q(S, A) <- Q_{old} + \alpha \cdot (Q_{new} - Q_{old})

        telle que :math:`Q_{old}` est l'ancienne Q-Value, :math:`\alpha` est le
        taux d'apprentissage, et :math:`Q_{new}` est la somme de la récompense
        actuelle et l'estimation des récompenses futures pondérée par le
        facteur d'actualisation.

        """

        new_q = reward + self.gamma * future_rewards
        self.q[(state, action)] = old_q + self.alpha * (new_q - old_q)


        # TODO: update_q_value (10 points)
        #   Tester et implémenter update_q_value


    def best_future_reward(self, state: Board) -> QValue:
        """Estime la meilleure récompense future étant donné un état `state`.

        Considère toutes les paires `(état, action)` possibles disponibles
        dans cet état et retourne le maximum de toutes leurs valeurs-Q.
        Utilise 0 comme valeur-Q si une paire n'a pas de valeur-Q dans
        `self.q`.
        S'il n'y a aucune action disponible dans l'état, retourne 0.

        """
        return max(
            (self.get_q_value(state, action) for action in available_actions(state)),
            default=0,
        )
        # TODO: best_future_reward (10 points)
        #   Tester et implémenter best_future_reward


    def choose_action(self, state: Board, train: bool = True) -> Action:
        """Étant donné un état, retourne une action à entreprendre.

        Si `train` est `False`, retourne la meilleure action disponible dans cet
        état (celle ayant la plus haute valeur-Q, en utilisant 0 pour les paires
        sans valeur-Q).

        Si `train` est `True`, choisit une action disponible aléatoire avec la
        probabilité `self.epsilon`, sinon choisit la meilleure action
        disponible.

        Si plusieurs actions ont la même valeur-Q, n'importe laquelle d'entre
        elles est une valeur de retour acceptable.

        """
        actions = list(available_actions(state))
        if train and random.random() < self.epsilon:
            return random.choice(actions)
        return max(actions, key=lambda action: self.get_q_value(state, action))

        # TODO: choose_action (10 points)
        #   Tester et implémenter choose_action

