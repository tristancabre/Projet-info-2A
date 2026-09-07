# Diagramme de modèle de données

Ce diagramme est codé avec [mermaid](https://mermaid.js.org/syntax/classDiagram.html) :

* avantage : facile à coder
* inconvénient : on ne maîtrise pas bien l'affichage

Pour afficher ce diagramme dans VScode :

* à gauche aller dans **Extensions** (ou CTRL + SHIFT + X)
* rechercher `mermaid`
  * installer l'extension **Markdown Preview Mermaid Support**
* revenir sur ce fichier
  * faire **CTRL + K**, puis **V**

```mermaid
classDiagram
    %% Business objects

    class User {
        id_user_PK
        pseudo
        password
        email
    }

    class Neo{
        id_neo_PK
        name
        weight 
        size
        distance 
        composition
        closest_day
        origin
        rarity
    }

    class Alert {
        id_alert_PK
        #id_user
        #id_neo
    }

    class Favorites {
        id_favorite_PK
        #id_user
        #id_neo
        date_added 
    }

    %% Relationships
    User "1" ..> "0.." Favorites
    User "1" ..> "0.." Alert
    Neo "0.." ..> "0.." Favorites
    Neo "0.." ..> "0.." Alert

```