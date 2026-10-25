from django.test import TestCase
from rest_framework.test import APIClient

from .models import Case, Category


class CatalogApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_catalog_endpoints_list_and_read(self):
        category = Category.objects.create(name='Kitchen', slug='kitchen')
        case = Case.objects.create(
            title='Kitchen project',
            slug='kitchen-project',
            category=category,
        )
        for endpoint in (
            '/api/v1/categories/',
            '/api/v1/cases/',
            '/api/v1/gallery-items/',
            '/api/v1/products/',
            '/api/v1/services/',
        ):
            with self.subTest(endpoint=endpoint):
                self.assertEqual(self.client.get(endpoint).status_code, 200)
        self.assertEqual(
            self.client.get(f'/api/v1/cases/{case.pk}/').json()['title'],
            'Kitchen project',
        )

    def test_inactive_case_is_not_public(self):
        case = Case.objects.create(
            title='Hidden project',
            slug='hidden-project',
            is_active=False,
        )
        self.assertEqual(
            self.client.get('/api/v1/cases/').json()['results'],
            [],
        )
        self.assertEqual(
            self.client.get(f'/api/v1/cases/{case.pk}/').status_code,
            404,
        )

    def test_category_filter_search_and_pagination_work(self):
        kitchen = Category.objects.create(name='Kitchen', slug='kitchen')
        bathroom = Category.objects.create(name='Bathroom', slug='bathroom')
        Case.objects.create(
            title='Kitchen renovation',
            slug='kitchen-renovation',
            category=kitchen,
        )
        Case.objects.create(
            title='Bathroom renovation',
            slug='bathroom-renovation',
            category=bathroom,
        )

        response = self.client.get(
            '/api/v1/cases/',
            {'category': kitchen.pk, 'search': 'Kitchen', 'page_size': 1},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['results'][0]['slug'], 'kitchen-renovation')

    def test_catalog_endpoints_reject_write_methods(self):
        response = self.client.post(
            '/api/v1/cases/',
            {'title': 'New case', 'slug': 'new-case'},
            format='json',
        )
        self.assertEqual(response.status_code, 405)
