import numpy as np
import matplotlib.pyplot as plt
import random
import os

"""
Implementation of N-Step Monte Carlo
It doesn't wait for the entire episode like MC (Monte Carlo) or just the next step like TD (Temporal Difference),
it updates after N steps.

Some cases
if N == 1   -> 1-step TD Learning
if N -> inf -> MonteCarlo 

Drawbacks: Tuning of N, tradeoff between bias and variance,
           smaller N -> more bias, less variance
           larger  N -> less bias, more variance 
"""

os.makedirs("Monte_Carlo/Results", exist_ok=True)

class NStepMcPredection:
    def __init__(self, pi=None, gamma=0.9, alpha=0.1, n=7):
        self.state_space = [(i, j) for i in range(3) for j in range(3)]
        self.rewards = {(0,2): 1, (2,2):-1}
        self.val_pi_s = {s: self.rewards.get(s, 0) for s in self.state_space}
        self.episode_list = []
        self.gamma = gamma
        self.num_visits = {s : 0 for s in self.state_space}
        self.pi = {
            (0, 0): "right", (0, 1): "right", (0, 2): "right",
            (1, 0): "up",    (1, 1): "up",    (1, 2): "right",
            (2, 0): "up",    (2, 1): "right", (2, 2): "up"
        }
        
        self.mse_lst = [] 
        
        self.alpha = alpha
        self.n = n

        

    def transition_function(self, state, action):
        
        if state in self.rewards:
            return  state, self.rewards.get(state)
    
        row, col = state

        if action == "up":
            next_state = (max(row-1, 0), col)
        elif action == "down":
            next_state = (min(row+1, 2), col)
        elif action == "right":
            next_state = (row, min(col+1, 2))
        elif action == "left":
            next_state = (row, max(col-1, 0))
        else:
            next_state = state
            
        reward = self.rewards.get(next_state, 0)
        
        return next_state, reward
        
    def episode_gen(self, start_state, max_steps=100):
        
        state = start_state
        self.episode_list = []
        
        for _ in range(max_steps):
           
            action = self.pi[state]
            next_state, reward = self.transition_function(state, action) 
            self.episode_list.append((state, action, reward))
            
            if next_state in self.rewards:
                break
            state = next_state
    
    def monte_carlo(self):
        
        ep_len = len(self.episode_list)
        for t in range(ep_len):
            G = 0
            n_step = min(self.n, ep_len - t)
            
            for i in range(n_step):
                _, _, reward = self.episode_list[t + i]
                G += (self.gamma ** i) * reward
                
            if t + self.n < ep_len:
                G += (self.gamma ** self.n) * self.val_pi_s[self.episode_list[t+self.n][0]]
                    
            state, _, _ = self.episode_list[t]
            
            if state not in self.rewards:
                self.num_visits[state] += 1
                self.val_pi_s[state] += (G - self.val_pi_s[state]) / self.num_visits[state]
                
        
    def train(self, num_episodes=100):    ## You can increase number of episodes
        
        for i in range(num_episodes):
            prev_val_pi_s = self.val_pi_s.copy()
            st_state = random.choice([s for s in self.state_space if s not in self.rewards]) 
            self.episode_gen(st_state)
            self.monte_carlo()
            
            mse = np.mean([abs(self.val_pi_s[s] - prev_val_pi_s[s]) ** 2 for s in self.state_space])
            self.mse_lst.append(mse)

            if i % 10 == 0:
                print(f"Iteration {i}, Values:")
                for row in range(3):
                    print([round(self.val_pi_s[(row, col)], 2) for col in range(3)])
                print("\n")
    
    def plot_res(self):
        plt.plot(self.mse_lst, label="MSE")
        plt.xlabel("Episodes")
        plt.ylabel("Mean Squared Error")
        plt.title("MSE of Value Function")
        plt.grid()
        plt.savefig("Monte_Carlo/Results/n_steps_mc_mse.png") 
        plt.show()
        
        val_mat = np.zeros((3,3)) 
        for (i, j), val in self.val_pi_s.items():
            val_mat[i, j] = val
            
        plt.imshow(val_mat, cmap="coolwarm",interpolation="nearest")
        
        for i in range(3):
            for j in range(3):
                plt.text(j, i, round(val_mat[i, j], 2), ha="center", va="center")
                
        plt.colorbar(label="State Value")
        plt.title("Final Value Function Heatmap")
        plt.savefig("Monte_Carlo/Results/n_step_mc_heat_map.png") 
        plt.show()


alpha = NStepMcPredection()
alpha.train()
alpha.plot_res()