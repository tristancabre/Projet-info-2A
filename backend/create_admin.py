"""Crée un compte administrateur. À lancer depuis la racine du projet :
    python -m scripts.create_admin
"""
import getpass

from dotenv import load_dotenv

from utils.env_variables import load_environment_variables

load_dotenv()
load_environment_variables()

from service.user_service import UserService  # noqa: E402 (après le chargement du .env)
from utils.exceptions import DuplicateUserError, InvalidPasswordError  # noqa: E402


def main() -> None:
    username = input("Nom d'utilisateur : ").strip()
    email = input("Email : ").strip()
    password = getpass.getpass("Mot de passe : ")
    if password != getpass.getpass("Confirmez le mot de passe : "):
        raise SystemExit("Les mots de passe ne correspondent pas.")

    try:
        user = UserService().create(username, password, email, is_admin=True)
    except (DuplicateUserError, InvalidPasswordError) as e:
        raise SystemExit(f"Erreur : {e}")

    if user is None:
        raise SystemExit("Erreur : la création a échoué.")
    print(f"Administrateur '{user.username}' créé (id={user.id_user}).")


if __name__ == "__main__":
    main()
