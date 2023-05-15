try:  # import as appropriate for 2.x vs. 3.x
    import tkinter as tk
    import tkinter.messagebox as tkMessageBox
except:
    import Tkinter as tk
    import tkMessageBox
import json
from tkinter import Entry


class Defender(object):
    def __init__(self):
        self.width = 20
        self.height = 20
        self.defen_id = None
        self.max_fired_bullets = 6
        self.fired_bullets = []

# Créer le defender et le centre au milieu de l'écran

    def install_in(self, canvas):
        lx = 700 - self.width/2
        ly = 800 - self.height - 10
        self.defen_id = canvas.create_rectangle(lx, ly, lx + self.width, ly + self.height, fill="white")

# Permet de récupérer les coordonnées du defender

    def coords_in(self, canvas):
        return canvas.coords(self.defen_id)

# Cette fonction est appelé à chaque fois que l'on désir déplacer le defender, dx est donné lors de l'appel de la fonction

    def move_in(self, canvas, dx):
        canvas.move(self.defen_id, dx, 0)
# Effectue le mouvement des différentes bullets sans intéragir entres elles
    def move_bullets_in(self, canvas):
        for b in self.fired_bullets:
            b.move_in(canvas)
# Enclenche le tir lorsqu'il y a moins de 8 bullet actives
    def fire(self, canvas):
        if len(self.fired_bullets) < self.max_fired_bullets:
            Bullet(self).install_in(canvas)

# ajoute dans la liste self.fired_bullets la dernière bullet tiré
    def fired(self, bullet):
        self.fired_bullets.append(bullet)
# Permet de retirer de la list 
    def remove_bullet(self, bullet):
        self.fired_bullets.remove(bullet)


class Bullet(object):
    def __init__(self, shooter):
        self.radius = 5
        self.color = "red"
        self.speed = 8
        self.bullet_id = None
        self.shooter = shooter

# Retourne l'id de la bullet
    def get_bullet_id(self):
        return self.bullet_id

    def install_in(self, canvas):
        r = self.radius
        x = self.shooter.coords_in(canvas)[0] + self.shooter.width / 2
        y = self.shooter.coords_in(canvas)[1] - r - 2
        # Créer la bullet en forme de cercle
        self.bullet_id = canvas.create_oval(x - r, y - r, x + r, y + r, fill=self.color, tags="projectile")
        # Voir commentaire ligne 46
        self.shooter.fired(self)


    def move_in(self, canvas):
        coord = canvas.coords(self.bullet_id)
        if coord[1] >= 0:
            # Effectue le mouvement de la bullet vers le haut
            canvas.move(self.bullet_id, 0, -self.speed)
        else:
            # Supprime l'affichage de la bullet
            canvas.delete(self.bullet_id)
            # Supprime de la liste fired_bullets
            self.shooter.remove_bullet(self)


class Alien(object):
    alive_image = None
    dead_image = None
# Récupère l'image d'alien vivant via le chemin relatif dans mon dossier
    @classmethod
    def get_alive_image(cls):
        '''Lazy initialization because a Tk must be created before PhotoImage'''
        if cls.alive_image == None:
            cls.alive_image = tk.PhotoImage(file='rsc/alien.gif')
        return cls.alive_image
# Récupère l'image de l'explosion via le chemin relatif dans mon dossier
    @classmethod
    def get_dead_image(cls):
        '''Lazy initialization because a Tk must be created before PhotoImage'''
        if cls.dead_image == None:
            cls.dead_image = tk.PhotoImage(file='rsc/explosion.gif')
        return cls.dead_image

    def __init__(self):
        self.alien_id = None
        self.alive = True


# Lorsqu'un alien est touché par un projectile alors, la fonction touched_by est lancé et permet récupérer les coordonnées avec la variable bbox, de suprimer l'alien touché et de 
# mettre en affichage l'image d'explosion suivant les coordonnées en x et y via bbox[0] pour x et bbox[1] pour y.
    def touched_by(self, canvas, projectile):
        self.alive = False
        bbox = canvas.coords(self.get_alien_id())
        canvas.delete(self.get_alien_id())
        self.install_dead_in(canvas, bbox[0], bbox[1])

# récupère l'id de l'alien
    def get_alien_id(self):
        return self.alien_id
# fonction appelé dansles deux fonctions (install_alive_in et install_dead_in)
    def install_in(self, canvas, x, y, image, tag):
        self.alien_id = canvas.create_image(x, y, image=image, tags=tag)
