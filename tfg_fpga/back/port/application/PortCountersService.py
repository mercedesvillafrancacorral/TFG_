from back.port.domain.PortCounters import PortCounters
from back.port.infrastructure.dto.MockInputDto import MockInputDto
from back.port.infrastructure.elasticshearch.elasticshearchPortCountersDomain import (
    elasticsearchPortCountersDomain,
)
from back.port.infrastructure.mapper.PortCounterMapper import PortCountersMapper


class PortCountersService:
    """Servicio con validación y flujo completo (DTO -> Domain -> ES Domain)."""

    def __init__(self, max_ports: int = 4):
        self.max_ports = max_ports

    def save_counters(
        self, dto: MockInputDto, port_id: int
    ) -> elasticsearchPortCountersDomain:
        """
        Flujo completo:
        1. Validar port_id existe
        2. Validar valores no negativos
        3. Mapear DTO -> Domain
        4. Mapear Domain -> ElasticsearchDomain
        """
        self._validate_port_id(port_id)
        self._validate_counters(dto)

        domain = PortCountersMapper.to_domain(dto, port_id)
        es_domain = PortCountersMapper.to_elasticsearch_domain(domain, port_id)

        return es_domain

    def get_counters(self, port_id: int) -> PortCounters:
        """Método legacy para compatibilidad."""
        self._validate_port_id(port_id)
        return PortCounters(
            rx_port_in_frames=0,
            rx_port_out_frames=0,
            rx_port_gen_frames=0,
            rx_port_in_true_frames=0,
            rx_port_gen_true_frames=0,
            tx_port_in_frames=0,
            tx_port_out_frames=0,
            tx_port_in_true_frames=0,
            gen_frames=0,
        )

    def _validate_port_id(self, port_id: int):
        """Valida que el port_id esté en rango."""
        if port_id < 0 or port_id >= self.max_ports:
            raise ValueError(
                f"Port ID {port_id} fuera de rango. Debe estar entre 0 y {self.max_ports - 1}"
            )

    def _validate_counters(self, dto: MockInputDto):
        """Valida que todos los contadores sean no negativos."""
        for field_name, value in vars(dto).items():
            if value < 0:
                raise ValueError(
                    f"Contador {field_name} no puede ser negativo: {value}"
                )
