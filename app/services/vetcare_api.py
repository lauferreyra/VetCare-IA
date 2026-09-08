import httpx

from app.config import settings


class VetCareApiService:

    def __init__(self):
        self.base_url = settings.vetcare_api_url

    async def get_pets(self):
        async with httpx.AsyncClient() as client:

            response = await client.get(
                f"{self.base_url}/pets"
            )

            response.raise_for_status()

            return response.json()

    async def get_appointments(self):
        async with httpx.AsyncClient() as client:

            response = await client.get(
                f"{self.base_url}/appointments"
            )

            response.raise_for_status()

            return response.json()

    async def get_available_appointments(
        self,
        date: str,
    ):

        async with httpx.AsyncClient() as client:

            response = await client.get(
                f"{self.base_url}/appointments/available",
                params={
                    "date": date,
                },
            )

            response.raise_for_status()

            return response.json()

    async def create_appointment(
        self,
        pet_id: str,
        date: str,
        time: str,
    ):

        async with httpx.AsyncClient() as client:

            response = await client.post(
                f"{self.base_url}/appointments",
                json={
                    "petId": pet_id,
                    "date": date,
                    "time": time,
                },
            )

            response.raise_for_status()

            return response.json()

    async def cancel_appointment(
        self,
        appointment_id: str,
    ):

        async with httpx.AsyncClient() as client:

            response = await client.delete(
                f"{self.base_url}/appointments/{appointment_id}"
            )

            response.raise_for_status()

            return response.json()