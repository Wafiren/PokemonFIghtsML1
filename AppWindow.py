import tkinter as tk
import pandas as pd
from DbContext import Db, pokemon, combats

class StaticText:
    def __init__(self,Window ,Text, X, Y):
        self.Text = tk.StringVar()
        self.Text.set(Text)
        TextLabel = tk.Label(Window, textvariable=self.Text, padx=X, pady=Y)
        TextLabel.pack()

class Input:
    def __init__(self, Window, Text):
        Description = tk.Label(Window, text=Text).pack()
        self.Value = tk.Entry(Window, width=40)
        self.Value.pack()

class Button:
    def __init__(self, Window, Text, Command):
        ok = tk.Button(Window, text=Text, width=20, command=Command)
        ok.pack()

class Window:
    def __init__(self, FinalModel):
        #Create Main window
        self.FinalModel = FinalModel
        self.Window = tk.Tk()
        self.Window.title("Pokemon Fights")
        StaticText(self.Window, f"Version\nMistake^2: {FinalModel.Mistake}\nMax-Min Diffrence: {FinalModel.MaxMinDiffrence}\nPopulation: {FinalModel.Population}", 200, 10)
        StaticText(self.Window, "Welcome! Write pokemon names in the inputs, and click 'Fight!' button to see who win.", 100, 10)
        self.Pokemon1 = Input(self.Window, "Pokemon 1:")
        StaticText(self.Window, "VS", 100, 10)
        self.Pokemon2 = Input(self.Window, "Pokemon 2:")
        Button(self.Window, "Fight!", self.Command)
        # Loop for endless running
        tk.mainloop()

    def Command(self):
        Db.OpenSession()
        Pokemon1 = Db.Session.query(pokemon.Id, pokemon.Type1, pokemon.Type2, pokemon.HP, pokemon.Atk, pokemon.Def, pokemon.SpAtk,
                                    pokemon.SpDef, pokemon.Speed, pokemon.Generation, pokemon.Legendary).filter(pokemon.Name == self.Pokemon1.Value.get()).statement
        Pokemon2 = Db.Session.query(pokemon.Id, pokemon.Type1, pokemon.Type2, pokemon.HP, pokemon.Atk, pokemon.Def, pokemon.SpAtk,
                                    pokemon.SpDef, pokemon.Speed, pokemon.Generation, pokemon.Legendary).filter(pokemon.Name == self.Pokemon2.Value.get()).statement
        DfPokemon1 = pd.read_sql(Pokemon1, Db.Connection)
        DfPokemon2 = pd.read_sql(Pokemon2, Db.Connection)
        Db.CloseSession()
        #Change for int
        DfPokemon1["Type1"] = DfPokemon1["Type1"].replace(
            self.FinalModel.Type1String, list([i for i in range(1, len(self.FinalModel.Type1String) + 1)]))
        DfPokemon1["Type2"] = DfPokemon1["Type2"].replace(
            self.FinalModel.Type2String, list([i for i in range(1, len(self.FinalModel.Type2String) + 1)]))
        DfPokemon2["Type1"] = DfPokemon2["Type1"].replace(
            self.FinalModel.Type1String, list([i for i in range(1, len(self.FinalModel.Type1String) + 1)]))
        DfPokemon2["Type2"] = DfPokemon2["Type2"].replace(
            self.FinalModel.Type2String, list([i for i in range(1, len(self.FinalModel.Type2String) + 1)]))
        #Change for int
        DfPokemon1.Legendary = DfPokemon1.Legendary.astype(int)
        DfPokemon2.Legendary = DfPokemon2.Legendary.astype(int)
        Battle = pd.concat([DfPokemon1, DfPokemon2], axis=1, join="inner") #Connect Dataframes to 1 (Like battle in MlEngine)
        Score = self.FinalModel.Model.predict(Battle)
        if Score == 1:
            Winner = self.Pokemon1.Value.get()
        elif Score == 0:
            Winner = self.Pokemon2.Value.get()
        StaticText(self.Window, f"The winner is: {Winner}", 200, 10)
