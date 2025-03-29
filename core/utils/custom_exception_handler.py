"""
Custom exception handler for the REST Framework.
This provides consistent error responses across the API.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom exception handler for REST framework that formats error responses.
    
    Args:
        exc: The exception that was raised
        context: The context of the exception
        
    Returns:
        Response object with a standardized error format
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # If response is None, there was an unhandled exception
    if response is None:
        return Response(
            {
                'success': False,
                'message': 'An unexpected error occurred.',
                'error': str(exc),
                'data': None
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Add custom formatting to the response
    error_response = {
        'success': False,
        'message': 'An error occurred while processing your request.',
        'error': response.data if hasattr(response, 'data') else str(exc),
        'data': None
    }
    
    # If the error data is a list, take the first item as the main message
    if isinstance(response.data, list) and len(response.data) > 0:
        error_response['message'] = str(response.data[0])
    # If the error data is a dict with a detail key, use that as the main message
    elif isinstance(response.data, dict) and 'detail' in response.data:
        error_response['message'] = str(response.data['detail'])
    
    response.data = error_response
    
    return response 