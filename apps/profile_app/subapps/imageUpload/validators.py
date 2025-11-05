import os
import requests
from django.core.exceptions import ValidationError

def validate_image_content(image):
    """
    uses the sightengine api to check if an image contains inappropriate content.
    raises a ValidationError if the content is deemed inappropriate.
    """
    api_user = os.getenv('SIGHTENGINE_API_USER')
    api_secret = os.getenv('SIGHTENGINE_API_SECRET')

    if not api_user or not api_secret:
        # if credentials are not set, skip validation in development
        # in production, this should probably raise an error or log a warning
        return

    url = 'https://api.sightengine.com/1.0/check.json'
    files = {'media': image}
    params = {
        'models': 'nudity-2.0,offensive',
        'api_user': api_user,
        'api_secret': api_secret
    }

    try:
        response = requests.post(url, files=files, data=params)
        output = response.json()

        if output.get('status') == 'success':
            # check nudity model
            nudity = output.get('nudity', {})
            if nudity.get('sexual_activity') > 0.5 or nudity.get('sexual_display') > 0.5:
                raise ValidationError("image contains sexually explicit content.")

            # check offensive model
            if output.get('offensive', {}).get('prob', 0) > 0.5:
                raise ValidationError("image contains offensive content.")
        else:
            # if sightengine returns a failure status, raise an error
            error_message = output.get('error', {}).get('message', 'unknown sightengine error')
            raise ValidationError(f"image validation failed: {error_message}")

    except requests.RequestException as e:
        # if there's a network error or problem connecting to sightengine
        raise ValidationError(f"could not connect to image validation service: {e}")
