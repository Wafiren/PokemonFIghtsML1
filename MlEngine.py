from DbContext import Db, pokemon, combats
import pandas as pd

from sklearn import metrics
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

from sqlalchemy.orm import aliased



class Data:
    def __init__(self, Database):
        # ----------Database Operations----------
        Database.OpenSession()  # Open DB session

        # Crate alieses, because we need attach one table 2 times in one query, so it will make column's names conflicts
        Pokemon1 = aliased(pokemon)
        Pokemon2 = aliased(pokemon)
        # Create SQLAlechemy Query. Statement give us possibility to convert it to DataFrame, because its create it as "Hard SQL Query"
        Battles = Database.Session.query(
            combats.BinaryWinner,
            Pokemon1.Id, Pokemon1.Type1, Pokemon1.Type2, Pokemon1.HP, Pokemon1.Atk, Pokemon1.Def, Pokemon1.SpAtk,
            Pokemon1.SpDef, Pokemon1.Speed, Pokemon1.Generation, Pokemon1.Legendary,
            Pokemon2.Id, Pokemon2.Type1, Pokemon2.Type2, Pokemon2.HP, Pokemon2.Atk, Pokemon2.Def, Pokemon2.SpAtk,
            Pokemon2.SpDef, Pokemon2.Speed, Pokemon2.Generation, Pokemon2.Legendary
        ). \
            join(Pokemon1, combats.First_pokemon == Pokemon1.Id). \
            join(Pokemon2, combats.Second_pokemon == Pokemon2.Id). \
            statement
        DfBattles = pd.read_sql(Battles, Database.Connection)

        PokemonList = Database.Session.query(pokemon).statement
        DfPokemonList = pd.read_sql(PokemonList, Database.Connection)

        Database.CloseSession()  # Close DB session
        # ----------Database Operations----------
        self.PokemonList = DfPokemonList
        self.PreparedData = DfBattles
        self.__ConvertToInts()

    def __ConvertToInts(self):
        # Convert Legendary (Bool) to int
        self.PreparedData.Legendary = self.PreparedData.Legendary.astype(int)
        # Convert types (String) to int
        # Download all types without duplicates
        self.Type1String = list(self.PokemonList["Type1"].unique())
        self.Type2String = list(self.PokemonList["Type2"].unique())
        # Replace strings with ints related to index value
        self.PreparedData["Type1"] = self.PreparedData["Type1"].replace(
            self.Type1String, list([i for i in range(1, len(self.Type1String) + 1)])
        )
        self.PreparedData["Type2"] = self.PreparedData["Type2"].replace(
            self.Type2String, list([i for i in range(1, len(self.Type2String) + 1)])
        )

class ProdModel:
    def __init__(self, ChoosenModel, Mistake, MaxMinDiffrence, Population):
        self.Model = ChoosenModel
        self.Mistake = Mistake
        self.MaxMinDiffrence = MaxMinDiffrence
        self.Population = Population #Loops
        self.Type1String = 0
        self.Type2String = 0

class Brain:
    def __init__(self, Data):
        self.Data = Data
        self.Results = []
        self.Models = []
        self.ChoosenModel = 0


    def Learn(self):

        RandomData = shuffle(self.Data, random_state=13)
        # Prepare Data
        X = RandomData.drop("BinaryWinner", axis=1)
        Y = RandomData["BinaryWinner"]
        # Split to train and test
        Xtr, Xtest, Ytr, Ytest = train_test_split(X, Y, test_size=0.3, random_state=19)

        for Learn in range(10):
            model = DecisionTreeClassifier()

            model.fit(Xtr, Ytr)
            predykcja = model.predict(Xtest)
            self.Results.append(metrics.mean_absolute_error(Ytest, predykcja))
            self.Models.append(model)

    def ConfigModel(self):
        #Find the best Result (closer to 0 -> better) and take the best model
        self.ChoosenModel = self.Models[self.Results.index(min(self.Results))]

def CreateModel():
    DbData = Data(Db)
    Model = Brain(DbData.PreparedData)
    Model.Learn()
    Model.ConfigModel()
    FinalModel = ProdModel(Model.ChoosenModel, min(Model.Results), max(Model.Results) - min(Model.Results), len(Model.Results))
    FinalModel.Type1String = DbData.Type1String
    FinalModel.Type2String = DbData.Type2String
    return FinalModel

