
import time
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.db import transaction
from django.utils.timezone import now as now_dj
from .models import Canvas, CanvasTile, PixelChange, TILE_SIZE
from .tile_utils import decompress_tile, compress_tile, set_pixel

COOLDOWN_SEC = 5
_last_click: dict[int, dict[int, float]] = {}


class CanvasConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.canvas_id = int(self.scope["url_route"]["kwargs"]["canvas_id"])
        self.group_name = f"canvas_{self.canvas_id}"

        exists = await sync_to_async(
            Canvas.objects.filter(pk=self.canvas_id).exists
        )()
        if not exists:
            await self.close(code=4004)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        user = self.scope.get("user")
        if user and user.is_authenticated:
            _last_click.setdefault(self.canvas_id, {}).pop(user.id, None)

        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, data, **kwargs):
        print(">>> receive_json", data)

        user = self.scope["user"]
        is_artist = (
            user.is_authenticated
            and (
                user.is_superuser or
                await user.groups.filter(name="artist").aexists()
                )
            )

        print("   artist?", is_artist)
        if not is_artist:
            await self.send_json({"error": "permission_denied"})
            return


        now = time.time()
        last = _last_click.setdefault(self.canvas_id, {}).get(user.id, 0)
        if now - last < COOLDOWN_SEC:
            await self.send_json({"error": "cooldown"})
            return
        _last_click[self.canvas_id][user.id] = now


        try:
            x, y, color = int(data["x"]), int(data["y"]), int(data["color"])
        except (KeyError, ValueError, TypeError):
            await self.send_json({"error": "bad_payload"})
            return

        canvas = await sync_to_async(Canvas.objects.get)(pk=self.canvas_id)
        if not (0 <= x < canvas.width and 0 <= y < canvas.height):
            await self.send_json({"error": "out_of_bounds"})
            return


        tx, ty = x // TILE_SIZE, y // TILE_SIZE
        lx, ly = x % TILE_SIZE, y % TILE_SIZE

        @sync_to_async
        @transaction.atomic
        def _write_tile():
            tile = CanvasTile.get_for_update(canvas_id=self.canvas_id, tx=tx, ty=ty)
            buf = decompress_tile(tile.data)
            set_pixel(buf, lx, ly, color)
            tile.data = compress_tile(buf)
            tile.save(update_fields=["data", "updated_at"])

            PixelChange.objects.create(
                canvas_id=self.canvas_id, user_id=user.id, x=x, y=y, color=color
            )

        

        

        await _write_tile()

        payload = {
                "x": x,
                "y": y,
                "color": color,
                "user": user.username or "—",
                "ts":   now_dj().isoformat(timespec="seconds"),
                }
        await self.channel_layer.group_send(
            self.group_name, {"type": "pixel_update", "payload": payload}
        )

    async def pixel_update(self, event):
        await self.send_json(event["payload"])
