from game import location
import game.config as config
import game.display as display
from game.events import *
import game.items as items
import game.combat as combat
import game.event as event
from game.items import Item
import random
from game.context import Context
from game.combat import Monster
from game.display import menu



class IslandB(location.Location):

    def __init__ (self, x, y, w):
        super().__init__(x, y, w)
        self.name = "Island"
        self.symbol = 'I'
        self.visitable = True
        self.locations = {}
        self.locations["rockybeach"] = Rocky_beach(self)
        self.locations["cavern"] = Damp_cavern(self)
        self.locations["room"] = Entry_room(self)
        self.starting_location = self.locations["rockybeach"]

    def enter (self, ship):
        display.announce ("arrived at an island with a big cavern.", pause=False)



class Rocky_beach (location.SubLocation):
    def __init__ (self, m):
        super().__init__(m)
        self.name = "rockybeach"
        self.verbs['south'] = self
    
    def enter (self):
        display.announce ("Your ship is at anchor to the south. You paddle ashore on a small rowboat.\nAvoiding the treacherous rocks")

    def process_verb (self, verb, cmd_list, nouns):
        if (verb == "south"):
            display.announce ("You return to your ship.", pause=False)
            self.main_location.end_visit()
        if (verb == "north"):
            config.the_player.next_loc = self.main_location.locations["cavern"]
        if (verb in ["west", "east"]):
            display.announce("You wonder around the perimeter of the island, finding yourself back at your ship.")

class Dungeon_map(items.Item):
    def __init__(self):
        super().__init__("dungeon-map", 0)

    def process_verb (self, verb, cmd_list, nouns):
        if (verb == "read"):
         display.announce("Study the scroll, it reveals the path for the dungeon! W:N:E:E:N")

class Damp_cavern (location.SubLocation):
    def __init__ (self, m):
        super().__init__(m)
        self.name = "cavern"
        self.rats_present = True
        self.verbs['scare'] = self
        self.verbs['run'] = self
        self.verbs['north'] = self
        self.verbs['south'] = self
        self.verbs['east'] = self
        self.verbs['west'] = self

        
    def process_verb (self, verb, cmd_list, nouns):
        if (verb == "north"):
            display.announce("You find yourself facing a wall.")

        if (verb == "west"):
            display.announce("You ascend deeper into the cavern, and discover a room.")
            config.the_player.next_loc = self.main_location.locations["door"]
            config.the_player.go = True

        if (verb == "east"):
            display.announce("You find yourself facing a wall.")

        if (verb == "south"):
            display.announce("You turn back.")
            config.the_player.next_loc = self.main_location.locations["rockybeach"]

        if (verb == "scare"):
            while self.rats_present:
                success = random.choice([True, False])
                if success:
                    print("You flail your arms and swing your Cutlass around,\nin an attempt to scare them off.")
                    self.rats_present = False
                    self.find_adventurer()
                else: 
                    print("Your first attempt was unsucessful.")
        if (verb == "run"):
            description = "You lack the bravery and walk back to the beach in defeat to regain some courage."
            display.announce(description)
            config.the_player.next_loc = self.main_location.locations["rockybeach"]
            config.the_player.go = True
    

        

    def enter (self):
        #add another announcement for re-entry
        if self.rats_present:
            description = "You notice a squeeking sound that becomes louder the deeper you ascend."
            display.announce(description, pause = False)
            description = "Do you scare them off or turn back?"
            display.announce(description, pause = True)
        if not self.rats_present:
            description = "This looks familiar, You notice nothing has changed since you were last here."
            display.announce(description)

    

        
    def find_adventurer(self):
         display.announce("As the rats disperse from around you, a forsaken body appears.")
         display.announce("You notice a scroll lodged in their tattered clothing.")
         display.announce("Study the scroll, it reveals the path for the dungeon! W:N:E:E:N")
         #adds to inventory
         config.the_player.add_to_inventory([Dungeon_map()])


