import httpx


class AtlassianConnector:
    def __init__(self, base_url, access_token, context):
        self.base_url = base_url
        self.access_token = access_token
        self.context = context
        self.url = f"{self.base_url}{self.context}"

    def getRessource(self, resource, *, params=None, headers=None):
        with httpx.Client() as client:
            response = client.get(
                f"{self.url}/rest/api/{resource}",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    **(headers or {}),
                },
                params=params,
            )
            response.raise_for_status()
            return response.json()
