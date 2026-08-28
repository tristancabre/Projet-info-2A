
# Diagramme de classes des objets métiers

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
    class Player {
        +id_player: int
        +username: string
        +password: string
        +elo: int
        +email: string
        +pokemon_fan: bool
    }
    
    %% Data Access Objects
    class PlayerDao {
        +create(Player): bool
        +find_by_id(int): Player
        +list_all(): list[Player]
        +delete(Player): bool
        +update(Player): bool
        +login(str,str): Player
    }
    
    %% Service layer
    class PlayerService {
        +create(str,str,int,str,bool): Player
        +find_by_id(int): Player
        +list_all(bool=False): list[Player]
        +delete(Player): bool
        +update(Player): Player
        +login(str,str): Player
        +username_already_used(str): bool
    }

    class GameService {
        +play(id_player:int, id_opponent:int, choice:str): dict
        +expected_score(elo1:int, elo2:int): float
        +compute_elo(elo1:int, elo2:int, win1:bool): tuple[int,int]
        +update_elo(j1:Player, j2:Player, winner:Player)
    }
    
    %% Controllers
    class PlayerController {
        +list_all_players(): list[Player]
        +player_by_id(int): Player
        +create_player(PlayerModel): Player
        +update_player(int, PlayerModel): str
        +delete_player(int): str
    }

    class AuthController {
        +login(ConnexionRequest): dict
    }

    class GameController {
        +play_game(GameRequest): dict
    }

    %% Relationships
    PlayerService ..> PlayerDao : calls
    PlayerService ..> Player : uses
    PlayerDao ..> Player : uses
    GameService ..> PlayerDao : calls
    GameService ..> Player : uses
    PlayerController ..> PlayerService : calls
    AuthController ..> PlayerService : calls
    GameController ..> GameService : calls
```
