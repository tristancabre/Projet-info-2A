
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

    class User {
        -pseudo: string
        -password: string
        -email: string
        +hash_password(plain_password: str) str
        +check_password(plain_password: str) bool
    }
    class Visitor {
        -visitor_name: string
    }
    class Administrator {
        -admin_name: string
    }

    class UserDao {
        +create(User): bool
        +find_by_pseudo(pseudo : string): User
        +list_all(): list[User]
        +delete(User): bool
        +update(User): bool
        +login(str,str): User
    }

    class UserService {
        +create(str,str,str,bool): User
        +find_by_pseudo(str): User
        +list_all: list[User]
        +delete(User): bool
        +update(User): User
        +login(str,str): User
        +username_already_used(str): bool
    }

    
    class AdministratorService {
        +view_connection_history(): list
        +manage_account(User, action: str): bool
        +update_db_nasa():  bool
    }

    class AdministratorController {
        +get_connection_history(): list
        +manage_account_request(AccountActionModel): str
        +update_db_nasa_request(): str
    }

    

    class Neo{
        -name : string
        -weight : int
        -size:int
        -age : int
        -distance : list
        -trajectory: string 
        -composition : list
        -closest_day : date
        -origin : string
    }
    class NeoDao {
        +create(Neo): bool
        +find_by_name(string): Neo
        +list_all(): list[Neo]
        +delete(Neo): bool
        +update(Neo): bool
    }

    class NeoService {
        +search_by_name(name : str): Neo
        +search_by_weight(weight:int): list[Neo]
        +search_by_size(size : int): list[Neo]
        +search_by_age(age:int): list[Neo]
        +search_by_composition (composition : list) : list[Neo]
        +search_by_date (closest_day : date): list[Neo]
        +create_neo(name: str, weight: int, size: int, age : int, distance : list, trajectory: str, composition : list, closest_day : date, origin : str): Neo
    }
    
    class UserController {
        +list_all_Users(): list[User]
        +User_by_pseudo(int): User
        +create_User(User): User
        +update_User(int, User): str
        +delete_User(int): str
    }

    class Connection_Controller {
        +login(ConnexionRequest): dict
    }

    class NeoController {
        +execute_features(NeoRequest): dict
    }

    class Alert {
        -earth_max_distance: int
        -min_size: float
        -targeted_neo: Neo
        -is_active: bool
        +check(Neo): bool
    }

    class Notifications {
        +message : string
        +date_message : date
        +send_mail(email : string): bool
    }

    class Favorites {
        -date_added: date
        -distance_history: list
        +add_neo(Neo): bool
        +remove_neo(Neo): bool
        +get_distance_history(): list
        +export_graph(): file
    }

    %% Relationships
    User <|-- Visitor
    User <|-- Administrator
    UserService ..> UserDao : calls
    UserService ..> User : uses
    UserDao ..> User : uses
    UserController ..> UserService : calls
    Connection_Controller ..> UserService : calls
    AdministratorService ..> UserService : calls
    AdministratorService ..> Administrator : uses
    AdministratorController ..> AdministratorService : calls
    NeoService ..> NeoDao : calls
    NeoService ..> Neo : uses
    NeoDao ..> Neo : uses
    NeoController ..> NeoService : calls
    Visitor "1" --> "0..*" Favorites : creates
    Favorites "0..*" --> "1" Neo
    Notifications ..> Visitor : uses
    Visitor "1" --> "0..*" Alert : defines
    Alert "1" --> "0..*" Notifications : triggers





```
