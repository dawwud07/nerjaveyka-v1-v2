from django.test import TestCase
from rest_framework.test import APIClient

from .models import ContactRequest, Feedback


class InquiryApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_feedback_and_request_can_be_submitted(self):
        feedback_response = self.client.post(
            '/api/v1/feedbacks/',
            {'name': 'Alex', 'email': 'alex@example.com', 'message': 'Great work'},
            format='json',
        )
        request_response = self.client.post(
            '/api/v1/requests/',
            {'name': 'Alex', 'phone': '+10000000000', 'message': 'Call me'},
            format='json',
        )
        self.assertEqual(feedback_response.status_code, 201)
        self.assertEqual(request_response.status_code, 201)
        self.assertEqual(Feedback.objects.count(), 1)
        self.assertEqual(ContactRequest.objects.count(), 1)

    def test_inquiries_are_submission_only(self):
        self.assertEqual(
            self.client.get('/api/v1/feedbacks/').status_code,
            405,
        )
        self.assertEqual(
            self.client.get('/api/v1/requests/').status_code,
            405,
        )

    def test_swagger_and_schema_are_available(self):
        self.assertEqual(self.client.get('/api/v1/swagger/').status_code, 200)
        schema_response = self.client.get('/api/v1/swagger.json')
        self.assertEqual(schema_response.status_code, 200)
        schema = schema_response.json()
        self.assertEqual(schema['basePath'], '/api/v1')
        schema_paths = schema['paths']
        for endpoint in (
            '/cases/',
            '/cases/{id}/',
            '/categories/',
            '/categories/{id}/',
            '/feedbacks/',
            '/gallery-items/',
            '/gallery-items/{id}/',
            '/products/',
            '/products/{id}/',
            '/requests/',
            '/services/',
            '/services/{id}/',
        ):
            with self.subTest(endpoint=endpoint):
                self.assertIn(endpoint, schema_paths)
        self.assertEqual(
            {
                tag
                for operation in schema_paths.values()
                for details in operation.values()
                if isinstance(details, dict)
                for tag in details.get('tags', [])
            },
            {
                'cases',
                'categories',
                'feedbacks',
                'gallery-items',
                'products',
                'requests',
                'services',
            },
        )

    def test_health_endpoint_is_available(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})
