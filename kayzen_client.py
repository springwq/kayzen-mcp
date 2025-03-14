from datetime import datetime, timedelta
import httpx
from config import config
from typing import Optional, Dict, Any

class KayzenClient:
    def __init__(self):
        self.base_url = config.base_url
        self.user_name = config.user_name
        self.password = config.password
        self.basic_auth_token = config.basic_auth_token
        self.auth_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None

    async def _get_auth_token(self) -> str:
        """Get or refresh authentication token"""
        if self.auth_token and self.token_expiry and datetime.now() < self.token_expiry:
            return self.auth_token

        url = "https://api.kayzen.io/v1/authentication/token"
        payload = {
            "grant_type": "password",
            "username": self.user_name,
            "password": self.password
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Basic {self.basic_auth_token}"
        }

        print("Requesting token with:")
        print(f"URL: {url}")
        print(f"Headers: {headers}")
        print(f"Payload: {payload}")

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                print(f"Response data: {data}")

                # Check if access_token exists in response
                if "access_token" in data:
                    self.auth_token = data["access_token"]
                else:
                    print(f"Unexpected response format: {data}")
                    raise ValueError("No access_token in response")

                # Token expires in 30 minutes, we'll refresh after 25 minutes
                self.token_expiry = datetime.now() + timedelta(minutes=25)
                return self.auth_token
            except httpx.HTTPError as e:
                print(f"HTTP Error: {str(e)}")
                print(f"Response status: {e.response.status_code if hasattr(e, 'response') else 'N/A'}")
                print(f"Response body: {await e.response.text() if hasattr(e, 'response') else 'N/A'}")
                raise

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make authenticated request to Kayzen API"""
        token = await self._get_auth_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        kwargs["headers"] = headers

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                f"{self.base_url}{endpoint}",
                **kwargs
            )
            response.raise_for_status()
            return response.json()

    async def create_report(self, report_type: str, start_date: str, end_date: str,
                          dimensions: list[str], metrics: list[str]) -> Dict[str, Any]:
        """Create a new report"""
        payload = {
            "report_type": report_type,
            "start_date": start_date,
            "end_date": end_date,
            "dimensions": dimensions,
            "metrics": metrics
        }
        return await self._make_request("POST", "/reports", json=payload)

    async def get_report_results(self, report_id: str) -> Dict[str, Any]:
        """Get report results"""
        return await self._make_request("GET", f"/reports/{report_id}/results")

    async def get_report_status(self, report_id: str) -> Dict[str, Any]:
        """Get report status"""
        return await self._make_request("GET", f"/reports/{report_id}/status")
