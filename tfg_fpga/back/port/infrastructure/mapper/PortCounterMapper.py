


from tfg_fpga.back.port.infrastructure.dto.MockInputDto import MockInputDto
from tfg_fpga.back.port.infrastructure.outbound.mock_register_bank import PortCounters


from back.port.infrastructure.dto.MockInputDto import MockInputDto
from back.port.domain.PortCounters import PortCounters
from back.port.infrastructure.dto import ElasticsearchCountersDTO 
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
    def to_elasticsearch_dto( domain: PortCounters, port_id: int) -> ElasticsearchCountersDTO:
        """Convierte Domain a ElasticsearchDTO con nombres adaptados para ES/Grafana."""
        return ElasticsearchCountersDTO(
            timestamp=datetime.utcnow(),
            port_id=port_id,
            rx_in_frames=domain.rx_port_in_frames,
            rx_out_frames=domain.rx_port_out_frames,
            rx_gen_frames=domain.rx_port_gen_frames,
            rx_in_true_frames=domain.rx_port_in_true_frames,
            rx_gen_true_frames=domain.rx_port_gen_true_frames,
            tx_in_frames=domain.tx_port_in_frames,
            tx_out_frames=domain.tx_port_out_frames,
            tx_in_true_frames=domain.tx_port_in_true_frames,
            gen_frames=domain.gen_frames,
        )

    @staticmethod
    def to_document(port_id: int, counters: PortCounters) -> ElasticsearchPortCountersDocument:
        return ElasticsearchPortCounters(
            timestamp=datetime.utcnow(),
            port_id=port_id,
            rx_port_in_frames=counters.rx_port_in_frames,
            rx_port_out_frames=counters.rx_port_out_frames,
            rx_port_gen_frames=counters.rx_port_gen_frames,
            rx_port_in_true_frames=counters.rx_port_in_true_frames,
            rx_port_gen_true_frames=counters.rx_port_gen_true_frames,
            tx_port_in_frames=counters.tx_port_in_frames,
            tx_port_out_frames=counters.tx_port_out_frames,
            tx_port_in_true_frames=counters.tx_port_in_true_frames,
            gen_frames=counters.gen_frames,
        )