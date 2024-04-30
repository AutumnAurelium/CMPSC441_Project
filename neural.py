import random
from typing import List, Tuple

import torch
from combat import Combat
import pygad

# generates a bunch of data of enemy player actions
def generate_data(n: int, device: torch.device, progress_every=-1) -> List[Tuple[torch.Tensor, torch.Tensor]]:
    combat = Combat()
    data = []
    for i in range(n):
        if progress_every != -1:
            if i % progress_every == 0:
                print(f"Generated {i} examples")
        combat.battle_started(400, False, -1)

        choices = []

        for _ in range(random.randint(1, 10)):
            choice = random.randint(0, 2)
            enemy_choice = combat.select_enemy_move()

            #choices.append(choice)
            choices.append(enemy_choice)

            combat.history.append((choice, enemy_choice, "???"))

        if len(choices) < 20:
            choices += [-1] * (20 - len(choices))

        data.append((torch.tensor(choices).float().to(device), torch.tensor([combat.select_enemy_move()]).float().to(device)))
    return data

class NeuralPlayerModel(torch.nn.Module):
    def __init__(self):
        super(NeuralPlayerModel, self).__init__()
        self.hidden1 = torch.nn.Linear(20, 10)
        self.hidden2 = torch.nn.Linear(10, 3)
        self.relu = torch.nn.ReLU()
        self.output = torch.nn.Linear(3, 1)

    def forward(self, x):
        x = self.hidden1(x)
        x = self.relu(x)
        x = self.hidden2(x)
        x = self.relu(x)
        x = self.output(x)
        return x

class NeuralPlayer:
    def __init__(self):
        self.model = NeuralPlayerModel()
        self.model.load_state_dict(torch.load("neural_player.pth"))
        self.model.eval()
    
    def predict(self, combat: Combat) -> int:
        history = []
        for player_move, enemy_move, outcome in combat.history:
            #history.append(player_move)
            history.append(enemy_move)
        
        if len(history) < 20:
            history += [-1] * (20 - len(history))
        
        with torch.no_grad():
            response = self.model(torch.tensor(history[-20:]).float()).numpy()[0]
            choice = int(round(response))
            print(response, choice)

            if choice < 0.7:
                choice = 0
            elif choice > 1.3:
                choice = 2
            
            return choice


if __name__ == "__main__":
    if torch.cuda.is_available():
        print("CUDA is available!")

    dtype = torch.float
    device = torch.device("cuda:0")

    print(torch.cuda.get_device_name(0))

    data = generate_data(20000, device, progress_every=1000)

    # this neural network is really bad
    # i am confident that there is a better way to do this, but i haven't taken Machine Learning yet
    # so this network just receives the last 10 moves as a tensor and outputs the next move

    model = NeuralPlayerModel().to(device)
   
    critereon = torch.nn.MSELoss().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

    try:
        for epoch in range(500):
            BATCH_SIZE = 50
            for i in range(0, len(data), BATCH_SIZE):
                inputs, label = torch.stack([x[0] for x in data[i:i+BATCH_SIZE]]), torch.stack([x[1] for x in data[i:i+BATCH_SIZE]])

                optimizer.zero_grad()

                outputs = model(inputs)
                
                loss = critereon(outputs, label)
                loss.backward()
                optimizer.step()

            print(f"Epoch {epoch}, loss: {loss.item()}")
    except KeyboardInterrupt:
        print("Exiting training early...")

    test_data = generate_data(1, device)

    input_data, _ = test_data[0]

    model.eval()

    with torch.no_grad():
       print(model(input_data).cpu().numpy())

    torch.save(model.state_dict(), "neural_player.pth")