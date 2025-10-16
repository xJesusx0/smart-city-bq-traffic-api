import logging
import traceback

from app.core.exceptions import get_internal_server_error_exception
from app.core.models.module import ModuleBase
from app.core.models.role import RoleBase
from app.iam.dtos.role_with_modules import RoleWithModulesDTO
from app.iam.services.module_service import ModuleService
from app.iam.services.role_service import RoleService


class GetRolesWithModulesUseCase:
    def __init__(self, role_service: RoleService, module_service: ModuleService):
        self.role_service = role_service
        self.module_service = module_service

    def invoke(self, active: bool | None = None) -> list[RoleWithModulesDTO]:
        print("get_roles_with_modules_use_case")
        try:
            roles = self.role_service.get_all_roles(active=active)
            if not roles:
                return []

            role_ids = [r.id for r in roles if r.id is not None]
            modules_map = self.module_service.get_modules_map_by_role_ids(role_ids)

            result: list[RoleWithModulesDTO] = []
            for role in roles:
                modules = modules_map.get(role.id or -1, [])
                modules = [ModuleBase.model_validate(m) for m in modules]
                dto = RoleWithModulesDTO(
                    modules=modules, **RoleBase.model_validate(role).model_dump()
                )
                result.append(dto)
            return result
        except Exception as e:
            print(traceback.format_exc())
            logging.error(f"Error al obtener los roles con modulos: {e}")
            raise get_internal_server_error_exception(
                "Ocurrio un error inesperado, contacte con un administrador"
            )
