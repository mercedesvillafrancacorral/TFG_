#from back.port.infrastructure.outbound.mock_register_bank import MockRegisterBank
#from back.port.infrastructure.outbound.MockHardwareAdapter import MockHardwareAdapter
from back.port.application.PortCountersService import PortCountersService
from back.port.infrastructure.elasticsearch.repository.elasticsearchRepository import ElasticsearchRepository
from back.port.infrastructure.outbound.TutorPortHardwareAdapter import TutorPortHardwareAdapter

# Instancia única compartida del simulador
#bank = MockRegisterBank(port_count=4, auto_start=True)

# Adaptador concreto que implementa IPortHardware
#cuando quier utilziar el mock hay que cambiarlo 
hardware = TutorPortHardwareAdapter(port_count=4)

def get_port_service():
    hw = TutorPortHardwareAdapter(port_count=4)
    repo = ElasticsearchRepository()

    return PortCountersService(hw, repo)