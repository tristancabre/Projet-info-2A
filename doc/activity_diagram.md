# Diagramme d'activité

> Un diagramme UML d'activité modélise le flux de travail d'un processus, montrant la séquence d'activités et de décisions dans un système. Il illustre comment les actions s'enchaînent et comment les choix sont faits.

Ce diagramme est codé avec [mermaid](https://mermaid.js.org/syntax/stateDiagram.html) :

- avantage : facile à coder
- inconvénient : on ne maîtrise pas bien l'affichage

Pour afficher ce diagramme dans VScode :

- à gauche aller dans **Extensions** (ou CTRL + SHIFT + X)
- rechercher `mermaid`
  - installer l'extension **Markdown Preview Mermaid Support**
- revenir sur ce fichier
  - faire **CTRL + K**, puis **V**


```mermaid
stateDiagram
    login : Login
    menu_player : Player Menu
    signup : Sign Up
    player_list : List Players
    play_game : Play a game
    logout : Logout
    
    [*] --> Home
    
    Home --> login
    login --> menu_player
    
    Home --> signup
    
    Home --> quit
    quit --> [*]
    
    state menu_player {
    	[*] --> player_list
    	[*] --> play_game
    	[*] --> logout
        logout --> [*]: return to home
    }
```