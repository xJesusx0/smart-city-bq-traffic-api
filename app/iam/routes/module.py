from fastapi import APIRouter

from app.core.dependencies import ModuleServiceDep
from app.core.exceptions import get_entity_not_found_exception
from app.core.models.module import ModuleBase

module_router = APIRouter(prefix="/api/iam/modules", tags=["modules"])


@module_router.get("", response_model=list[ModuleBase])
def get_all_modules(module_service: ModuleServiceDep):
    return module_service.get_all_modules()


@module_router.get("/{module_id}", response_model=ModuleBase)
def get_module_by_id(module_id: int, module_service: ModuleServiceDep):
    module = module_service.get_module_by_id(module_id)
    if module is None:
        raise get_entity_not_found_exception(f"Modulo con id {module_id} no encontrado")

    return module
