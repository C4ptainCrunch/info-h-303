from users.models import User, AnonymousUser

class CustomSessionMiddleware:
    def process_request(self, request):
        cookies = request.COOKIES
        if 'horeca_user' in cookies:
            cookie = cookies['horeca_user']
            users = User.objects.raw(
                """SELECT *
                    FROM "user"
                    WHERE id=(
                        SELECT user_id FROM "session" WHERE cookie=%s
                    )
                """, [cookie])
            if users:
                request.user = users[0]
                return None

        request.user = AnonymousUser()
