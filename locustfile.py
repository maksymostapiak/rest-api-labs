from locust import HttpUser, task, between

class LibraryLoadTest(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """
        Цей метод автоматично виконується один раз для КОЖНОГО нового віртуального юзера.
        Ми використовуємо його для логіну, щоб юзер міг стукатись у захищені ендпоінти.
        """
        response = self.client.post(
            "/auth/token", 
            data={"username": "admin", "password": "secret"}
        )
        if response.status_code == 200:
            token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {token}"}
        else:
            self.headers = {}
            print("Помилка авторизації Locust юзера!")

    @task
    def get_books(self):
        """
        Основне завдання, яке Locust буде постійно повторювати.
        """
        self.client.get("/books/", headers=self.headers)