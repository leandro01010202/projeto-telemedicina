import hashlib
from sqlalchemy.ext.asyncio import AsyncSession

from domains.receitas.models import Receita, ItemReceita, Atestado
from domains.receitas.schemas import (
    ReceitaCreate,
    ReceitaResponse,
    AtestadoCreate,
    AtestadoResponse,
)
from domains.receitas.repository import ReceitaRepository, AtestadoRepository
from domains.auth.models import User
from core.exceptions import NotFoundException, ForbiddenException


class ReceitaService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ReceitaRepository(db)

    async def create(self, data: ReceitaCreate, current_user: User) -> ReceitaResponse:
        # Obter medico_id
        medico_id = await self._get_medico_id(current_user.id)
        if not medico_id:
            raise ForbiddenException("Usuário não é um médico cadastrado")

        receita = Receita(
            paciente_id=data.paciente_id,
            medico_id=medico_id,
            consulta_id=data.consulta_id,
            validade_dias=data.validade_dias,
            observacoes=data.observacoes,
        )
        self.db.add(receita)
        await self.db.flush()

        # Adicionar itens
        for item_data in data.itens:
            item = ItemReceita(
                receita_id=receita.id,
                medicamento=item_data.medicamento,
                concentracao=item_data.concentracao,
                quantidade=item_data.quantidade,
                posologia=item_data.posologia,
                via_administracao=item_data.via_administracao,
            )
            self.db.add(item)

        await self.db.flush()
        return await self.get_by_id(receita.id)

    async def get_by_id(self, receita_id: int) -> ReceitaResponse:
        receita = await self.repository.get_by_id(receita_id)
        if not receita:
            raise NotFoundException("Receita não encontrada")
        return ReceitaResponse.model_validate(receita)

    async def sign(self, receita_id: int, current_user: User) -> ReceitaResponse:
        # Verificar se é o médico que criou
        receita = await self.repository.get_by_id(receita_id)
        if not receita:
            raise NotFoundException("Receita não encontrada")

        medico_id = await self._get_medico_id(current_user.id)
        if receita.medico_id != medico_id:
            raise ForbiddenException("Apenas o médico que criou pode assinar")

        # Gerar hash de assinatura
        signature_data = f"{receita_id}:{current_user.id}:{receita.created_at.isoformat()}"
        signature_hash = hashlib.sha256(signature_data.encode()).hexdigest()

        signed = await self.repository.sign(receita_id, signature_hash)
        return ReceitaResponse.model_validate(signed)

    async def list_by_paciente(self, paciente_id: int, include_expired: bool = False) -> list[ReceitaResponse]:
        receitas = await self.repository.list_by_paciente(paciente_id, include_expired)
        return [ReceitaResponse.model_validate(r) for r in receitas]

    async def _get_medico_id(self, user_id: int) -> int | None:
        from domains.medicos.models import Medico
        from sqlalchemy import select
        result = await self.db.execute(select(Medico.id).where(Medico.user_id == user_id))
        row = result.first()
        return row[0] if row else None


class AtestadoService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = AtestadoRepository(db)

    async def create(self, data: AtestadoCreate, current_user: User) -> AtestadoResponse:
        medico_id = await self._get_medico_id(current_user.id)
        if not medico_id:
            raise ForbiddenException("Usuário não é um médico cadastrado")

        atestado = Atestado(
            paciente_id=data.paciente_id,
            medico_id=medico_id,
            consulta_id=data.consulta_id,
            cid=data.cid,
            dias=data.dias,
            motivo=data.motivo,
        )
        created = await self.repository.create(atestado)
        return AtestadoResponse.model_validate(created)

    async def get_by_id(self, atestado_id: int) -> AtestadoResponse:
        atestado = await self.repository.get_by_id(atestado_id)
        if not atestado:
            raise NotFoundException("Atestado não encontrado")
        return AtestadoResponse.model_validate(atestado)

    async def sign(self, atestado_id: int, current_user: User) -> AtestadoResponse:
        atestado = await self.repository.get_by_id(atestado_id)
        if not atestado:
            raise NotFoundException("Atestado não encontrado")

        medico_id = await self._get_medico_id(current_user.id)
        if atestado.medico_id != medico_id:
            raise ForbiddenException("Apenas o médico que criou pode assinar")

        signature_data = f"{atestado_id}:{current_user.id}:{atestado.created_at.isoformat()}"
        signature_hash = hashlib.sha256(signature_data.encode()).hexdigest()

        signed = await self.repository.sign(atestado_id, signature_hash)
        return AtestadoResponse.model_validate(signed)

    async def list_by_paciente(self, paciente_id: int) -> list[AtestadoResponse]:
        atestados = await self.repository.list_by_paciente(paciente_id)
        return [AtestadoResponse.model_validate(a) for a in atestados]

    async def _get_medico_id(self, user_id: int) -> int | None:
        from domains.medicos.models import Medico
        from sqlalchemy import select
        result = await self.db.execute(select(Medico.id).where(Medico.user_id == user_id))
        row = result.first()
        return row[0] if row else None
