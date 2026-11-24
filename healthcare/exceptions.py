"""Consistent JSON error responses for the whole API.

Every error response has the shape::

    {"success": false, "error": {"status_code": 400, "message": "...", "details": {...}}}
"""
import logging

from django.db import IntegrityError
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def _message_from(data):
    if isinstance(data, dict):
        if "detail" in data:
            return str(data["detail"])
        return "Validation failed."
    if isinstance(data, list) and data:
        return str(data[0])
    return str(data)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        if isinstance(exc, IntegrityError):
            return Response(
                {
                    "success": False,
                    "error": {
                        "status_code": status.HTTP_400_BAD_REQUEST,
                        "message": "The request conflicts with existing data.",
                        "details": {},
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        logger.exception("Unhandled API error", exc_info=exc)
        return Response(
            {
                "success": False,
                "error": {
                    "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "message": "An unexpected error occurred.",
                    "details": {},
                },
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if isinstance(exc, Http404):
        message = "Resource not found."
    else:
        message = _message_from(response.data)

    details = response.data if isinstance(response.data, dict) else {"errors": response.data}
    details = {k: v for k, v in details.items() if k != "detail"}

    response.data = {
        "success": False,
        "error": {
            "status_code": response.status_code,
            "message": message,
            "details": details,
        },
    }
    return response
