from tkinter import *
from tkinter import messagebox
from datetime import datetime
from PIL import Image, ImageTk
import json, os
from collections import deque

# ============================================================
# CLASSE NOEUD : représente un match dans l'arbre binaire
# ============================================================

class NoeudMatch:
    """Représente un match (noeud) dans l'arbre binaire du tournoi."""
    def __init__(self, equipe1=None, equipe2=None, tour=0, index=0):
        self.equipe1 = equipe1
        self.equipe2 = equipe2
        self.score1 = None
        self.score2 = None
        self.vainqueur = None
        self.gauche = None
        self.droite = None
        self.tour = tour
        self.index = index
        self.cote = None

    def __repr__(self):
        return f"Match({self.equipe1}/{self.equipe2}, gagnant={self.vainqueur})"

    # ==================== MÉTHODES D'ARBRE BINAIRE ====================

    def affiche_infixe(self):
        """Parcours infixe (Gauche-Racine-Droite) : affiche les équipes gagnantes en ordre de tour."""
        if self.gauche is not None:
            self.gauche.affiche_infixe()
        if self.vainqueur:
            print(f"Tour {self.tour}: {self.vainqueur}", end=' | ')
        if self.droite is not None:
            self.droite.affiche_infixe()

    def affiche_prefixe(self):
        """Parcours préfixe (Racine-Gauche-Droite) : affiche le noeud avant ses enfants."""
        print(f"Match(T{self.tour}#{self.index}: {self.equipe1 or '?'} vs {self.equipe2 or '?'})", end=' → ')
        if self.gauche is not None:
            self.gauche.affiche_prefixe()
        if self.droite is not None:
            self.droite.affiche_prefixe()

    def affiche_postfixe(self):
        """Parcours postfixe (Gauche-Droite-Racine) : affiche les enfants avant la racine."""
        if self.gauche is not None:
            self.gauche.affiche_postfixe()
        if self.droite is not None:
            self.droite.affiche_postfixe()
        print(f"Match(T{self.tour}#{self.index})", end=' → ')

    def affiche_largeur(self):
        """Parcours en largeur : affiche tous les matchs niveau par niveau."""
        from collections import deque
        file = deque([self])
        resultat = []
        while file:
            noeud = file.popleft()
            resultat.append(f"T{noeud.tour}#{noeud.index}")
            if noeud.gauche is not None:
                file.append(noeud.gauche)
            if noeud.droite is not None:
                file.append(noeud.droite)
        return " → ".join(resultat)

    def hauteur(self):
        """Retourne la hauteur de l'arbre (nombre maximum de niveaux)."""
        if self is None:
            return 0
        return 1 + max(self.gauche.hauteur() if self.gauche else 0,
                       self.droite.hauteur() if self.droite else 0)

    def taille(self):
        """Retourne le nombre total de noeuds dans l'arbre."""
        if self is None:
            return 0
        return 1 + (self.gauche.taille() if self.gauche else 0) + (self.droite.taille() if self.droite else 0)

    def compte_feuilles(self):
        """Retourne le nombre de feuilles (matchs sans enfants)."""
        if self.gauche is None and self.droite is None:
            return 1
        compte = 0
        if self.gauche:
            compte += self.gauche.compte_feuilles()
        if self.droite:
            compte += self.droite.compte_feuilles()
        return compte

    def recherche_equipe(self, nom_equipe):
        """Recherche une équipe dans l'arbre et retourne le match où elle apparaît."""
        if self.equipe1 == nom_equipe or self.equipe2 == nom_equipe:
            return self
        
        resultat = None
        if self.gauche:
            resultat = self.gauche.recherche_equipe(nom_equipe)
        if not resultat and self.droite:
            resultat = self.droite.recherche_equipe(nom_equipe)
        return resultat

# ============================================================
# DONNÉES : équipes, configuration des tours, fichier de sauvegarde
# ============================================================

