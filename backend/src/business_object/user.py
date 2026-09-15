class User:
    """
    Class representing a Player.
    Attributes:
        id_player (int): The unique identifier for the user.
        pseudo (str): The user's pseudo.
        password (str): The user's password.
        email (str): The user's email address.
    """

    def __init__(
        self,
        pseudo,
        email,
        password=None,
        id_player=None,
    ):
        """Constructor"""
        self.id_player = id_player
        self.pseudo = pseudo
        self.password = password
        self.email = email

    def __str__(self):
        """Returns a string representation of the player.
        Returns:
            str: A string containing the username and Elo rating.
        """
        return f"Player({self.pseudo})"

    def as_list(self) -> list[str]:
        """Returns the player's key attributes as a list.
        Returns:
            list[str]: A list containing [username, elo, email, pokemon_fan].
        """
        return [self.pseudo, self.email]
