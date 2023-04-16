from pokemon import All_Pokemons, Pokemon, create_copy_pokemon, find_pokemon_by_name


class NPC:
    def __init__(self, name, dialogue):
        self.name = name
        self.dialogue = dialogue
        
    def talk(self):
        print(self.name + " says: " + self.dialogue)


class GymLeader(NPC):
    def __init__(self, name, dialogue, gym_type, team, badge_name):
        super().__init__(name, dialogue)
        self.gym_type = gym_type
        self.team = team
        self.badge_name = badge_name
        
    def challenge(self, player):
        print(self.name + " challenges you to a battle!")
        # start battle with player's team against Gym Leader's team
        #
        #
        #

class EliteTrainer(NPC):
    def __init__(self, name, dialogue, trainer_type, team):
        super().__init__(name, dialogue)
        self.trainer_type = trainer_type
        self.team = team
        
    def challenge(self, player):
        print(self.name + " challenges you to a battle!")
        # start battle with player's team against Gym Leader's team
        #
        #
        #


class Professor(NPC):
    def __init__(self, name, dialogue, research_area):
        super().__init__(name, dialogue)
        self.research_area = research_area
        
    def give_advice(self):
        print(self.name + " says: " + self.dialogue + " Remember to always do your research!")

class WildTrainer(NPC):
    def __init__(self, name, dialogue, team):
        super().__init__(name, dialogue)
        self.team = team
        
    def challenge(self, player):
        print(self.name + " challenges you to a battle!")
        # start battle with player's team against Wild Trainer's team







#faudrait faire des copies des pokemon plutôt
def return_GymLeader(number_of_the_Gym):
    
    if number_of_the_Gym == 1:
        Geodude = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Geodude"))
        Geodude.skip_to_lvl(12)
        Onix = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Onix"))
        Onix.skip_to_lvl(14)
        return GymLeader("Brock", "I'm the Gym Leader of the Pewter City Gym. My team is all about rock-solid defenses!", "Rock", [Geodude, Onix], "Boulder Badge")
    
    elif number_of_the_Gym == 2:
        Staryu = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Staryu"))
        Staryu.skip_to_lvl(18)
        Starmie = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Starmie"))
        Starmie.skip_to_lvl(21)
        return GymLeader("Misty", "I'm the Gym Leader of the Cerulean City Gym. My team is all about water-type Pokémon!", "Water", [Staryu, Starmie], "Cascade Badge")

    elif number_of_the_Gym == 3:
        Voltorb = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Voltorb"))
        Voltorb.skip_to_lvl(21)
        Pikachu = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Pikachu"))
        Pikachu.skip_to_lvl(18)
        Raichu = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Raichu"))
        Raichu.skip_to_lvl(24)    

        return GymLeader("Lt. Surge", "I'm the Gym Leader of the Vermilion City Gym. My team is all about electric-type Pokémon!", "Electric", [Voltorb, Pikachu, Raichu], "Thunder Badge")
   
    elif number_of_the_Gym == 4:
        Tangela = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Tangela"))
        Tangela.skip_to_lvl(24)
        Victreebel = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Victreebel"))
        Victreebel.skip_to_lvl(29)
        Vileplume = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Vileplume"))
        Vileplume.skip_to_lvl(29)    
        return GymLeader("Erika", "I'm the Gym Leader of the Celadon City Gym. My team is all about grass-type Pokémon!", "Grass", [Tangela, Victreebel, Vileplume], "Rainbow Badge")
    
    elif number_of_the_Gym == 5:
        Koffing1 = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Koffing"))
        Koffing1.skip_to_lvl(37)
        Koffing2 = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Koffing"))
        Koffing2.skip_to_lvl(37)
        Weezing = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Weezing"))
        Weezing.skip_to_lvl(43) 
        Muk = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Muk"))
        Muk.skip_to_lvl(39) 
        return GymLeader("Koga", "I'm the Gym Leader of the Fuchsia City Gym. My team is all about poison-type Pokémon!", "Poison", [Koffing1, Koffing2, Weezing, Muk], "Soul Badge")
    
    elif number_of_the_Gym == 6:     
        Kadabra = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Kadabra"))
        Kadabra.skip_to_lvl(38)
        MrMime = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Mr. Mime"))
        MrMime.skip_to_lvl(37)
        Alakazam = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Alakazam"))
        Alakazam.skip_to_lvl(43) 
        Venomoth = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Venomoth"))
        Venomoth.skip_to_lvl(38) 
        return GymLeader("Sabrina", "I'm the Gym Leader of the Saffron City Gym. My team is all about psychic-type Pokémon!", "Psychic", [Kadabra, MrMime, Alakazam, Venomoth], "Marsh Badge")
    
    elif number_of_the_Gym == 7:
        Growlithe = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Growlithe"))
        Growlithe.skip_to_lvl(42)
        Ponyta = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Ponyta"))
        Ponyta.skip_to_lvl(40)
        Rapidash = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Rapidash"))
        Rapidash.skip_to_lvl(42) 
        Arcanine = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Arcanine"))
        Arcanine.skip_to_lvl(47) 
        return GymLeader("Blaine", "I'm the Gym Leader of the Cinnabar Island Gym. My team is all about fire-type Pokémon!", "Fire", [Growlithe, Ponyta, Rapidash, Arcanine], "Volcano Badge")
    
    elif number_of_the_Gym == 8:
        Dugtrio = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Dugtrio"))
        Dugtrio.skip_to_lvl(42)
        Rhyhorn = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Rhyhorn"))
        Rhyhorn.skip_to_lvl(45)
        Nidoqueen = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Nidoqueen"))
        Nidoqueen.skip_to_lvl(44) 
        Nidoking = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Nidoking"))
        Nidoking.skip_to_lvl(45)        
        Rhydon = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Rhydon"))
        Rhydon.skip_to_lvl(50)  
        return GymLeader("Giovanni", "I'm the Gym Leader of the Viridian City Gym. My team is all about ground-type Pokémon!", "Ground", [Dugtrio, Rhyhorn, Nidoqueen, Nidoking, Rhydon], "Earth Badge")
    
    else:
        print("ERROR GymLeader doesn't exist")


