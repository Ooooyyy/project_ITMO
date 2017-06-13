from django.test import TestCase
import requests

# Create your tests here.
owner_response = requests.get('http://127.0.0.1:8000/todolists/{}/'.format(8),
                            headers=dict(Authorization=request.session['Authorization'])).json()
print(owner_response)