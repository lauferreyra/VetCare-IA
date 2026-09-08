import httpx

from app.config import settings


class VetCareApiService:

    def __init__(self, access_token: str):
        self.base_url = settings.vetcare_api_url
        self.access_token = access_token

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
        }

    def get_pets(self):
        with httpx.Client() as client:
            response = client.get(
                f"{self.base_url}/pets",
                headers=self._headers(),
            )

            response.raise_for_status()

            return response.json()

    def get_appointments(self):
        with httpx.Client() as client:
            response = client.get(
                f"{self.base_url}/appointments",
                headers=self._headers(),
            )

            response.raise_for_status()

            return response.json()

    def get_available_appointments(
        self,
        date: str,
    ):
        with httpx.Client() as client:
            response = client.get(
                f"{self.base_url}/appointments/availability",
                params={
                    "date": date,
                },
                headers=self._headers(),
            )

            response.raise_for_status()

            return response.json()

    def create_appointment(
        self,
        data: dict,
    ):
        with httpx.Client() as client:
            response = client.post(
                f"{self.base_url}/appointments",
                json=data,
                headers=self._headers(),
            )

            response.raise_for_status()

            return response.json()

    def cancel_appointment(
        self,
        appointment_id: int,
    ):
        with httpx.Client() as client:
            response = client.patch(
                f"{self.base_url}/appointments/{appointment_id}/cancel",
                headers=self._headers(),
            )

            response.raise_for_status()

            return response.json()