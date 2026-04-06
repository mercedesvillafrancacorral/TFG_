from back.port.infrastructure.dto.MockInputDto import MockInputDto
from back.port.domain.PortCounters import PortCounters
from back.port.infrastructure.elasticshearch.elasticshearchPortCountersDomain import (
    elasticsearchPortCountersDomain,
)
from datetime import datetime


class PortCountersMapper:
    @staticmethod
    def to_domain(dto: MockInputDto, port_id: int) -> PortCounters:
        """Convierte MockInputDto a Domain (estilo MapStruct)."""
        return PortCounters(
            rx_port_in_frames=dto.rx_port_in_frames,
            rx_port_out_frames=dto.rx_port_out_frames,
            rx_port_gen_frames=dto.rx_port_gen_frames,
            rx_port_in_true_frames=dto.rx_port_in_true_frames,
            rx_port_gen_true_frames=dto.rx_port_gen_true_frames,
            tx_port_in_frames=dto.tx_port_in_frames,
            tx_port_out_frames=dto.tx_port_out_frames,
            tx_port_in_true_frames=dto.tx_port_in_true_frames,
            gen_frames=dto.gen_frames,
        )

    @staticmethod
    def to_elasticsearch_domain(
        domain: PortCounters, port_id: int
    ) -> elasticsearchPortCountersDomain:
        """Convierte Domain a ElasticsearchDomain para guardar en base de datos."""
        return elasticsearchPortCountersDomain(
            port_id=port_id,
            rx_port_in_frames=domain.rx_port_in_frames,
            rx_port_out_frames=domain.rx_port_out_frames,
            rx_port_gen_frames=domain.rx_port_gen_frames,
            rx_port_in_true_frames=domain.rx_port_in_true_frames,
            rx_port_gen_true_frames=domain.rx_port_gen_true_frames,
            tx_port_in_frames=domain.tx_port_in_frames,
            tx_port_out_frames=domain.tx_port_out_frames,
            tx_port_in_true_frames=domain.tx_port_in_true_frames,
        )
