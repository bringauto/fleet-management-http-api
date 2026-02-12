from flask.json.provider import DefaultJSONProvider

from fleet_management_api.models.base_model import Model


class CustomJSONProvider(DefaultJSONProvider):
    def default(self, o):
        if isinstance(o, Model):
            dikt = {}
            for attr in o.openapi_types:
                value = getattr(o, attr)
                if value is None:
                    continue
                attr = o.attribute_map[attr]
                dikt[attr] = value
            return dikt
        return super().default(o)
