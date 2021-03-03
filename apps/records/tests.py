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

    @patch('django.utils.timezone.now')
    def test_search_ability(self, mock_now):

        self.assertEqual(Record.objects.count(), 3)

        mock_now.return_value = '2021-01-23'
        Record.objects.create(
            owner=self.test_manager_user,
            distance="45",
            latitude="54",
            longitude="89",
            weather_conditions="clear sky",
        )

        mock_now.return_value = '2020-05-21'
        Record.objects.create(
            owner=self.test_admin_user,
            distance="85",
            latitude="74",
            longitude="105",
            weather_conditions="overcast clouds",
        )

        mock_now.return_value = '2019-07-28'
        Record.objects.create(
            owner=self.test_member_user,
            distance="250",
            latitude="90",
            longitude="180",
            weather_conditions="light rain",
        )

        mock_now.return_value = '2020-12-05'
        Record.objects.create(
            owner=self.test_member_user,
            distance="8500",
            latitude="-33",
            longitude="133",
            weather_conditions="few clouds",
        )

        mock_now.return_value = '2019-07-14'
        Record.objects.create(
            owner=self.test_member_user,
            distance="50060",
            latitude="90",
            longitude="-134",
            weather_conditions="broken clouds",
        )

        mock_now.return_value = '2020-01-01'
        Record.objects.create(
            owner=self.test_member_user,
            distance="8554",
            latitude="48",
            longitude="-79",
            weather_conditions="overcast clouds",
        )

        mock_now.return_value = '2020-12-31'
        Record.objects.create(
            owner=self.test_member_user,
            distance="100",
            latitude="-4",
            longitude="178",
            weather_conditions="overcast clouds",
        )

        self.client.force_authenticate(user=self.test_member_user)
        response = self.client.get(self.list_create_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # member can only list his records
        self.assertEqual(Record.objects.count(), 10)
        self.assertEqual(response.data['count'], 6)

        # test EQ operator
        response = self.client.get(
            self.list_create_url,
            {'search': 'weather_conditions eq overcast clouds'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

        # test NE operator
        response = self.client.get(
            self.list_create_url,
            {'search': 'owner ne 1'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

        response = self.client.get(
            self.list_create_url,
            {'search': 'owner lt 3'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 6)

        # test GT opertor
        response = self.client.get(
            self.list_create_url,
            {'search': 'created gt 2020-01-01'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

        response = self.client.get(
            self.list_create_url,
            {'search': 'created eq 2020-01-01'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

        # test LT operator
        response = self.client.get(
            self.list_create_url,
            {'search': 'distance lt 500'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

        # test AND operator
        response = self.client.get(
            self.list_create_url,
            {'search': '(distance eq 250) and (weather_conditions eq light rain)'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

        # test OR operator
        response = self.client.get(
            self.list_create_url,
            {'search': '(distance eq 250) or (distance eq 8500)'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

        # test operator case insensitivity and any number of spaces in search_phrase
        response = self.client.get(
            self.list_create_url,
            {'search': '(  distance Gt   5000 )     AnD (  distance  Lt 10000)'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

        # test user search phrase case sensitive
        response = self.client.get(
            self.list_create_url,
            {'search': 'Weather_conditions eq Light rain'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # test bad operator
        response = self.client.get(
            self.list_create_url,
            {'search': '(  distance Gt   5000 )     An (  distance  Lt 10000)'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # test bad field name search
        response = self.client.get(
            self.list_create_url,
            {'search': 'speed eq 78'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # test bad field value search
        response = self.client.get(
            self.list_create_url,
            {'search': 'id lt seven'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
