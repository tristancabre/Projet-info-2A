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
        id_user_PK : SERIAL
        pseudo : VARCHAR
        password : VARCHAR
        email : VARCHAR
    }

    class Neo{
        id_neo_PK : SERIAL
        name : VARCHAR
        weight : INT
        size : INT
        distance : INT
        composition : VARCHAR
        closest_day : DATE
        origin : VARCHAR
        rarity : INT
    }

    class Alert {
        id_alert_PK : SERIAL
        #id_user : SERIAL
        #id_neo : SERIAL | NULL
        min_size : INT | Null
        max_size : INT | Null
        min_distance : FLOAT | Null
        max_distance : FLOAT | Null
    }

    class Favorites {
        id_favorite_PK : SERIAL
        #id_user : SERIAL
        #id_neo : SERIAL
        date_added : DATE
    }

    class ConnectionLog {
        id_connection_PK : SERIAL
        #id_user : SERIAL
        timestamp : TIMESTAMP
    }

    class SearchHistory {
        id_search_PK : SERIAL
        #id_user : SERIAL
        search_query : VARCHAR
        timestamp : TIMESTAMP
    }

    class NeoDistanceHistory {
        id_history_PK : SERIAL
        #id_neo : SERIAL
        distance : FLOAT
        observation_date : DATE
    }


    %% Relationships
    Neo "0.." ..> "0.." Favorites
    Neo "0.." ..> "0.." Alert
    Neo "1" ..> "1" NeoDistanceHistory
    User "1" ..> "0.." ConnectionLog
    User "1" ..> "1" SearchHistory
    User "1" ..> "1" Favorites
    User "1" ..> "0.." Alert

```