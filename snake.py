# Wir benutzen die Bibliothek pygame – damit kann man ganz einfach Spiele programmieren!
from pygame.locals import *
import pygame

# Damit unser Apfel an zufälligen Stellen erscheinen kann
from random import randint

# Zeit-Funktion – damit das Spiel nicht zu schnell läuft
import time

# Damit wir Bilder aus dem Internet laden können
from io import BytesIO
import requests

# 🍎 Apfel-Klasse – der Apfel, den die Schlange fressen soll
class Apple:
    x = 0  # x-Position des Apfels
    y = 0  # y-Position des Apfels
    step = 44  # Ein Schritt im Spielfeld ist 44 Pixel groß

    def __init__(self, x, y):
        # Der Apfel wird an einer bestimmten Stelle erzeugt
        self.x = x * self.step
        self.y = y * self.step

    def draw(self, surface, image):
        # Der Apfel wird auf dem Spielfeld angezeigt
        surface.blit(image, (self.x, self.y))


# 🐍 Schlange-Klasse – hier passiert die Bewegung der Schlange
class Player:
    x = [0]  # x-Positionen der einzelnen Körperteile
    y = [0]  # y-Positionen der einzelnen Körperteile
    step = 44  # Ein Schritt ist 44 Pixel
    direction = 0  # Start-Richtung: 0 = rechts, 1 = links, 2 = oben, 3 = unten
    length = 3  # Die Schlange startet mit 3 Segmenten

    updateCountMax = 2  # Geschwindigkeit: Je kleiner die Zahl, desto schneller
    updateCount = 0

    def __init__(self, length):
        self.length = length

        # Die Schlange hat am Anfang 2000 leere Körperteile, die weit weg liegen
        for i in range(0, 2000):
            self.x.append(-100)
            self.y.append(-100)

        # Die ersten drei Körperteile haben Start-Positionen
        self.x[1] = 1 * 44
        self.x[2] = 2 * 44

    def update(self):
        # Die Schlange wird nur manchmal bewegt, nicht bei jedem Schleifendurchlauf
        self.updateCount = self.updateCount + 1
        if self.updateCount > self.updateCountMax:
            # Die Körperteile folgen dem Kopf
            for i in range(self.length - 1, 0, -1):
                self.x[i] = self.x[i - 1]
                self.y[i] = self.y[i - 1]

            # Kopf bewegen je nach Richtung
            if self.direction == 0:  # Rechts
                self.x[0] = self.x[0] + self.step
            if self.direction == 1:  # Links
                self.x[0] = self.x[0] - self.step
            if self.direction == 2:  # Oben
                self.y[0] = self.y[0] - self.step
            if self.direction == 3:  # Unten
                self.y[0] = self.y[0] + self.step

            self.updateCount = 0  # Zähler zurücksetzen

    # Bewegungsfunktionen – hier wird die Richtung geändert
    def moveRight(self):
        if self.direction != 1:  # Nur wenn die Schlange nicht nach links geht
            self.direction = 0

    def moveLeft(self):
        if self.direction != 0:
            self.direction = 1

    def moveUp(self):
        if self.direction != 3:
            self.direction = 2

    def moveDown(self):
        if self.direction != 2:
            self.direction = 3

    def draw(self, surface, image):
        # Die Schlange wird auf das Spielfeld gezeichnet
        for i in range(0, self.length):
            surface.blit(image, (self.x[i], self.y[i]))


# 🔍 Spielregeln – Kollisionen prüfen
class Game:
    # Prüfen, ob der Kopf der Schlange ein Körperteil berührt
    def isCollision(self, x1, y1, x2, y2, bsize):
        if x1 >= x2 and x1 <= x2 + bsize:
            if y1 >= y2 and y1 <= y2 + bsize:
                return True
        return False

    # Prüfen, ob die Schlange den Apfel gefressen hat
    def isCollision_apple(self, x1, y1, x2, y2, bsize):
        return x1 == x2 and y1 == y2


