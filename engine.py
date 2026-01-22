LOGO = r"""
 __  __                         _
|  \/  | ___  _ __   ___   ___ | |__
| |\/| |/ _ \| '_ \ / _ \ / __|| '_ \
| |  | | (_) | | | | (_) | (__ | | | |
|_|  |_|\___/|_| |_|\___/ \___||_| |_|

        M O N O C H R O M E
            E N G I N E
"""

# ==============================
# MONOCHROME ENGINE
# Motor para RPG's de texto
# v0.1
# by Nico Causade
# ==============================

import json
import random
import os
import time
import sys

# =========================
# UTILIDADES
# =========================

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def pause(sec=1):
    time.sleep(sec)

def ask(options):
    options_lower = {k.lower(): k for k in options}  # mapea minúscula → clave original
    while True:
        cmd = input("> ").lower().strip()
        if cmd in options_lower:
            return options_lower[cmd]
        print("No entendés esa opción.")

# =========================
# ESTADO DEL JUEGO
# =========================

class GameState:
    def __init__(self):
        self.hp = 100
        self.flags = {}
        self.inventory = []

# =========================
# EVENTOS BASE
# =========================

def damage(state, min_dmg, max_dmg, chance=1.0):
    if random.random() <= chance:
        dmg = random.randint(min_dmg, max_dmg)
        state.hp -= dmg
        print(f"Recibís {dmg} de daño.")
        pause()

def heal(state, amount):
    state.hp += amount
    print(f"Recuperás {amount} HP.")
    pause()

def add_item(state, item):
    if item not in state.inventory:
        state.inventory.append(item)
        print(f"Obtenés: {item}")
        pause()

ITEMS = {
    "pocion": {"heal": 20},
    "pepsi": {"heal": 10},
    "mana": {"heal": 15},
    "espada": {"atk": 5}
}

def use_item(state, item):
    if item not in state.inventory:
        print("No tenés eso.")
        return

    info = ITEMS.get(item)
    if not info:
        print(f"No sabés cómo usar {item}.")
        return

    if "heal" in info:
        heal(state, info["heal"])

    # podés agregar más efectos: atk, flags, etc.
    state.inventory.remove(item)
    print(f"Usaste {item}.")

# =========================
# COMBATE POR TURNOS
# =========================

def combat(state, enemy):
    enemy_hp = enemy["hp"]
    enemy_atk = enemy["atk"]

    while enemy_hp > 0 and state.hp > 0:
        clear()
        print("COMBATE")
        print(f"Tu HP: {state.hp}")
        print(f"{enemy['name']} HP: {enemy_hp}")
        print("- atacar")
        print("- correr")

        action = input("> ").lower().strip()

        if action == "atacar":
            dmg = random.randint(5, 15)
            enemy_hp -= dmg
            print(f"Golpeás al enemigo por {dmg}.")
            pause()

            if enemy_hp > 0:
                state.hp -= enemy_atk
                print(f"{enemy['name']} te ataca ({enemy_atk}).")
                pause()

        elif action == "correr":
            print("Escapás del combate.")
            pause()
            return False

    print(f"Derrotaste a {enemy['name']}.")
    pause()
    return True

# =========================
# GUARDADO / CARGA
# =========================

def save_game(state, current_scene):
    data = {
        "hp": state.hp,
        "flags": state.flags,
        "inventory": state.inventory,
        "scene": current_scene
    }
    with open("save.json", "w") as f:
        json.dump(data, f)
    print("Juego guardado.")
    pause()

def load_game(state):
    with open("save.json") as f:
        data = json.load(f)
    state.hp = data["hp"]
    state.flags = data["flags"]
    state.inventory = data["inventory"]
    return data["scene"]

# =========================
# MOTOR PRINCIPAL
# =========================

class TextRPGEngine:
    def __init__(self, scenes, start):
        self.scenes = scenes
        self.current = start
        self.state = GameState()

    def check_death(self):
        if self.state.hp <= 0:
            print("\nCaés al suelo. Todo se vuelve oscuro...")
            print("HAS MUERTO")
            sys.exit()

    def get_valid_options(self, options):
        valid = {}
        for text, data in options.items():
            if isinstance(data, str):
                valid[text] = data
            else:
                cond = data.get("condition")
                if cond is None or eval(cond)(self.state):
                    valid[text] = data
        return valid

    def run(self):
        while True:
            clear()
            scene = self.scenes[self.current]

            if "on_enter" in scene:
                eval(scene["on_enter"])(self.state)

            self.check_death()

            print(scene["text"])
            print("\nHP:", self.state.hp)
            print("Inventario:", self.state.inventory)
            print("-" * 30)

            if not scene["options"]:
                print("FIN DEL JUEGO")
                break

            options = self.get_valid_options(scene["options"])

            for opt in options:
                print("-", opt)

            choice = ask(options)

            selected = options[choice]

            if isinstance(selected, dict) and "action" in selected:
                eval(selected["action"])
                self.check_death()

            self.current = selected if isinstance(selected, str) else selected["next"]


# =========================
# CARGA DE ESCENAS
# =========================

with open("scenes.json") as f:
    scenes = json.load(f)

# --------- MOSTRAR LOGO AL INICIO ----------
clear()                # limpia la pantalla
print(LOGO)            # imprime el logo
input("\nPresioná ENTER para comenzar...")  # pausa para que lo veas
# -------------------------------------------


engine = TextRPGEngine(scenes, "inicio")
engine.run()