EQUIPES = [
    "Real Madrid", "FC Barcelona", "Atlético Madrid", "Sevilla FC",
    "Manchester United", "Liverpool FC", "Chelsea FC", "Arsenal FC",
    "Manchester City", "Tottenham Hotspur", "Newcastle United", "Aston Villa",
    "Bayern Munich", "Borussia Dortmund", "RB Leipzig", "Bayer Leverkusen",
    "Paris Saint-Germain", "Olympique de Marseille", "Olympique Lyonnais", "AS Monaco",
    "Lille OSC", "Stade Rennais", "OGC Nice", "RC Lens",
    "Juventus", "Inter Milan", "AC Milan", "AS Roma",
    "Napoli", "Lazio", "Atalanta", "Fiorentina",
    "Ajax Amsterdam", "PSV Eindhoven", "Feyenoord", "AZ Alkmaar",
    "FC Porto", "Benfica", "Sporting CP", "Braga",
    "Celtic", "Rangers", "Galatasaray", "Fenerbahce",
    "Besiktas", "Olympiacos", "Panathinaikos", "AEK Athens",
    "Club Brugge", "Anderlecht", "Red Bull Salzburg", "Rapid Vienna",
    "Shakhtar Donetsk", "Dynamo Kyiv", "Zenit Saint Petersburg", "CSKA Moscow",
    "Flamengo", "Palmeiras", "Boca Juniors", "River Plate",
    "LA Galaxy", "Inter Miami", "Al Hilal", "Al Nassr"
]

# Noms des tours et nombre de matchs par tour
NOMS_TOURS = ["32èmes", "16èmes", "8èmes", "Quarts", "Demis"]
NB_MATCHS  = [16, 8, 4, 2, 1]

FICHIER_CACHE = "tournoi_cache.json"

# ============================================================
# VARIABLES GLOBALES : arbres du tournoi et historique
# ============================================================

arbres_bracket = {"G": None, "D": None}
finale_bracket = None
historique = []

# ============================================================
# COULEURS
# ============================================================

BG        = "#000000"   # fond fenêtre
BG_CANVAS = "#000000"   # fond canvas
C_VIDE    = "#000000"   # match non joué
C_JOUE    = "#1a4a1a"   # match joué
C_BLANC   = "#FFFFFF"
C_OR      = "#ffd700"

# ============================================================
# INITIALISATION : création de tous les matchs du tournoi
# ============================================================

def creer_feuilles_arbre(cote, decalage):
    feuilles = []
    for i in range(16):
        e1 = EQUIPES[decalage + i * 2]
        e2 = EQUIPES[decalage + i * 2 + 1]
        noeud = NoeudMatch(e1, e2, tour=0, index=i)
        noeud.cote = cote
        feuilles.append(noeud)
    return feuilles

