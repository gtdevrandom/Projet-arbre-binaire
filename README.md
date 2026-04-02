# 🏆 Gestion de Tournoi avec Arbre Binaire

## 📌 Description du projet

Ce projet implémente un système de gestion de tournoi basé sur une structure en **arbre binaire**. Il permet de modéliser les différentes phases d’un tournoi (du 16ème de finale jusqu’à la finale), d’enregistrer les résultats des matchs, et de suivre les performances des joueurs.

L’objectif principal est de fournir une représentation claire et évolutive des matchs ainsi qu’un suivi structuré des gagnants et des statistiques.

---

## ⚙️ Fonctionnalités

### 🌳 Structure du tournoi

* Représentation du tournoi sous forme d’un **arbre binaire**
* Chaque **nœud** contient :

  * Informations du match
  * Participants
  * Résultat
  * Date du match
* Les nœuds parents représentent les matchs suivants

---

### Architecture et fichiers

```
Projet-arbre-binaire/
┌── main.py
├── LICENSE                         # Licence MIT
├── requirements.txt
├── lanceur.bat
├── README.md                       # Résumé du projet
├── images/
└──  └── fond.png
```

### 🏁 Phases du tournoi

Le système prend en charge les différentes étapes :

* 16ème de finale
* 8ème de finale
* Quart de finale (1/4)
* Demi-finale (1/2)
* Finale

---

### 🥇 Gestion des matchs

* Enregistrement des résultats
* Détermination automatique du **gagnant**
* Accès au **prochain match** via la structure de l’arbre
* Mise à jour dynamique des nœuds

---

### 📊 Statistiques des joueurs (optionel)

* Tableau des meilleurs joueurs :

  * ⚽ Meilleur **buteur**
  * 🎯 Meilleur **tireur**
* Mise à jour en fonction des performances enregistrées

---

### 💾 Stockage des données

* Les informations sont stockées directement dans les **nœuds de l’arbre**
* Chaque nœud contient :

  * Joueurs
  * Score
  * Gagnant
  * Date du match

---

## 🔄 Logique de fonctionnement

1. Initialisation des matchs (16ème de finale)
2. Saisie des résultats
3. Propagation des gagnants vers le niveau supérieur
4. Construction automatique des phases suivantes
5. Accès à la finale via la racine de l’arbre

---

## 📅 Exemple d'information de match

* Joueurs : A vs B
* Score : 2 - 1
* Gagnant : A
* Date : 2026-03-26

---

## 📁 Objectif pédagogique

Ce projet est idéal pour :

* Comprendre les **arbres binaires**
* Manipuler des structures de données
* Modéliser des systèmes réels (tournois sportifs)

---

## 💡Inspiration

- [UEFA](https://fr.uefa.com/uefachampionsleague/fixtures-results/bracket/)

---

## Image de fond

- [Vecteezy](https://static.vecteezy.com/ti/photos-gratuite/p2/31690029-football-stade-a-l-interieur-a-nuit-avec-lumieres-post-production-gratuit-photo.jpg)

---

## Documentation

- [Documentation tkinter](https://docs.python.org/fr/3/library/tkinter.html)

---
## 👨‍💻 Auteur et License

Projet réalisé dans un objectif d’apprentissage et de pratique en développement par gtdevrandom.
Projet sous la [License Mit](LICENSE)

---
