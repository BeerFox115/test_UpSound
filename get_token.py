import asyncio

from yandex_music import ClientAsync


async def main():
    def on_code(code):
        print(f'Откройте {code.verification_url} и введите код: {code.user_code}')

    client = ClientAsync()
    token = await client.device_auth(on_code=on_code)

    # Сохраните токен, чтобы не проходить авторизацию заново.
    print(f'access_token:  {token.access_token}')
    print(f'refresh_token: {token.refresh_token}')
    print(f'expires_in:    {token.expires_in}')

    await client.init()
    print(client.me.account.login)


asyncio.run(main())