def creer_arbre_depuis_feuilles(feuilles, cote):
    niveaux = [feuilles]
    
    # Construire chaque niveau suivant
    for tour in range(1, 5):
        niveau_precedent = niveaux[-1]
        nouveau_niveau = []
        for i in range(0, len(niveau_precedent), 2):
            noeud = NoeudMatch(None, None, tour=tour, index=i // 2)
            noeud.cote = cote
            noeud.gauche = niveau_precedent[i]
            noeud.droite = niveau_precedent[i + 1]
            nouveau_niveau.append(noeud)
        niveaux.append(nouveau_niveau)
    
    # La racine est le dernier noeud du dernier niveau
    return niveaux[-1][0]

def init():
    global arbres_bracket, finale_bracket, historique
    historique = []
    
    for cote in ["G", "D"]:
        decalage = 0 if cote == "G" else 32
        feuilles = creer_feuilles_arbre(cote, decalage)
        arbres_bracket[cote] = creer_arbre_depuis_feuilles(feuilles, cote)
    
    finale_bracket = NoeudMatch(None, None, tour=5, index=0)
    finale_bracket.cote = "F"

# ============================================================
# SAUVEGARDE / CHARGEMENT / RESET
# ============================================================

def serialiser_noeud(noeud):
    if noeud is None:
        return None
    return {
        "equipe1": noeud.equipe1,
        "equipe2": noeud.equipe2,
        "score1": noeud.score1,
        "score2": noeud.score2,
        "vainqueur": noeud.vainqueur,
        "tour": noeud.tour,
        "index": noeud.index,
        "cote": noeud.cote,
        "gauche": serialiser_noeud(noeud.gauche),
        "droite": serialiser_noeud(noeud.droite)
    }

def deserialiser_noeud(data):
    if data is None:
        return None
    noeud = NoeudMatch(
        equipe1=data["equipe1"],
        equipe2=data["equipe2"],
        tour=data["tour"],
        index=data["index"]
    )
    noeud.score1 = data["score1"]
    noeud.score2 = data["score2"]
    noeud.vainqueur = data["vainqueur"]
    noeud.cote = data["cote"]
    noeud.gauche = deserialiser_noeud(data["gauche"])
    noeud.droite = deserialiser_noeud(data["droite"])
    return noeud

def sauvegarder():
    data = {
        "arbres_bracket": {cote: serialiser_noeud(arbres_bracket[cote]) for cote in ["G", "D"]},
        "finale_bracket": serialiser_noeud(finale_bracket),
        "historique": historique
    }
    with open(FICHIER_CACHE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def charger():
    global arbres_bracket, finale_bracket, historique
    if not os.path.exists(FICHIER_CACHE):
        return False
    try:
        with open(FICHIER_CACHE, "r", encoding="utf-8") as f:
            data = json.load(f)
        arbres_bracket["G"] = deserialiser_noeud(data["arbres_bracket"]["G"])
        arbres_bracket["D"] = deserialiser_noeud(data["arbres_bracket"]["D"])
        finale_bracket = deserialiser_noeud(data["finale_bracket"])
        historique = data.get("historique", [])
        return True
    except:
        return False

def reset():
    if not messagebox.askyesno("Réinitialiser", "Tout effacer ?", icon="warning"):
        return
    init()
    if os.path.exists(FICHIER_CACHE):
        os.remove(FICHIER_CACHE)
    dessiner()
    messagebox.showinfo("OK", "Tournoi réinitialisé.")

# ============================================================
# LOGIQUE TOURNOI : propagation du vainqueur au tour suivant
# ============================================================

def trouver_parent_et_slot(racine, cible, cote):
    """Trouve le parent d'un noeud et son slot (0=gauche, 1=droite)."""
    if racine is None or racine == cible:
        return None, None
    
    if racine.gauche == cible:
        return racine, 0
    if racine.droite == cible:
        return racine, 1
    
    parent, slot = trouver_parent_et_slot(racine.gauche, cible, cote)
    if parent:
        return parent, slot
    
    return trouver_parent_et_slot(racine.droite, cible, cote)

def propager(noeud, cote, vainqueur):
    if cote == "F":
        return
    
    # Trouver le noeud parent dans l'arbre
    racine = arbres_bracket[cote]
    parent, slot = trouver_parent_et_slot(racine, noeud, cote)
    
    if parent is None:
        # Le noeud est la racine du côté, le vainqueur va à la finale
        if cote == "G":
            finale_bracket.equipe1 = vainqueur
        else:
            finale_bracket.equipe2 = vainqueur
    else:
        # Placer le vainqueur dans le parent
        if slot == 0:
            parent.equipe1 = vainqueur
        else:
            parent.equipe2 = vainqueur
        
        # Propager récursivement au parent du parent
        propager(parent, cote, vainqueur)

# ============================================================
# POPUP SAISIE DE SCORE
# ============================================================

def ouvrir_match(noeud, cote):
    if noeud is None:
        return

    e1 = noeud.equipe1 or "TBD"
    e2 = noeud.equipe2 or "TBD"

    # On ne peut pas jouer si une équipe n'est pas encore qualifiée
    if e1 == "TBD" or e2 == "TBD":
        return None

    nom_tour = "Finale" if cote == "F" else NOMS_TOURS[noeud.tour]

    # Création de la fenêtre popup
    popup = Toplevel(fenetre)
    popup.title(f"{nom_tour} — Match {noeud.index+1}")
    popup.geometry("430x260")
    popup.resizable(False, False)
    popup.configure(bg=BG)

    # Champs de saisie
    Label(popup, text=nom_tour, bg=BG, fg="white", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(15, 5))
    Label(popup, text="Date (JJ/MM/YYYY):", bg=BG, fg="white").grid(row=1, column=0, padx=15, pady=8, sticky=W)
    champ_date = Entry(popup, width=18)
    champ_date.grid(row=1, column=1, padx=10, pady=8, sticky=W)
    champ_date.insert(0, datetime.now().strftime("%d/%m/%Y"))

    Label(popup, text=f"{e1} :", bg=BG, fg="white", font=("Arial", 10, "bold")).grid(row=2, column=0, padx=15, pady=8, sticky=W)
    champ_s1 = Entry(popup, width=5, font=("Arial", 12))
    champ_s1.grid(row=2, column=1, padx=10, pady=8, sticky=W)

    Label(popup, text=f"{e2} :", bg=BG, fg="white", font=("Arial", 10, "bold")).grid(row=3, column=0, padx=15, pady=8, sticky=W)
    champ_s2 = Entry(popup, width=5, font=("Arial", 12))
    champ_s2.grid(row=3, column=1, padx=10, pady=8, sticky=W)

    if noeud.score1 is not None:
        champ_s1.insert(0, str(noeud.score1))
    if noeud.score2 is not None:
        champ_s2.insert(0, str(noeud.score2))

    def valider():
        """Vérifie le score, met à jour le match et propage le vainqueur."""
        try:
            s1 = int(champ_s1.get())
            s2 = int(champ_s2.get())
        except ValueError:
            messagebox.showerror("Erreur", "Scores entiers requis.")
            return
        if s1 == s2:
            messagebox.showerror("Erreur", "Pas d'égalité !")
            return

        vainqueur = e1 if s1 > s2 else e2
        noeud.score1 = s1
        noeud.score2 = s2
        noeud.vainqueur = vainqueur

        historique.append({"date": champ_date.get(), "equipe1": e1, "equipe2": e2, "score1": s1, "score2": s2})
        propager(noeud, cote, vainqueur)
        sauvegarder()
        dessiner()
        popup.destroy()

        if cote == "F":
            messagebox.showinfo("Champion !", f"Le champion est :\n\n{vainqueur}")

    cadre = Frame(popup, bg=BG)
    cadre.grid(row=4, column=0, columnspan=2, pady=18)
    Button(cadre, text="Valider",  command=valider,        bg="#4CAF50", fg="white", font=("Arial", 11), padx=15).pack(side=LEFT, padx=8)
    Button(cadre, text="Annuler", command=popup.destroy,   bg="#f44336", fg="white", font=("Arial", 11), padx=15).pack(side=LEFT, padx=8)

# ============================================================
# STATISTIQUES : top 3 des équipes ayant marqué le plus de buts
# ============================================================

def top3_buts():
    noms_equipes = []
    totaux_buts  = []

    for m in historique:
        # Equipe 1
        if m["equipe1"] in noms_equipes:
            i = noms_equipes.index(m["equipe1"])
            totaux_buts[i] += m["score1"]
        else:
            noms_equipes.append(m["equipe1"])
            totaux_buts.append(m["score1"])

        # Equipe 2
        if m["equipe2"] in noms_equipes:
            i = noms_equipes.index(m["equipe2"])
            totaux_buts[i] += m["score2"]
        else:
            noms_equipes.append(m["equipe2"])
            totaux_buts.append(m["score2"])

    if len(noms_equipes) == 0:
        messagebox.showinfo("Top 3", "Aucun match joué.")
        return

    for i in range(len(totaux_buts)):
        for j in range(i + 1, len(totaux_buts)):
            if totaux_buts[j] > totaux_buts[i]:
                totaux_buts[i],   totaux_buts[j]  = totaux_buts[j],  totaux_buts[i]
                noms_equipes[i], noms_equipes[j] = noms_equipes[j], noms_equipes[i]

    msg = "TOP 3 MEILLEURES ATTAQUES\n\n"
    for rang in range(min(3, len(noms_equipes))):
        msg += f"{rang+1}. {noms_equipes[rang]} : {totaux_buts[rang]} buts\n"
    messagebox.showinfo("Statistiques", msg)

# ============================================================
# DESSIN : affichage du bracket sur le canvas
# ============================================================

def couleur_rect(noeud):
    """Retourne la couleur du rectangle selon l'état du match."""
    if noeud is None or not noeud.equipe1 or not noeud.equipe2:
        return C_VIDE
    if noeud.vainqueur:
        return C_JOUE      # match terminé
    return C_VIDE          # match à jouer

def texte_slot(noeud, slot):
    """Retourne le texte à afficher dans un slot (equipe + score éventuel)."""
    if noeud is None:
        return "?"
    if slot == 0:
        equipe = noeud.equipe1 or "?"
        score  = noeud.score1
    else:
        equipe = noeud.equipe2 or "?"
        score  = noeud.score2

    if score is not None:
        return f"{equipe[:13]} {score}"
    return equipe[:13]

def collecter_noeuds_par_tour(racine, tour_cible):
    """Collecte tous les noeuds d'un tour donné (parcours en largeur)."""
    if racine is None:
        return []
    
    file = deque([racine])
    noeuds_tour = []
    
    while file:
        noeud = file.popleft()
        if noeud.tour == tour_cible:
            noeuds_tour.append(noeud)
        
        # Ajouter les enfants (on les traite en largeur)
        if noeud.gauche:
            file.append(noeud.gauche)
        if noeud.droite:
            file.append(noeud.droite)
    
    noeuds_tour.sort(key=lambda n: n.index)
    return noeuds_tour

def dessiner(event=None):
    """Redessine tout le bracket (appelé à chaque changement ou redimensionnement)."""
    global photo_fond
    canvas.delete("all")
    L = canvas.winfo_width()
    H = canvas.winfo_height()
    if L < 10 or H < 10:
        return

    # Image de fond (redimensionnée à la taille du canvas)
    try:
        photo_fond = ImageTk.PhotoImage(image_fond.resize((L, H), Image.LANCZOS))
        canvas.create_image(0, 0, anchor=NW, image=photo_fond)
    except:
        pass

    COL_L  = L * 0.44 / 5
    BOX_W  = COL_L * 0.84
    SLOT_H = (H * 0.98) / 16
    BOX_H  = SLOT_H * 0.30
    GAP    = SLOT_H * 0.05
    fp     = max(int(BOX_H * 0.58), 5)
    pol    = ("Arial", fp)
    pol_f  = ("Arial", max(fp + 1, 6), "bold")
    pol_l  = ("Arial", max(fp + 2, 7), "bold")

    pos = []
    pos_tour0 = []
    for i in range(16):
        pos_tour0.append(H * 0.01 + i * SLOT_H + SLOT_H / 2)
    pos.append(pos_tour0)

    for t in range(1, 5):
        pos_tourt = []
        for i in range(NB_MATCHS[t]):
            centre = (pos[t-1][i*2] + pos[t-1][i*2+1]) / 2
            pos_tourt.append(centre)
        pos.append(pos_tourt)

    # Dessin d'un côté (G ou D) du bracket
    def dessiner_cote(racine, cote, x0, direction):
        for tour in range(5):
            noeuds = collecter_noeuds_par_tour(racine, tour)
            for noeud in noeuds:
                i = noeud.index
                cx = x0 + direction * (tour + 0.5) * COL_L
                cy = pos[tour][i]
                m  = noeud

                x1 = cx - BOX_W / 2
                x2 = cx + BOX_W / 2

                y_haut = cy - BOX_H - GAP / 2
                y_bas  = cy + GAP / 2

                r1 = canvas.create_rectangle(x1, y_haut, x2, y_haut + BOX_H, fill=couleur_rect(m), outline=C_BLANC)
                t1 = canvas.create_text(x1 + 3, y_haut + BOX_H / 2, text=texte_slot(m, 0), fill=C_BLANC, font=pol, anchor=W)
                canvas.tag_bind(r1, "<Button-1>", lambda e, n=noeud, c=cote: ouvrir_match(n, c))
                canvas.tag_bind(t1, "<Button-1>", lambda e, n=noeud, c=cote: ouvrir_match(n, c))

                r2 = canvas.create_rectangle(x1, y_bas, x2, y_bas + BOX_H, fill=couleur_rect(m), outline=C_BLANC)
                t2 = canvas.create_text(x1 + 3, y_bas + BOX_H / 2, text=texte_slot(m, 1), fill=C_BLANC, font=pol, anchor=W)
                canvas.tag_bind(r2, "<Button-1>", lambda e, n=noeud, c=cote: ouvrir_match(n, c))
                canvas.tag_bind(t2, "<Button-1>", lambda e, n=noeud, c=cote: ouvrir_match(n, c))

    dessiner_cote(arbres_bracket["G"], "G", 0,  +1)
    dessiner_cote(arbres_bracket["D"], "D", L,  -1)

    # ---- Dessin de la Finale (centre) ----
    cx = L / 2
    cy = H / 2
    FW = COL_L * 1.05
    FH = BOX_H * 2 + GAP + SLOT_H * 0.25
    m  = finale_bracket

    if m is not None:
        e1 = (m.equipe1 or "?")[:16]
        e2 = (m.equipe2 or "?")[:16]
        s1 = m.score1
        s2 = m.score2
        couleur_finale = couleur_rect(m)
    else:
        e1 = "?"
        e2 = "?"
        s1 = None
        s2 = None
        couleur_finale = C_VIDE

    texte_e1 = f"{e1} {s1}" if s1 is not None else e1
    texte_e2 = f"{e2} {s2}" if s2 is not None else e2

    r_finale = canvas.create_rectangle(cx - FW/2, cy - FH/2, cx + FW/2, cy + FH/2, fill=couleur_finale, outline=C_OR, width=2)
    canvas.create_text(cx, cy - FH * 0.18, text=texte_e1, fill=C_BLANC, font=pol_f)
    canvas.create_text(cx, cy + FH * 0.18, text=texte_e2, fill=C_BLANC, font=pol_f)
    canvas.create_text(cx, cy - FH/2 - fp * 1.5, text="FINALE", fill=C_BLANC, font=pol_l)
    canvas.tag_bind(r_finale, "<Button-1>", lambda e, n=finale_bracket: ouvrir_match(n, "F"))

# ============================================================
# FENÊTRE PRINCIPALE
# ============================================================

fenetre = Tk()
fenetre.title("Tournoi de Football")
fenetre.state('zoomed')
fenetre.configure(bg=BG)

Label(fenetre, text="Tournoi de Football", bg=BG, fg="white", font=("Arial", 18, "bold")).pack(pady=(6, 2))

# Canvas principal (bracket)
canvas = Canvas(fenetre, bg=BG_CANVAS, highlightthickness=0)
canvas.pack(fill=BOTH, expand=True, padx=4)

# Barre du bas avec boutons
bas = Frame(fenetre, bg=BG)
bas.pack(fill=X, side=BOTTOM, pady=10)
Button(bas, text="Top 3 Buteurs", command=top3_buts, bg=C_OR,     fg="black", font=("Arial", 11, "bold"), padx=20, pady=5, cursor="hand2").pack(side=LEFT,  padx=20)
Button(bas, text="Réinitialiser", command=reset,     bg="#c0392b", fg="white", font=("Arial", 11, "bold"), padx=20, pady=5, cursor="hand2").pack(side=RIGHT, padx=20)
lbl_info = Label(bas, text="", bg=BG, fg="#888", font=("Arial", 9))
lbl_info.pack(side=LEFT, padx=10)

canvas.bind("<Configure>", dessiner)

# Chargement de l'image de fond
try:
    image_fond = Image.open("images/fond.jpg")
except:
    image_fond = Image.new("RGB", (100, 100), color=BG_CANVAS)
photo_fond = None

# ============================================================
# LANCEMENT : init ou chargement du cache
# ============================================================

init()
if charger():
    lbl_info.config(text=f"Cache chargé : {FICHIER_CACHE}", fg="#4CAF50")
else:
    lbl_info.config(text="Nouveau tournoi", fg="#888")

fenetre.mainloop()