class Ornate_door(location.SubLocation):
    def __init__ (self, m):
        super().__init__(m)
        self.name = "door"
        self.verbs['exit'] = self
        self.verbs['leave'] = self
        self.verbs['north'] = self
        self.verbs['south'] = self
        self.verbs['east'] = self
        self.verbs['west'] = self

        self.event_chance = 100
        self.events.append(OoozeEvent())

    def enter (self):
        description = "You enter a room with a very ornate door to the north."
        display.announce(description)

    def process_verb (self, verb, cmd_list, nouns):
        if (verb == "south"):
            config.the_player.next_loc = self.main_location.locations["cavern"]
            config.the_player.go = True
        if (verb == "north"):
            config.the_player.next_loc = self.main_location.locations["room"]
            config.the_player.go = True

class Ooze(Monster):
    def __init__ (self):
        attacks = {}
        attacks["splash"] = ["splashes",random.randrange(55,110), (10,15)]
        attacks["spit"] = ["spit",random.randrange(70,90), (5,15)]
        super().__init__("Ooze", random.randint(50,100), attacks, 40 + random.randint(0, 10))
        self.type_name = "Ooze" 
class OoozeEvent(event.Event):

    def __init__ (self):
        self.name = " Oooze attacks."

    def process (self, world):
        result = {}
        Oooze = Oooze()
        display.announce("A giant Ooze drops from the ceiling")
        combat.Combat([Oooze]).combat()
        display.announce("The Oooze disintegrates into the air.")
        result["newevents"] = []
        result["message"] = ""
        display.announce("A mysterious weapon appears to fall from the Oozes body.")
        config.the_player.add_to_inventory([Oozeblaster()])
        return result
class Oozeblaster(Item):

    # triple shot oozeblaster.
    def __init__(self):
        super().__init__("oozeblaster", 10)
        self.damage = (25,75)
        self.firearm = True
        self.charges = 3
        self.skill = "guns"
        self.verb = "shoot"
        self.verb2 = "shoots"
        self.NUMBER_OF_ATTACKS = 3 # Number of attacks to be made in pickTargets

    def pickTargets(self, action, attacker, allies, enemies):
        if (len(enemies) <= self.NUMBER_OF_ATTACKS): # If less than or equal to three targets, hit everyone
            return enemies
        else:
            options = []
            for t in enemies:
                options.append("attack " + t.name)
            targets = []

            while(len(targets) < self.NUMBER_OF_ATTACKS): # While loop so that it keeps going until the player picks three different targets.
                display.announce(f"Pick target number {len(targets)}.", pause=False)
                choice = menu(options)
                if(not choice in targets):
                    targets.append(enemies[choice])
            return targets


class Entry_room(location.SubLocation):
    def __init__ (self, m):
        super().__init__(m)
        self.name = "room"
        self.verbs['exit'] = self
        self.verbs['leave'] = self
        self.verbs['north'] = self
        self.verbs['south'] = self
        self.verbs['east'] = self
        self.verbs['west'] = self

        self.event_chance = 100
        self.events.append(SkeletonEvent())

    def enter (self):
        description = "Hazy fog filled room with torches that are somehow still lit."
        display.announce(description)

    def process_verb (self, verb, cmd_list, nouns):
        if (verb == "south" or verb == "leave"):
            config.the_player.next_loc = self.main_location.locations["door"]
            config.the_player.go = True
        if (verb == "north"):
            config.the_player.next_loc = self.main_location.locations["armorroom"]
            config.the_player.go = True

class Skeleton(Monster):
    def __init__ (self):
        attacks = {}
        attacks["smash"] = ["smashes",random.randrange(40,90), (5,15)]
        attacks["slash"] = ["slashes",random.randrange(40,90), (5,15)]
        super().__init__("Skeleton", random.randint(25,75), attacks, 15 + random.randint(0, 10))
        self.type_name = "Skeleton" 
class SkeletonEvent(event.Event):

    def __init__ (self):
        self.name = " skeleton attack."

    def process (self, world):
        result = {}
        skeleton = Skeleton()
        display.announce("A skeleton appears to rise from the corner")
        combat.Combat([skeleton]).combat()
        display.announce("The skeleton is once again at rest.")
        result["newevents"] = []
        result["message"] = ""
        return result
    
