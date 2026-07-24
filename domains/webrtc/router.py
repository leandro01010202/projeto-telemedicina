import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.security import verify_access_token
from domains.webrtc.signaling import SignalingConnection, signaling_handler
from domains.webrtc.models import signaling_manager
from domains.consultas.service import ConsultaService
from core.exceptions import NotFoundException

router = APIRouter(tags=["WebRTC"])
logger = logging.getLogger(__name__)


@router.websocket("/ws/sala/{sala_id}")
async def websocket_sala(
    websocket: WebSocket,
    sala_id: str,
    token: str = Query(...),
):
    # Validar token
    try:
        payload = verify_access_token(token)
        user_id = payload.get("sub", 0)
    except Exception as e:
        await websocket.close(code=4001, reason="Token inválido")
        return

    # Verificar se a sala existe (consulta)
    # Esta verificação é opcional - você pode permitir salas sem consulta associada

    connection = SignalingConnection(websocket)
    await connection.connect()

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            handlers = {
                "join": signaling_handler.handle_join,
                "offer": signaling_handler.handle_offer,
                "answer": signaling_handler.handle_answer,
                "ice-candidate": signaling_handler.handle_ice_candidate,
                "leave": signaling_handler.handle_leave,
            }

            handler = handlers.get(msg_type)
            if handler:
                await handler(connection, data)
            else:
                await connection.send({
                    "type": "error",
                    "message": f"Tipo de mensagem desconhecido: {msg_type}"
                })

    except WebSocketDisconnect:
        await signaling_handler.handle_disconnect(connection)
        logger.info(f"WebSocket desconectado para sala {sala_id}")
    except Exception as e:
        logger.error(f"Erro no WebSocket: {e}")
        await signaling_handler.handle_disconnect(connection)


@router.get("/rooms/stats")
async def get_rooms_stats():
    """Retorna estatísticas das salas ativas (para monitoramento)."""
    return {
        "active_rooms": signaling_manager.get_active_rooms_count(),
        "total_peers": signaling_manager.get_total_peers_count(),
    }
