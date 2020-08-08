# Soldier

class Soldier():
    def __init__(self, health, strength):
        self.health = health 
        self.strength = strength

    def attack(self):
        return self.strength

    def receiveDamage(self,the_damage):
        self.health = self.health-the_damage


# Viking

class Viking(Soldier):
    def __init__(self, name, health, strength):
        self.name = name
        Soldier.health = health 
        Soldier.strength = strength
    
    def receiveDamage(self,the_damage):
        self.health = self.health-the_damage
        if self.health > 0:
            return f"{self.name} has received {the_damage} points of damage"
        else:
            return f"{self.name} has died in act of combat"
    
    def battleCry(self):
        return "Odin Owns You All!"


# Saxon

class Saxon(Soldier):
    def __init__(self, health, strength):
        Soldier.__init__(self, health, strength)

    def receiveDamage(self,the_damage):
        self.health = self.health-the_damage
        if self.health > 0:
            return f"A Saxon has received {the_damage} points of damage"
        else:
            return "A Saxon has died in combat"


# War


class War():
    def __init__(self):
        self.vikingArmy = []
        self.saxonArmy = []
        
    def addViking(self, viking):
        self.vikingArmy.append(viking)

    def addSaxon(self, saxon):
        self.saxonArmy.append(saxon)

    def vikingAttack(self):
        viking = self.vikingArmy[0]
        saxon = self.saxonArmy[0]
        damage = saxon.receiveDamage(viking.attack())
        if saxon.health <= 0:
            self.saxonArmy.pop(0)
        return damage

    def saxonAttack(self):
        viking = self.vikingArmy[0]
        saxon = self.saxonArmy[0]
        damage = viking.receiveDamage(saxon.attack())
        if viking.health <= 0:
            self.vikingArmy.pop(0)
        return damage

    def showStatus(self):
        if len(self.saxonArmy) == 0:
            return "Vikings have won the war of the century!"
        elif len(self.vikingArmy) == 0:
            return "Saxons have fought for their lives and survive another day..."
        elif len(self.saxonArmy) >= 1 and len(self.vikingArmy) >= 1:
            return "Vikings and Saxons are still in the thick of battle."