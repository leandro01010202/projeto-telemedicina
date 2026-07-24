from dataclasses import dataclass, field
from typing import Any
import asyncio


@dataclass
class Peer:
    peer_id: str
    user_id: int
    sala_id: str
    connection: Any = None
    is_connected: bool = False


@dataclass
class Room:
    sala_id: str
    peers: dict[str, Peer] = field(default_factory=dict)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    created_at: float = field(default_factory=lambda: asyncio.get_event_loop().time())

    def add_peer(self, peer: Peer) -> None:
        self.peers[peer.peer_id] = peer

    def remove_peer(self, peer_id: str) -> Peer | None:
        return self.peers.pop(peer_id, None)

    def get_peer(self, peer_id: str) -> Peer | None:
        return self.peers.get(peer_id)

    def get_other_peers(self, exclude_peer_id: str) -> list[Peer]:
        return [p for pid, p in self.peers.items() if pid != exclude_peer_id and p.is_connected]

    @property
    def peer_count(self) -> int:
        return len(self.peers)

    @property
    def is_empty(self) -> bool:
        return len(self.peers) == 0


class SignalingManager:
    def __init__(self):
        self._rooms: dict[str, Room] = {}
        self._lock = asyncio.Lock()

    async def create_room(self, sala_id: str) -> Room:
        async with self._lock:
            if sala_id not in self._rooms:
                self._rooms[sala_id] = Room(sala_id=sala_id)
            return self._rooms[sala_id]

    async def get_room(self, sala_id: str) -> Room | None:
        return self._rooms.get(sala_id)

    async def delete_room(self, sala_id: str) -> None:
        async with self._lock:
            self._rooms.pop(sala_id, None)

    async def add_peer_to_room(self, sala_id: str, peer: Peer) -> Room:
        room = await self.get_room(sala_id)
        if not room:
            room = await self.create_room(sala_id)

        async with room.lock:
            room.add_peer(peer)

        return room

    async def remove_peer_from_room(self, sala_id: str, peer_id: str) -> None:
        room = await self.get_room(sala_id)
        if not room:
            return

        async with room.lock:
            room.remove_peer(peer_id)

        # Remove room se vazia
        if room.is_empty:
            await self.delete_room(sala_id)

    def get_active_rooms_count(self) -> int:
        return len(self._rooms)

    def get_total_peers_count(self) -> int:
        return sum(room.peer_count for room in self._rooms.values())


signaling_manager = SignalingManager()