# Créer l'alien en utilisant son image récupéré dans la fonction get_alive_image
    def install_alive_in(self, canvas, x, y):
        self.install_in(canvas, x, y, Alien.get_alive_image(), "alive_alien")
# Créer l'explosion de l'alien en utilisant son image récupéré dans la fonction get_alive_image
    def install_dead_in(self, canvas, x, y):
        self.install_in(canvas, x, y, Alien.get_dead_image(), "dead_alien")
        canvas.after(300, self.clean, canvas, self.get_alien_id())
# Fonction appelé pour le mouvement de l'alien de gauche à droite et vers le bas suivant les paramètres rentré
    def move_in(self, canvas, dx, dy):
        if self.alive:
            canvas.move(self.get_alien_id(), dx, dy)
# Retire l'image de l'explosion de l'alien
    def clean(self, canvas, canvas_id):
        canvas.delete(canvas_id)


class Fleet(object):
    def __init__(self):
        ''' Aliens '''
        self.aliens_lines = 5
        self.aliens_columns = 10
        self.aliens_down = 20
        self.alien_x = 5
        self.alien_y = 15
        self.aliens_fleet = [None] * (self.aliens_lines * self.aliens_columns)
        self.score=Score()
        self.texte =""

# Créer l'ensemble d'alien grouper sur self.aliens_lines = 5 donc 5 lignes et self.aliens_columns = 10 donc 10 colonnes ce qui fait 50 aliens sur 5 lignes de 10 aliens
    def install_in(self, canvas):
        x = 50
        y = self.aliens_down

        self.texte = canvas.create_text(10, 20, anchor="w", text="Votre score : "+str(self.score.get_point()),
                        font=('Arial', 25, 'bold italic'), fill="yellow")          

        for i in range(len(self.aliens_fleet)):
            if (i % self.aliens_columns == 0):
                y = y + Alien.get_alive_image().height() + self.aliens_down
                x = 50
            alien = Alien()
            alien.install_alive_in(canvas, x, y)
            self.aliens_fleet[i] = alien
            x = x + Alien.get_alive_image().width() + self.aliens_down

# Permet d'afficher le score actif en haut à gauche de la fenetre de jeu
    def result_score(self, score, canvas):
        score = "Votre score : "+str(score)
        return canvas.create_text(10, 20, anchor="w", text=score,
                font=('Arial', 25, 'bold italic'), fill="yellow")  

    def move_in(self, canvas):
        bbox = canvas.bbox("alive_alien")
        if bbox == None: return
        cwidth = int(canvas.cget("width"))

        y_delta = 0
        if (self.alien_x > 0):
            if (bbox[2] >= cwidth):
                self.alien_x = self.alien_x * -1
                y_delta = self.alien_y
        else:
            if (bbox[0] < 0):
                self.alien_x = self.alien_x * -1
                y_delta = self.alien_y

        for alien in self.aliens_fleet:
            alien.move_in(canvas, self.alien_x, y_delta)

# Vérifie les coordonnées des bullets actives afin de déterminé si elle touche un aliens et si elle touche une aliens alors lance la fonction touched_by par rapport à l'alien touché
    def manage_touched_aliens_by(self, canvas, defender):
        bullets = defender.fired_bullets
        for bull in list(bullets):
            x1, y1, x2, y2 = canvas.coords(bull.get_bullet_id())
            touched = canvas.find_overlapping(x1, y1, x2, y2)
            for alien in self.aliens_fleet:
                if alien.alive and alien.get_alien_id() in touched:
                    alien.touched_by(canvas, defender)
                    bullets.remove(bull)
                    canvas.delete(bull.get_bullet_id())
                    canvas.delete(self.texte)
                    # Incrémente le score de 100 à chaques alien touché
                    self.score.set_point(self.score.get_point() +100)
                    self.texte = self.result_score(self.score.get_point(), canvas)
                    
        
                    
class Score(object):
    def __init__(self):
        self.joueur="Joueur 1"
        self.point= 0

    def get_joueur(self):
        return self.joueur

    def get_point(self):
        return self.point

    def set_joueur(self, new_joueur):
        self.joueur=new_joueur

    def set_point(self, new_point):
        self.point=new_point

    def toFile(self, fichier):
        f = open(fichier, "w")
        l=self
        json.dump(l.__dict__,f)
        f.close()
    '''
    @classmethod
    def fromFile(cls, fichier):
        f = open(fichier,"r")
        d = json.load(f)
        lnew=Score(d["joueur"],d["point"])
        f.close()
        return lnew
    def __str__(self):
        return str(self.joueur) + str(self.point)
    '''