class ArmorRoom:
    def __init__(self, m):
        super().__init__(m)
        self.name = "armorroom"
        self.verbs['north'] = self
        self.verbs['south'] = self
        self.verbs['east'] = self
        self.verbs['west'] = self
        self.verbs['pickup'] = self
        self.verbs['place'] = self
        self.pickedup = []  # Items the player has picked up
        self.floor_items = ["bascinet", "byrnie", "chausses", "aegis", "strop", "canthus", "rapier", "katana"]
        self.mannequin_items = []  # The mannequin is initially empty
        self.required_items = ["bascinet", "byrnie", "chausses"]  # Items needed to complete the mannequin

    def enter(self):
        # Generate descriptions for the floor items and mannequin state
        if len(self.floor_items) > 0:
            floor_description = f"Upon entry, you notice scattered pieces of armor: {', '.join(self.floor_items)}."
        else:
            floor_description = "The floor is empty, void of any armor or equipment."

        if len(self.mannequin_items) == 0:
            mannequin_description = "The mannequin is completely stripped of armor."
        else:
            mannequin_description = f"The mannequin is armored with the following pieces: {', '.join(self.mannequin_items)}."

        # Check if the mannequin is complete with the required items
        if all(item in self.mannequin_items for item in self.required_items):
            complete_message = "the mannequins look similar!"
        else:
            complete_message = "The mannequin is still incomplete."

        # Combine the descriptions and announce
        description = f"{floor_description} {mannequin_description} {complete_message}"
        display.announce(description)

    def process_verb(self, verb, cmd_list, nouns):
        if verb == "south":
            config.the_player.next_loc = self.main_location.locations["room"]
            config.the_player.go = True

        elif verb in ["north", "west"]:
            config.the_player.next_loc = self.main_location.locations["armorroom"]
        elif verb == "east":
            config.the_player.next_loc = self.main_location.locations["door"]
            config.the_player.go = True

        elif verb == "pickup":
            if nouns and nouns[0] in self.floor_items:
                item = nouns[0]
                self.floor_items.remove(item)
                self.pickedup.append(item)
                display.announce(f"You picked up the {item}.")
            elif nouns:
                display.announce(f"There is no {nouns[0]} on the floor.")
            else:
                display.announce("What item do you want to pick up?")
        elif verb == "place":
            if nouns and nouns[0] in self.pickedup:
                item = nouns[0]
                # Place the item on the mannequin
                self.pickedup.remove(item)
                self.mannequin_items.append(item)
                display.announce(f"You placed the {item} on the mannequin.")
                
                # Check if the mannequin is complete with the required items
                if all(required_item in self.mannequin_items for required_item in self.required_items):
                    display.announce("The mannequin is now complete with all required armor pieces!")
            else:
                display.announce("You don't have that item to place or the item isn't in your inventory.")
        else:
            display.announce("I don't understand that action.")

        


#class next_loct #north to get here #back to the beach
class Treasure_room (location.SubLocation):
    def __init__ (self, m):
        super().__init__(m)
        self.name = "Treasure"
        self.verbs['exit'] = self
        self.verbs['leave'] = self
        self.verbs['north'] = self
        self.verbs['south'] = self
        self.verbs['east'] = self
        self.verbs['west'] = self
        self.verbs["open"] = self
    
    def enter (self):
        display.announce ("You assemble the mannequin, the door opens to reveal a golden chest.")

    def process_verb (self, verb, cmd_list, nouns):
        if (verb == "south", verb == "east"):
            display.announce ("You find yourself looking at a wall.", pause=False)
        if (verb in ["north", "exit", "leave"]):
            display.announce ("You return to your ship.", pause=False)
            config.the_player.next_loc = self.main_location.locations["rockybeach"]
            self.main_location.end_visit()

        if (verb == "open"):
            display.announce ("You open the chest, and feel your body recovering as if magic!")
            for i in config.the_player.get_pirates():
                i.lucky = True
                i.sick = False
                i.health = i.max_health

