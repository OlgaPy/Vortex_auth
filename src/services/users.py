from models import User


class UserService:
    """Сервис управления пользователями"""

    def create_user(self, login: str, password: str, email: str) -> User:
        """Создание нового пользователя"""

        raise NotImplemented

    def get_user(self, user_id: str) -> User:
        """Получение пользователя по id"""

        raise NotImplemented

    def get_users(self, page: int) -> list[User]:
        """Получение пользователя по id"""

        raise NotImplemented

    def edit_user(self, login: str, password: str, email: str) -> User:
        """Редактирование пользователя"""

        raise NotImplemented

    def delete_user(self, user_id: str) -> User:
        """Удаление пользователя"""

        raise NotImplemented
