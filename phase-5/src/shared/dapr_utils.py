from dapr.clients import DaprClient
from typing import Any, Optional
from fastapi import HTTPException
import json
import logging

from src.shared.exceptions import ConflictException, NotFoundException, UnauthorizedException, ForbiddenException

logger = logging.getLogger(__name__)

class DaprServiceInvoker:
    def __init__(self, dapr_client: DaprClient = None):
        self._dapr_client = dapr_client if dapr_client else DaprClient()

    async def invoke_service(
        self,
        app_id: str,
        method_name: str,
        data: dict = None,
        http_verb: str = "POST",
        content_type: str = "application/json",
    ) -> Any:
        """
        Invokes a Dapr service.
        """
        try:
            logger.info(f"Invoking service '{app_id}' method '{method_name}' with verb '{http_verb}'")
            response = await self._dapr_client.invoke_method(
                app_id=app_id,
                method_name=method_name,
                data=json.dumps(data) if data else None,
                http_verb=http_verb,
                content_type=content_type,
            )
            response_data = json.loads(response.text()) if response.text() else {}
            # Dapr invoke method uses gRPC and returns 200 even for application-level errors
            # We need to parse the actual status from the response if the invoked service sends it
            # This is a convention that services might adopt
            if 'status_code' in response_data:
                status_code = response_data['status_code']
                detail = response_data.get('detail', 'Service invocation failed')
                if status_code == 404:
                    raise NotFoundException(detail=detail)
                if status_code == 409:
                    raise ConflictException(detail=detail)
                if status_code == 401:
                    raise UnauthorizedException(detail=detail)
                if status_code == 403:
                    raise ForbiddenException(detail=detail)
            return response_data
        except NotFoundException:
            raise
        except ConflictException:
            raise
        except UnauthorizedException:
            raise
        except ForbiddenException:
            raise
        except Exception as e:
            logger.error(f"Error invoking service '{app_id}' method '{method_name}': {e}")
            raise HTTPException(
                status_code=500, detail=f"Failed to invoke service {app_id}: {e}"
            )

    async def publish_event(self, pubsub_name: str, topic_name: str, data: dict):
        """
        Publishes an event to a Dapr PubSub topic.
        """
        try:
            logger.info(f"Publishing event to pubsub '{pubsub_name}', topic '{topic_name}'")
            await self._dapr_client.publish_event(
                pubsub_name=pubsub_name,
                topic_name=topic_name,
                data=json.dumps(data),
                content_type="application/json",
            )
        except Exception as e:
            logger.error(f"Error publishing event to pubsub '{pubsub_name}', topic '{topic_name}': {e}")
            raise HTTPException(
                status_code=500, detail=f"Failed to publish event to {topic_name}: {e}"
            )

    async def save_state(self, store_name: str, key: str, value: any):
        """
        Saves state to a Dapr State Store.
        """
        try:
            logger.info(f"Saving state to store '{store_name}' with key '{key}'")
            await self._dapr_client.save_state(
                store_name=store_name,
                key=key,
                value=json.dumps(value),
            )
        except Exception as e:
            logger.error(f"Error saving state to store '{store_name}' with key '{key}': {e}")
            raise HTTPException(
                status_code=500, detail=f"Failed to save state for {key}: {e}"
            )

    async def get_state(self, store_name: str, key: str) -> Optional[dict]:
        """
        Retrieves state from a Dapr State Store.
        """
        try:
            logger.info(f"Getting state from store '{store_name}' with key '{key}'")
            response = await self._dapr_client.get_state(
                store_name=store_name,
                key=key,
            )
            if response.data:
                return json.loads(response.data.decode('utf-8'))
            return None
        except Exception as e:
            logger.error(f"Error getting state from store '{store_name}' with key '{key}': {e}")
            raise HTTPException(
                status_code=500, detail=f"Failed to get state for {key}: {e}"
            )