def return_LigueTrainer(number_trainer, starter_type):
    if number_trainer == 1:
        Dewgong = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Dewgong"))
        Dewgong.skip_to_lvl(54)
        Cloyster = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Cloyster"))
        Cloyster.skip_to_lvl(53)
        Slowbro = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Slowbro"))
        Slowbro.skip_to_lvl(54)
        Jynx = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Jynx"))
        Jynx.skip_to_lvl(56)
        Lapras = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Lapras"))
        Lapras.skip_to_lvl(56)
        return EliteTrainer("Lorelei", "I'm one of the Elite Four! I'm Lorelei of the Pokémon League! \nWelcome to my icy domain!", "Ice", [Dewgong, Cloyster, Slowbro, Jynx, Lapras])
    elif number_trainer == 2:
        Onix1 = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Onix"))
        Onix1.skip_to_lvl(53)
        Hitmonlee = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Hitmonlee"))
        Hitmonlee.skip_to_lvl(55)
        Hitmonchan = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Hitmonchan"))
        Hitmonchan.skip_to_lvl(55)
        Onix2 = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Onix"))
        Onix2.skip_to_lvl(56)
        Machamp = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Machamp"))
        Machamp.skip_to_lvl(58)
        return EliteTrainer("Bruno", "I'm Bruno of the Elite Four! Through rigorous training, people and Pokémon can become stronger without limit!", "Fighting", [Onix1, Hitmonlee, Hitmonchan, Onix2, Machamp])
    elif number_trainer == 3:
        Gengar_1 = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Gengar"))
        Gengar_1.skip_to_lvl(56)
        Haunter_1 = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Haunter"))
        Haunter_1.skip_to_lvl(55)
        Golbat_1 = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Golbat"))
        Golbat_1.skip_to_lvl(56)
        Arbok_1 = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Arbok"))
        Arbok_1.skip_to_lvl(58)
        Gengar_2 = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Gengar"))
        Gengar_2.skip_to_lvl(60)
        return EliteTrainer("Agatha", "I am Agatha of the Elite Four. I hear Oak's taken a lot of interest in you, child. That old duff was once tough and handsome. That was decades ago. Now he just wants to fiddle with his Pokédex.", "Ghost", [Gengar_1, Haunter_1, Golbat_1, Arbok_1, Gengar_2])
 
    elif number_trainer == 4:
        Gyarados = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Gyarados"))
        Gyarados.skip_to_lvl(58)
        Dragonair1 = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Dragonair"))
        Dragonair1.skip_to_lvl(56)
        Dragonair2 = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Dragonair"))
        Dragonair2.skip_to_lvl(56)
        Aerodactyl = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Aerodactyl"))
        Aerodactyl.skip_to_lvl(60)
        Dragonite = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Dragonite"))
        Dragonite.skip_to_lvl(62)
        return EliteTrainer("Lance", "I am the Dragon-type Pokémon League Champion. You're going to need skill to defeat me!", "Dragon", [Gyarados, Dragonair1, Dragonair2, Aerodactyl, Dragonite])
    elif number_trainer == 5:
        pidgeot = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Pidgeot"))
        pidgeot.skip_to_lvl(61)
        alakazam = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Alakazam"))
        alakazam.skip_to_lvl(59)
        gyarados = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Gyarados"))
        gyarados.skip_to_lvl(61)
        rhydon = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Rhydon"))
        rhydon.skip_to_lvl(61)

        #if starter bulbizar
        if(starter_type=="grass"):
            exeggutor = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Exeggutor"))
            exeggutor.skip_to_lvl(61)
            charizard = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Charizard"))
            charizard.skip_to_lvl(65)
            team = [pidgeot, alakazam, gyarados, exeggutor, rhydon, charizard]
        #if starter salamèche
        elif(starter_type=="fire"):
            arcanine = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Arcanine"))
            arcanine.skip_to_lvl(61)
            blastoise = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Blastoise"))
            blastoise.skip_to_lvl(65)
            team = [pidgeot, alakazam, gyarados, arcanine, rhydon, blastoise]
        #if starter carapute
        elif(starter_type=="water"):
            arcanine = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Arcanine"))
            arcanine.skip_to_lvl(61)
            venusaur = create_copy_pokemon(All_Pokemons().better_find_pokemon_by_name("Venusaur"))
            venusaur.skip_to_lvl(65)
            team = [pidgeot, alakazam, gyarados, arcanine, rhydon, venusaur]
        else:
            print("Error no starter type")

        return EliteTrainer("Blue", "The Pokémon League Champion. You are now the most powerful Trainer in the world!", "no type", team)
    else:
        print("Error")









###########################TESTS###########################
#professor_oak = Professor("Professor Oak", "Welcome to the world of Pokémon!", "Pokédex development")
#professor_oak.talk()  # Professor Oak says: Welcome to the world of Pokémon!
#professor_oak.give_advice()  # Professor Oak says: Welcome to the world of Pokémon! Remember to always do your research!

import time
start_time = time.time()

Giovanni = return_GymLeader(8)
Giovanni.talk()
print(Giovanni.badge_name)
for pokemon in Giovanni.team:
    print(f"{pokemon.name} lvl: {pokemon.level}     hp: {pokemon.hp}    max_hp: {pokemon.max_hp}")

print("--- %s seconds ---" % (time.time() - start_time))


start_time = time.time()
ligue_trainer = return_LigueTrainer(5, "grass")
ligue_trainer.talk()
for pokemon in ligue_trainer.team:
    print(f"{pokemon.name} lvl: {pokemon.level}     hp: {pokemon.hp}    max_hp: {pokemon.max_hp}")

print("--- %s seconds ---" % (time.time() - start_time))

#peut-être pas aller chercher les poke ou en tout cas leur mettre direct les bon move pcq ça prend pas mal du temps à calculer