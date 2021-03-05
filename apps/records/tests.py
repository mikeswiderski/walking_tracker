from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.records.models import Record
from apps.users.models import User


class RecordsTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.test_member_user = User.objects.create_user(
            username='testmemberuser',
            email='testmemberuser@users.com',
            password='testmemberpassword',
            role=User.MEMBER,
        )

        self.test_manager_user = User.objects.create_user(
            username='testmanageruser',
            email='testmanageruser@users.com',
            password='testmanagerpassword',
            role=User.MANAGER,
        )

        self.test_admin_user = User.objects.create_user(
            username='testadminuser',
            email='testadminuser@users.com',
            password='testadminpassword',
            role=User.ADMIN,
        )

        self.test_member_record = Record.objects.create(
            owner=self.test_member_user,
            distance="45",
            latitude="54",
            longitude="89",
            weather_conditions="clear sky",
        )

        self.test_manager_record = Record.objects.create(
            owner=self.test_manager_user,
            distance="65",
            latitude="59",
            longitude="-29",
            weather_conditions="cloudy",
        )

        self.test_admin_record = Record.objects.create(
            owner=self.test_admin_user,
            distance="450",
            latitude="24",
            longitude="-59",
            weather_conditions="rain",
        )

        self.list_create_url = reverse('record-create-list')

    def test_anonymous_cant_create_record(self):
        data = {
            "distance": 56,
            "latitude": 46,
            "longitude": -120,
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(Record.objects.count(), 3)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('apps.records.serializers.get_weather')
    def test_weather_api(self, mock_get_weather):
        mock_get_weather.return_value = 'clear'
        data = {
            "distance": 56,
            "latitude": 46,
            "longitude": -120,
        }
        self.client.force_authenticate(user=self.test_member_user)
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(mock_get_weather.called, True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Record.objects.count(), 4)
        self.assertEqual(response.data["weather_conditions"], "clear")

    @patch('apps.records.serializers.get_weather')
    def test_member_can_create_record_for_himself(self, mock_get_weather):
        mock_get_weather.return_value = 'clear'
        data = {
            "distance": 56,
            "latitude": 46,
            "longitude": -120,
        }
        self.client.force_authenticate(user=self.test_member_user)
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Record.objects.count(), 4)
        self.assertEqual(response.data["owner"], self.test_member_user.id)

    @patch('apps.records.serializers.get_weather')
    def test_member_cant_create_record_for_manager_only_for_himself(self, mock_get_weather):
        mock_get_weather.return_value = 'clear'
        data = {
            "owner": self.test_manager_user.id,
            "distance": 56,
            "latitude": 46,
            "longitude": -120,
        }
        self.client.force_authenticate(user=self.test_member_user)
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Record.objects.count(), 4)
        self.assertEqual(response.data["owner"], self.test_member_user.id)

    @patch('apps.records.serializers.get_weather')
    def test_member_cant_create_record_for_admin_only_for_himself(self, mock_get_weather):
        mock_get_weather.return_value = 'clear'
        data = {
            "owner": self.test_admin_user.id,
            "distance": 56,
            "latitude": 46,
            "longitude": -120,
        }
        self.client.force_authenticate(user=self.test_member_user)
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Record.objects.count(), 4)
        self.assertEqual(response.data["owner"], self.test_member_user.id)

    @patch('apps.records.serializers.get_weather')
    def test_member_cant_create_record_for_another_member_only_for_himself(self, mock_get_weather):
        mock_get_weather.return_value = 'clear'

        another_member = User.objects.create_user(
            username='memberuser',
            email='memberuser@users.com',
            password='memberpassword',
            role=User.MEMBER,
        )

        data = {
            "owner": another_member.id,
            "distance": 56,
            "latitude": 46,
            "longitude": -120,
        }

        self.client.force_authenticate(user=self.test_member_user)
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Record.objects.count(), 4)
        self.assertEqual(response.data["owner"], self.test_member_user.id)

    @patch('apps.records.serializers.get_weather')
    def test_manager_can_create_record_for_himself(self, mock_get_weather):
        mock_get_weather.return_value = 'rain'
        data = {
            "distance": 56,
            "latitude": 46,
            "longitude": -120,
        }
        self.client.force_authenticate(user=self.test_manager_user)
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Record.objects.count(), 4)
        self.assertEqual(response.data["owner"], self.test_manager_user.id)

    @patch('apps.records.serializers.get_weather')
    def test_manager_cant_create_record_for_member_only_for_himself(self, mock_get_weather):
        mock_get_weather.return_value = 'rain'
        data = {
            "owner": self.test_member_user.id,
            "distance": 56,
            "latitude": 46,
            "longitude": -120,
        }
        self.client.force_authenticate(user=self.test_manager_user)
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Record.objects.count(), 4)
        self.assertEqual(response.data["owner"], self.test_manager_user.id)

    @patch('apps.records.serializers.get_weather')
    def test_manager_cant_create_record_for_admin_only_for_himself(self, mock_get_weather):
        mock_get_weather.return_value = 'rain'
        data = {
            "owner": self.test_admin_user.id,
            "distance": 56,
            "latitude": 46,
            "longitude": -120,
        }
        self.client.force_authenticate(user=self.test_manager_user)
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Record.objects.count(), 4)
        self.assertEqual(response.data["owner"], self.test_manager_user.id)

    @patch('apps.records.serializers.get_weather')
    def test_manager_cant_create_record_for_another_manager_only_for_himself(self, mock_get_weather):
        mock_get_weather.return_value = 'rain'

        another_manager = User.objects.create_user(
            username='manageruser',
            email='manageruser@users.com',
            password='managerpassword',
            role=User.MANAGER,
        )

        data = {
            "owner": another_manager.id,
            "distance": 56,
            "latitude": 46,
            "longitude": -120,
        }

        self.client.force_authenticate(user=self.test_manager_user)
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Record.objects.count(), 4)
        self.assertEqual(response.data["owner"], self.test_manager_user.id)

    @patch('apps.records.serializers.get_weather')
    def test_admin_can_create_record_for_himself(self, mock_get_weather):
        mock_get_weather.return_value = 'sunny'
        data = {
            "owner": self.test_admin_user.id,
            "distance": 56,
            "latitude": 46,
            "longitude": -120,
        }
        self.client.force_authenticate(user=self.test_admin_user)
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Record.objects.count(), 4)
        self.assertEqual(response.data["owner"], self.test_admin_user.id)

    @patch('apps.records.serializers.get_weather')
    def test_admin_can_create_record_for_member(self, mock_get_weather):
        mock_get_weather.return_value = 'sunny'
        data = {
            "owner": self.test_member_user.id,
            "distance": 56,
            "latitude": 46,
            "longitude": -120,
        }
        self.client.force_authenticate(user=self.test_admin_user)
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Record.objects.count(), 4)
        self.assertEqual(response.data["owner"], self.test_member_user.id)

    @patch('apps.records.serializers.get_weather')
    def test_admin_can_create_record_for_manager(self, mock_get_weather):
        mock_get_weather.return_value = 'sunny'
        data = {
            "owner": self.test_manager_user.id,
            "distance": 56,
            "latitude": 46,
            "longitude": -120,
        }
        self.client.force_authenticate(user=self.test_admin_user)
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Record.objects.count(), 4)
        self.assertEqual(response.data["owner"], self.test_manager_user.id)

    @patch('apps.records.serializers.get_weather')
    def test_admin_can_create_record_for_another_admin(self, mock_get_weather):
        mock_get_weather.return_value = 'sunny'

        another_admin = User.objects.create_user(
            username='adminuser',
            email='adminuser@users.com',
            password='adminpassword',
            role=User.ADMIN,
        )

        data = {
            "owner": another_admin.id,
            "distance": 56,
            "latitude": 46,
            "longitude": -120,
        }

        self.client.force_authenticate(user=self.test_admin_user)
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Record.objects.count(), 4)
        self.assertEqual(response.data["owner"], another_admin.id)

    def test_member_can_list_only_his_own_records(self):
        self.assertEqual(Record.objects.count(), 3)
        self.client.force_authenticate(user=self.test_member_user)
        response = self.client.get(self.list_create_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(
            response.data['results'][0].get('owner'),
            self.test_member_user.id,
        )

    def test_manager_can_list_only_his_own_records(self):
        self.assertEqual(Record.objects.count(), 3)
        self.client.force_authenticate(user=self.test_manager_user)
        response = self.client.get(self.list_create_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(
            response.data['results'][0].get('owner'),
            self.test_manager_user.id,
        )

    def test_admin_can_list_all_records(self):
        self.assertEqual(Record.objects.count(), 3)
        self.client.force_authenticate(user=self.test_admin_user)
        response = self.client.get(self.list_create_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        self.assertEqual(
            response.data['results'][0].get('owner'),
            self.test_admin_user.id,
        )
        self.assertEqual(
            response.data['results'][1].get('owner'),
            self.test_manager_user.id,
        )
        self.assertEqual(
            response.data['results'][2].get('owner'),
            self.test_member_user.id,
        )

    def test_member_can_detail_delate_only_his_own_records(self):
        self.assertEqual(Record.objects.count(), 3)
        self.client.force_authenticate(user=self.test_member_user)

        response = self.client.get(
            reverse('record-detail-delete',
                    kwargs={'pk': self.test_manager_record.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.delete(
            reverse('record-detail-delete',
                    kwargs={'pk': self.test_manager_record.id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.get(
            reverse('record-detail-delete',
                    kwargs={'pk': self.test_admin_record.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.delete(
            reverse('record-detail-delete',
                    kwargs={'pk': self.test_admin_record.id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.get(
            reverse('record-detail-delete',
                    kwargs={'pk': self.test_member_record.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(
            reverse('record-detail-delete',
                    kwargs={'pk': self.test_member_record.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Record.objects.count(), 2)

    def test_manager_can_detail_delate_only_his_own_records(self):
        self.assertEqual(Record.objects.count(), 3)
        self.client.force_authenticate(user=self.test_manager_user)

        response = self.client.get(
            reverse('record-detail-delete',
                    kwargs={'pk': self.test_member_record.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.delete(
            reverse('record-detail-delete',
                    kwargs={'pk': self.test_member_record.id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.get(
            reverse('record-detail-delete',
                    kwargs={'pk': self.test_admin_record.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.delete(
            reverse('record-detail-delete',
                    kwargs={'pk': self.test_admin_record.id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.get(
            reverse('record-detail-delete',
                    kwargs={'pk': self.test_manager_record.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(
            reverse('record-detail-delete',
                    kwargs={'pk': self.test_manager_record.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Record.objects.count(), 2)

    def test_admin_can_detail_delate_any_record(self):
        self.assertEqual(Record.objects.count(), 3)
        self.client.force_authenticate(user=self.test_admin_user)

        response = self.client.get(
            reverse('record-detail-delete',
                    kwargs={'pk': self.test_member_record.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(
            reverse('record-detail-delete',
                    kwargs={'pk': self.test_member_record.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Record.objects.count(), 2)

        response = self.client.get(
            reverse('record-detail-delete',
                    kwargs={'pk': self.test_manager_record.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(
            reverse('record-detail-delete',
                    kwargs={'pk': self.test_manager_record.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Record.objects.count(), 1)

        response = self.client.get(
            reverse('record-detail-delete',
                    kwargs={'pk': self.test_admin_record.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(
            reverse('record-detail-delete',
                    kwargs={'pk': self.test_admin_record.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Record.objects.count(), 0)

    def test_member_can_request_only_his_monthly_activity_record(self):
        self.client.force_authenticate(user=self.test_member_user)
        response = self.client.get(
            reverse('record-average-distance',
                    kwargs={'user_id': self.test_member_user.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(
            reverse('record-average-distance',
                    kwargs={'user_id': self.test_manager_user.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.get(
            reverse('record-average-distance',
                    kwargs={'user_id': self.test_admin_user.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_manager_can_request_only_his_monthly_activity_record(self):
        self.client.force_authenticate(user=self.test_manager_user)
        response = self.client.get(
            reverse(
                'record-average-distance',
                kwargs={'user_id': self.test_manager_user.id}),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(
            reverse('record-average-distance',
                    kwargs={'user_id': self.test_member_user.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.get(
            reverse('record-average-distance',
                    kwargs={'user_id': self.test_admin_user.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_request_any_user_monthly_activity_record(self):
        self.client.force_authenticate(user=self.test_admin_user)
        response = self.client.get(
            reverse('record-average-distance',
                    kwargs={'user_id': self.test_admin_user.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(
            reverse('record-average-distance',
                    kwargs={'user_id': self.test_member_user.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(
            reverse('record-average-distance',
                    kwargs={'user_id': self.test_manager_user.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_cant_request_his_monthly_activity_record_providing_only_year(self):
        self.client.force_authenticate(user=self.test_member_user)
        response = self.client.get(
            reverse('record-average-distance',
                    kwargs={'user_id': self.test_member_user.id}),
            {'year': 2021}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_cant_request_his_monthly_activity_record_providing_only_month(self):
        self.client.force_authenticate(user=self.test_member_user)
        response = self.client.get(
            reverse('record-average-distance',
                    kwargs={'user_id': self.test_member_user.id}),
            {'month': 1}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_cant_request_his_monthly_activity_record_providing_non_int_args(self):
        self.client.force_authenticate(user=self.test_member_user)
        response = self.client.get(
            reverse('record-average-distance',
                    kwargs={'user_id': self.test_member_user.id}),
            {'year': 'two', 'month': 'six'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_request_his_monthly_activity_record_providing_int_args(self):
        self.client.force_authenticate(user=self.test_member_user)
        response = self.client.get(
            reverse('record-average-distance',
                    kwargs={'user_id': self.test_member_user.id}),
            {'year': 2021, 'month': 6}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_get_current_monthly_and_year_activity_record_if_args_not_provided(self):
        self.client.force_authenticate(user=self.test_member_user)
        response = self.client.get(
            reverse('record-average-distance',
                    kwargs={'user_id': self.test_member_user.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('average_distance'),
            float(self.test_member_record.distance),
        )
