# 

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[
            int,
            list[WebSocket]
        ] = {}

    async def connect(
        self,
        user_id: int,
        websocket: WebSocket,
    ):
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = []

        self.active_connections[user_id].append(
            websocket
        )

        print(
            "CONNECTED USER:",
            user_id
        )

        print(
            "ACTIVE USERS:",
            list(self.active_connections.keys())
        )

    def disconnect(
        self,
        user_id: int,
        websocket: WebSocket,
    ):
        connections = self.active_connections.get(
            user_id
        )

        if not connections:
            return

        if websocket in connections:
            connections.remove(websocket)

        if not connections:
            del self.active_connections[user_id]

        print(
            "DISCONNECTED USER:",
            user_id
        )

        print(
            "ACTIVE USERS:",
            list(self.active_connections.keys())
        )

    async def send_to_user(
        self,
        user_id: int,
        data: dict,
    ):
        connections = self.active_connections.get(
            user_id,
            [],
        )

        print(
            f"Sending to user {user_id}. "
            f"Connections: {len(connections)}"
        )

        for connection in connections:
            try:
                await connection.send_json(data)

                print(
                    "MESSAGE SENT TO USER:",
                    user_id
                )

            except Exception as error:
                print(
                    "SEND ERROR:",
                    repr(error)
                )

    def is_online(
        self,
        user_id: int,
    ) -> bool:
        return user_id in self.active_connections


manager = ConnectionManager()