# 🎮 Haupt-Spielklasse – hier läuft das Spiel ab
class App:
    windowWidth = 800
    windowHeight = 600
    player = 0
    apple = 0

    def __init__(self):
        self._running = True
        self._display_surf = None
        self._image_surf = None
        self._apple_surf = None
        self.game = Game()
        self.player = Player(3)
        self.apple = Apple(5, 5)

    def on_init(self):
        # Pygame starten
        pygame.init()
        self._display_surf = pygame.display.set_mode((self.windowWidth, self.windowHeight), pygame.HWSURFACE)
        pygame.display.set_caption('S N A K E')

        self._running = True

        # Bilder aus dem Internet laden
        response = requests.get('https://i.ibb.co/wNRPxg2G/apple.png')
        self._image_surf = pygame.image.load(BytesIO(response.content)).convert()

        response = requests.get('https://i.ibb.co/WpRSLqzY/block.png')
        self._apple_surf = pygame.image.load(BytesIO(response.content)).convert()

    def on_event(self, event):
        # Prüfen, ob das Fenster geschlossen wurde
        if event.type == QUIT:
            self._running = False

    def on_loop(self):
        # Schlange bewegen
        self.player.update()

        # Prüfen, ob die Schlange den Apfel gefressen hat
        for i in range(0, self.player.length):
            if self.game.isCollision_apple(self.apple.x, self.apple.y, self.player.x[i], self.player.y[i], 44):
                # Neuer Apfel an zufälliger Stelle
                self.apple.x = randint(2, 9) * 44
                self.apple.y = randint(2, 9) * 44
                # Die Schlange wird länger
                self.player.length = self.player.length + 1

        # Prüfen, ob die Schlange sich selbst berührt
        for i in range(2, self.player.length):
            if self.game.isCollision(self.player.x[0], self.player.y[0], self.player.x[i], self.player.y[i], 40):
                print("Du hast dich selbst berührt – verloren!")
                print("Deine Länge: " + str(self.player.length))
                exit(0)

        # Prüfen, ob die Schlange gegen die Wand läuft – dann auf der anderen Seite weiter
        cols = self.windowWidth // self.player.step
        rows = self.windowHeight // self.player.step

        if self.player.x[0] < 0:
            self.player.x[0] = self.windowWidth - 44
        if self.player.x[0] > self.windowWidth - 44:
            self.player.x[0] = 0
        if self.player.y[0] < 0:
            self.player.y[0] = self.windowHeight - 44
        if self.player.y[0] > self.windowHeight - 44:
            self.player.y[0] = 0

        # Auf Raster-Koordinaten anpassen (sauberes Einrasten)
        self.player.x[0] = (self.player.x[0] // self.player.step) % cols * self.player.step
        self.player.y[0] = (self.player.y[0] // self.player.step) % rows * self.player.step

    def on_render(self):
        # Spielfeld leeren (schwarz)
        self._display_surf.fill((0, 0, 0))
        # Schlange und Apfel zeichnen
        self.player.draw(self._display_surf, self._image_surf)
        self.apple.draw(self._display_surf, self._apple_surf)
        # Bildschirm aktualisieren
        pygame.display.flip()

    def on_cleanup(self):
        # Spiel beenden
        pygame.quit()

    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        while self._running:
            pygame.event.pump()
            keys = pygame.key.get_pressed()

            # Steuerung: Mit den Pfeiltasten bewegen
            if keys[K_RIGHT]:
                self.player.moveRight()
            if keys[K_LEFT]:
                self.player.moveLeft()
            if keys[K_UP]:
                self.player.moveUp()
            if keys[K_DOWN]:
                self.player.moveDown()

            # Mit ESC das Spiel beenden
            if keys[K_ESCAPE]:
                self._running = False

            self.on_loop()
            self.on_render()

            # Kleine Pause – sonst läuft das Spiel zu schnell
            time.sleep(80.0 / 1000.0)

        self.on_cleanup()


# Hier startet das Spiel
if __name__ == "__main__":
    theApp = App()
    theApp.on_execute()