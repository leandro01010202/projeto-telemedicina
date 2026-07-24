import json
import logging
from typing import Any
from fastapi import WebSocket, WebSocketDisconnect

from domains.webrtc.models import Peer, signaling_manager

logger = logging.getLogger(__name__)


class SignalingConnection:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.peer: Peer | None = None

    async def connect(self) -> None:
        await self.websocket.accept()

    async def send(self, message: dict[str, Any]) -> None:
        await self.websocket.send_json(message)

    async def broadcast_to_room(self, sala_id: str, message: dict[str, Any], exclude_peer_id: str | None = None) -> None:
        room = await signaling_manager.get_room(sala_id)
        if not room:
            return

        for peer_id, peer in list(room.peers.items()):
            if exclude_peer_id and peer_id == exclude_peer_id:
                continue
            try:
                if peer.connection:
                    await peer.connection.send(message)
            except Exception as e:
                logger.error(f"Erro ao enviar para peer {peer_id}: {e}")


class SignalingHandler:
    def __init__(self):
        self.connections: dict[str, SignalingConnection] = {}

    async def handle_join(self, connection: SignalingConnection, data: dict[str, Any]) -> None:
        sala_id = data.get("sala_id")
        peer_id = data.get("peer_id")
        user_id = data.get("user_id", 0)

        if not sala_id or not peer_id:
            await connection.send({"type": "error", "message": "sala_id e peer_id são obrigatórios"})
            return

        peer = Peer(
            peer_id=peer_id,
            user_id=user_id,
            sala_id=sala_id,
            connection=connection,
            is_connected=True,
        )

        room = await signaling_manager.add_peer_to_room(sala_id, peer)
        connection.peer = peer

        # Notificar outros peers na sala
        await connection.broadcast_to_room(
            sala_id,
            {
                "type": "peer-joined",
                "peer_id": peer_id,
                "user_id": user_id,
            },
            exclude_peer_id=peer_id,
        )

        # Se já houver outros peers, enviar offer para o novo peer
        other_peers = room.get_other_peers(peer_id)
        if other_peers:
            await connection.send({
                "type": "peers-present",
                "peer_ids": [p.peer_id for p in other_peers],
            })

        await connection.send({
            "type": "joined",
            "sala_id": sala_id,
            "peer_id": peer_id,
        })

        logger.info(f"Peer {peer_id} entrou na sala {sala_id}")

    async def handle_offer(self, connection: SignalingConnection, data: dict[str, Any]) -> None:
        if not connection.peer:
            return

        target_peer_id = data.get("target_peer_id")
        offer_sdp = data.get("sdp")

        if not target_peer_id or not offer_sdp:
            return

        room = await signaling_manager.get_room(connection.peer.sala_id)
        if not room:
            return

        target_peer = room.get_peer(target_peer_id)
        if target_peer and target_peer.connection:
            await target_peer.connection.send({
                "type": "offer",
                "sdp": offer_sdp,
                "from_peer_id": connection.peer.peer_id,
            })

    async def handle_answer(self, connection: SignalingConnection, data: dict[str, Any]) -> None:
        if not connection.peer:
            return

        target_peer_id = data.get("target_peer_id")
        answer_sdp = data.get("sdp")

        if not target_peer_id or not answer_sdp:
            return

        room = await signaling_manager.get_room(connection.peer.sala_id)
        if not room:
            return

        target_peer = room.get_peer(target_peer_id)
        if target_peer and target_peer.connection:
            await target_peer.connection.send({
                "type": "answer",
                "sdp": answer_sdp,
                "from_peer_id": connection.peer.peer_id,
            })

    async def handle_ice_candidate(self, connection: SignalingConnection, data: dict[str, Any]) -> None:
        if not connection.peer:
            return

        target_peer_id = data.get("target_peer_id")
        candidate = data.get("candidate")

        if not target_peer_id or not candidate:
            return

        room = await signaling_manager.get_room(connection.peer.sala_id)
        if not room:
            return

        target_peer = room.get_peer(target_peer_id)
        if target_peer and target_peer.connection:
            await target_peer.connection.send({
                "type": "ice-candidate",
                "candidate": candidate,
                "from_peer_id": connection.peer.peer_id,
            })

    async def handle_leave(self, connection: SignalingConnection, data: dict[str, Any]) -> None:
        if not connection.peer:
            return

        peer = connection.peer
        sala_id = peer.sala_id

        await signaling_manager.remove_peer_from_room(sala_id, peer.peer_id)

        await connection.broadcast_to_room(
            sala_id,
            {
                "type": "peer-left",
                "peer_id": peer.peer_id,
            },
        )

        logger.info(f"Peer {peer.peer_id} saiu da sala {sala_id}")

    async def handle_disconnect(self, connection: SignalingConnection) -> None:
        if connection.peer:
            await self.handle_leave(connection, {})


signaling_handler = SignalingHandler()