class Game(object):
    def __init__(self, frame):
        self.frame = frame
        self.fleet = Fleet()
        self.defender = Defender()

# Taille de l'écran en largeur et hauteur pour créer le canvas
        self.height = 800
        self.width = 1400
        self.canvas = tk.Canvas(self.frame, width=self.width, height=self.height, bg="black")
        self.canvas.pack(side="top", fill="both", expand=True)
        # Installation defender et fleet + mise en place détection touches
        self.defender.install_in(self.canvas)
        self.fleet.install_in(self.canvas)
        self.frame.winfo_toplevel().bind("<Key>", self.keypressed)

    def keypressed(self, event):
        x = 0
        x1, y1, x2, y2 = self.canvas.coords(self.defender.defen_id)
        if (x1>20):
            if event.keysym == 'Left':
                x = -20
        if (x2< 1380):
            if event.keysym == 'Right':
                x = 20
        if event.keysym == 'space':
            self.defender.fire(self.canvas)
        self.defender.move_in(self.canvas, x)

    def start_animation(self):
        self.animation_on = True
        self.frame.after(30, self.animation)

    def stop_animation(self):
        self.animation_on = False

    def result_message(self, message):
        self.canvas.create_text(self.width / 3, self.height / 3, anchor="w", text=message,
                                font=('Arial', 100, 'bold italic'), fill="yellow")

    def animation(self):
        if not self.animation_on: return
        self.fleet.manage_touched_aliens_by(self.canvas, self.defender)
        self.fleet.move_in(self.canvas)
        self.defender.move_bullets_in(self.canvas)
        result = self.result()
        if result == "playing":
            self.frame.after(30, self.animation)
        elif result == "successful":
            self.result_message("Victoire")
            self.fleet.score.toFile("score.json")
        else:
            self.result_message("Perdu")
            self.fleet.score.toFile("score.json")


    def result(self):
        
        alive_aliens = self.canvas.find_withtag("alive_alien")
        if (len(alive_aliens) == 0): return "successful"
        fleet_bbox = self.canvas.bbox("alive_alien")
        # Vérifie si les aliens atteint la hauteur du defender et si c'est le cas alors result de la fonction animation reçoit du return "lost"
        if (fleet_bbox[3] >= (self.defender.coords_in(self.canvas)[1])):
            return "lost"
        return "playing"

        '''
        res ="playing"
        if (len(alive_aliens) == 0):
            res = "successful"
        fleet_bbox = self.canvas.bbox("alive_alien")
        if (fleet_bbox[3] >= (self.defender.coords_in(self.canvas)[1])):
            res ="lost"
        
        return res
        
        '''


class SpaceInvaders(object):

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Space Invaders")
        self.root.protocol("WM_DELETE_WINDOW", self.ask_quit)
        self.frame = tk.Frame(self.root)
        self.frame.pack(side="top", fill="both", expand=True)
        self.game = Game(self.frame)
        # Test pour la solution expliqué plus bas
        '''
        self.fenetreName = tk.Tk()
        self.fenetreName.title("Entrez votre Nom : ")
        self.fenetreNameCanvas = tk.Canvas(self.fenetreName, width=500, height=100, bg="white")
        '''
    def ask_quit(self):
        self.game.stop_animation()
        if self.game.result() == "playing":
            if tkMessageBox.askokcancel("Quit", "Voulez-vous vraiment quitter ?"):
                self.root.destroy()
                self.game.fleet.score.toFile("score.json")
            else:
                self.game.start_animation()

        else:
            self.root.destroy()



    def play(self):
        # Appel la fonction start_animation() qui est dans Game() et lance la partie
        '''
        self.ask_name()
        '''
        self.game.start_animation()
        self.root.mainloop()

# On voulait afficher une deuxième fenetre qui aurait permit de rentrez le prenom de la personne pour la partie, la partie se lance lorsque le prenom est enregistrer
'''''
    def closeFenetre(self):
        self.game.start_animation()
        self.fenetreName.destroy()

    def takeName(self, takeName):
        if takeName!="":
            self.game.fleet.score.set_joueur(takeName)
            self.closeFenetre()

    def ask_name(self):
        self.fenetreName.geometry('400x100')
        name = Entry(self.fenetreName, font=("arial", 20))
        btn = tk.Button(self.fenetreName, text=" Enregistrer ", command=self.takeName(name))
        name.pack()
        btn.pack()
'''''


SpaceInvaders().play()


