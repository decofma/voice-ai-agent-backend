# backend/app/services/data_store.py
from typing import Dict, List, Any

# Simulação de tabelas de banco de dados
AGENTS_DB: Dict[int, Dict[str, Any]] = {}
CALLS_DB: Dict[int, Dict[str, Any]] = {}

next_agent_id = 1
next_call_id = 1

def create_agent(data: Dict[str, Any]) -> Dict[str, Any]:
    global next_agent_id
    new_id = next_agent_id
    data['id'] = new_id
    AGENTS_DB[new_id] = data
    next_agent_id += 1
    return AGENTS_DB[new_id]

def get_agent(agent_id: int) -> Dict[str, Any] | None:
    return AGENTS_DB.get(agent_id)

def get_all_agents() -> List[Dict[str, Any]]:
    return list(AGENTS_DB.values())

def create_call_record(data: Dict[str, Any]) -> Dict[str, Any]:
    global next_call_id
    new_id = next_call_id
    data['id'] = new_id
    CALLS_DB[new_id] = data
    next_call_id += 1
    return CALLS_DB[new_id]

def update_call_record(retell_call_id: str, data: Dict[str, Any]):
    for call_id, record in CALLS_DB.items():
        if record.get('retell_call_id') == retell_call_id:
            CALLS_DB[call_id].update(data)
            return CALLS_DB[call_id]
    return None

def get_call_record_by_retell_id(retell_call_id: str) -> Dict[str, Any] | None:
    for record in CALLS_DB.values():
        if record.get('retell_call_id') == retell_call_id:
            return record
    return None

def get_all_call_records() -> List[Dict[str, Any]]:
    return sorted(list(CALLS_DB.values()), key=lambda x: x['id'], reverse=True)