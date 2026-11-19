from drf_spectacular import openapi
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated


class AutoSchema(openapi.AutoSchema):
    def get_auth(self):
        auths = super().get_auth()
        needs_login = any(isinstance(p, IsAuthenticated) for p in self.view.get_permissions())
        if self.method in SAFE_METHODS and not needs_login and {} not in auths:
            auths.append({})
        return auths

    def _is_create_operation(self):
        return self.method == 'POST'
