import aiohttp
from aiohttp import web
import json
from config.settings import (
    LUMINOUS_CLIENT_ID, LUMINOUS_CLIENT_SECRET,
    TENEBRIS_CLIENT_ID, TENEBRIS_CLIENT_SECRET,
    OAUTH2_REDIRECT_URI, PORT
)

class EquinoxWebServer:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.app = web.Application()
        self.app.add_routes([web.get('/callback', self.oauth_callback)])
        self.api_endpoint = "https://discord.com/api/v10/oauth2/token"
        self.user_endpoint = "https://discord.com/api/v10/users/@me"

    async def oauth_callback(self, request):
        code = request.query.get("code")
        state = request.query.get("state")

        if not code or not state:
            return web.Response(text="❌ Lỗi: Thiếu tham số xác thực từ Discord.", status=400)

        if state == "luminous":
            client_id = LUMINOUS_CLIENT_ID
            client_secret = LUMINOUS_CLIENT_SECRET
        elif state == "tenebris":
            client_id = TENEBRIS_CLIENT_ID
            client_secret = TENEBRIS_CLIENT_SECRET
        else:
            return web.Response(text="❌ Lỗi: State định danh Bot không hợp lệ.", status=400)

        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": OAUTH2_REDIRECT_URI
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        async with aiohttp.ClientSession() as session:
            # 1. Trao đổi mã code lấy Token
            async with session.post(self.api_endpoint, data=data, headers=headers) as resp:
                if resp.status != 200:
                    return web.Response(text=f"❌ Lỗi trao đổi Token: {await resp.text()}", status=400)
                
                token_info = await resp.json()
                access_token = token_info.get("access_token")

            # 2. Gọi API Discord để lấy User ID của người vừa ủy quyền
            auth_headers = {"Authorization": f"Bearer {access_token}"}
            async with session.get(self.user_endpoint, headers=auth_headers) as user_resp:
                if user_resp.status != 200:
                    return web.Response(text="❌ Lỗi: Không thể định danh User ID.", status=400)
                
                user_info = await user_resp.json()
                user_id = user_info.get("id")

        # 3. Lưu Access Token và Refresh Token vào Redis Cloud theo ID
        await self.redis.hset(f"oauth:{user_id}", state, json.dumps({
            "access_token": access_token,
            "refresh_token": token_info.get("refresh_token"),
            "scopes": token_info.get("scope")
        }))

        # 4. Trả về giao diện thông báo thành công đẹp mắt
        html_content = f"""
        <html>
            <head>
                <title>Ủy Quyền Thành Công - Equinox Network</title>
                <meta charset="utf-8">
            </head>
            <body style="background-color: #2b2d31; color: white; text-align: center; font-family: sans-serif; padding-top: 100px;">
                <h1>🎉 Xác thực OAuth2 Thành Công!</h1>
                <p>Bạn đã cấp quyền can thiệp Profile cho thực thể <b>{state.capitalize()}</b> thành công.</p>
                <p style="color: #a3a6aa;">Bạn có thể đóng trình duyệt này và quay lại Discord để tiếp tục cài đặt.</p>
            </body>
        </html>
        """
        return web.Response(text=html_content, content_type="text/html")

    async def start(self):
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', PORT)
        await site.start()
        print(f"[Web Server] Đã mở Port {PORT} lắng nghe OAuth2 Callback.")
