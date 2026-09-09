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
        id_user_PK : int
        pseudo : varchar
        password : varchar
        email : varchar
    }

    class Neo{
        id_neo_PK : id
        name : varchar
        weight : int
        size : int
        distance : int
        composition : varchar
        closest_day : date
        origin : varchar
        rarity : int
    }

    class Alert {
        id_alert_PK : int
        #id_user : int
        #id_neo : int | NULL
        min_size : int | Null
        max_size : int | Null
        min_distance : int | Null
        max_distance : int | Null
    }

    class Favorites {
        id_favorite_PK : int
        #id_user : int
        #id_neo : int
        date_added : date
    }

    class ConnectionLog {
        id_connection_PK : int
        #id_user : int 
        timestamp : timestamp
    }

    class SearchHistory {
        id_search_PK : int
        #id_user : int
        search_query : varchar
        timestamp : timestamp
    }

    class NeoDistanceHistory {
        id_history_PK : int
        #id_neo : int
        distance : float
        observation_date : date
    }


    %% Relationships
    Neo "0.." ..> "0.." Favorites
    Neo "0.." ..> "0.." Alert
    Neo "1" ..> "1" NeoDistanceHistory
    User "1" ..> "0.." ConnectionLog
    User "1" ..> "1" SearchHistory
    User "1" ..> "0.." Favorites
    User "1" ..> "0.." Alert

```