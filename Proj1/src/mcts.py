import math
import random
import time
from state import *
from copy import deepcopy

# Represents a node of the mcts tree
class MCTSNode:
    def __init__(self, game_state):
        self.game_state = game_state
        self.parent = None
        self.children = []
        self.num_visits = 0
        self.total_reward = 0
        # Untried actions are simply the valid moves formatted for mcts (capture sequence as a list of lists)
        self.untried_actions = [move for move in game_state.ai_moves]

    # Pops an untried action, applies it and adds the node created from the child state to children
    def add_child(self):
        action = self.untried_actions.pop()
        child_game_state = self.game_state.apply_move(action)
        child = MCTSNode(child_game_state)
        child.parent = self
        self.children.append(child)

# UCT calculation based on the standard formula
# with an exploration parameter (c) equal to the square-root of 2
# proven to give asymptotic optimality, for reward in the range
# of [0, 1]
def calc_uct(child, parent_visits):
    avg_reward = child.total_reward/child.num_visits
    exploration_param = math.sqrt(2)

    uct = avg_reward + exploration_param*math.sqrt(math.log(parent_visits)/child.num_visits)

    return uct

# Gets the child with largest uct value
# balancing exploration and exploitation
# while traversing
def best_uct(children, parent_visits):
    best_uct = -math.inf
    best_child = None
    
    for child in children:
        if child.num_visits == 0: return child

        child_uct = calc_uct(child, parent_visits)

        if child_uct > best_uct:
            best_child = child
            best_uct = child_uct
        elif child_uct == best_uct:
            if child.num_visits > best_child.num_visits:
                best_child = child

    return best_child


def is_terminal(node):
    return node.game_state.winner != -1

# A node is a leaf, if it still has untried_actions
# from which no children were added to run simulations
# or it has a terminal state
def is_leaf(node):
    return node.untried_actions != [] or is_terminal(node)


# Traverses the tree from the root to a leaf
# by always choosing the child with the best uct value
def traverse(node):
    while not is_leaf(node):
        node = best_uct(node.children, node.num_visits)

    # If a node is terminal, make a rollout from it
    if is_terminal(node): return node

    # Otherwise the rollout will be made from one of its children
    node.add_child()

    return node.children[-1]

# Our policy is to simply choose random moves
def rollout_policy(state):
    chosen_move = random.choice(state.ai_moves)

    return chosen_move


# Apply random moves, until a result is reached
def rollout(node):
    game_state = deepcopy(node.game_state)

    while game_state.winner == -1:
        move = rollout_policy(game_state)
        game_state = game_state.apply_move(move)
        
    result = game_state.winner

    return result

# When updating the statistics of a node
# The number of visits is always incremented by 1
# And a reward is added based on who won in the rollout
# And what player made the move in the parent node
def update_stats(node, result):
    node.num_visits += 1

    if result == 3 - node.game_state.player:
        node.total_reward += 1
    elif result == 0:
        node.total_reward += 0.5


# Update stats from leaf where rollout was made
# up to the root
def backpropagate(node, result):
    if node == None: return

    update_stats(node, result)

    backpropagate(node.parent, result)


# The child of the root picked, will be the one
# With the highest average of reward over number of visits
def best_child(root):
    best_avg_reward = -math.inf
    best_child = None

    for child in root.children:
        avg_reward = child.total_reward/child.num_visits
        if avg_reward > best_avg_reward:
            best_child = child
            best_avg_reward = avg_reward

    return best_child


def time_left(start_time, time_limit):
    return time.time() - start_time < time_limit

# Continuously traverses to a leaf, performs a rollout
# and backpropagates the result, building the search tree
# until the specified time is over
def monte_carlo_tree_search(root, time_limit):
    start_time = time.time()

    while time_left(start_time, time_limit):
        leaf = traverse(root)
        simulation_result = rollout(leaf)
        backpropagate(leaf, simulation_result)

    return best_child(root)

# Updates the game state based on the state resulting
# from the best move, according to the monte carlo simulations
def make_mcts_move(time_limit=60):
    def make_mcts_move_aux(game):        
        mcts_root = MCTSNode(game.state)
        best_child_node = monte_carlo_tree_search(mcts_root, time_limit)
        game.state = best_child_node.game_state
    return make_mcts_move_aux
