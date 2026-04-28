#from back.port.infrastructure.outbound.mock_register_bank import MockRegisterBank
#from back.port.infrastructure.outbound.MockHardwareAdapter import MockHardwareAdapter
from back.port.application.PortCountersService import PortCountersService
from back.port.infrastructure.elasticsearch.repository.elasticsearchRepository import ElasticsearchRepository
from back.port.infrastructure.outbound.mock_port_hardware_adapter import PortHardwareAdapter

#PONEMOS POR A 4 PARA SIMULAR 4 PUERTOS DE LA ZCU102 SY QUIERA ALVEO200 HABRIA QUE PONER 2


hardware = PortHardwareAdapter(port_count=4)
repo = ElasticsearchRepository()
service = PortCountersService(hardware, repo)

def get_port_service():
    return service