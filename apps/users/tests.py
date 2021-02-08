from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.users.models import User


class UsersTests(APITestCase):

    def setUp(self):
        self.token_url = reverse('token_obtain_pair')

        self.client = APIClient()
        self.memberusername = 'testmemberuser'
        self.memberpassword = 'testmemberpassword'
        self.test_member_user = User.objects.create_user(
            username='testmemberuser',
            email='testmemberuser@users.com',
            password='testmemberpassword',
            role=User.MEMBER,
        )

        response = self.client.post(
            self.token_url,
            {'username': self.memberusername, 'password': self.memberpassword},
            format='json',
        )
        self.member_token = response.data['access']

        self.managerusername = 'testmanageruser'
        self.managerpassword = 'testmanagerpassword'
        self.test_manager_user = User.objects.create_user(
            username='testmanageruser',
            email='testmanageruser@users.com',
            password='testmanagerpassword',
            role=User.MANAGER,
        )

        response = self.client.post(
            self.token_url,
            {'username': self.managerusername, 'password': self.managerpassword},
            format='json',
        )
        self.manager_token = response.data['access']

        self.adminusername = 'testadminuser'
        self.adminpassword = 'testadminpassword'
        self.test_admin_user = User.objects.create_user(
            username='testadminuser',
            email='testadminuser@users.com',
            password='testadminpassword',
            role=User.ADMIN,
        )

        response = self.client.post(
            self.token_url,
            {'username': self.adminusername, 'password': self.adminpassword},
            format='json',
        )
        self.admin_token = response.data['access']

        self.list_create_url = reverse('user-create-list')

    def test_create_user_with_short_password(self):
        """
        Ensure user is not created for password lengths less than 8.
        """
        data = {
            'username': 'testuser',
            'email': 'testuser@users.com',
            'password': 'test',
            'role': User.MEMBER,
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 3)

    def test_create_user_with_no_password(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@users.com',
            'password': '',
            'role': User.MEMBER,
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 3)

    def test_create_user_with_too_long_username(self):
        data = {
            'username': 't'*33,
            'email': 'testuser@users.com',
            'password': 'testpassword',
            'role': User.MEMBER,
        }

        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 3)

    def test_create_user_with_no_username(self):
        data = {
            'username': '',
            'email': 'testuser@users.com',
            'password': 'testpassword',
            'role': User.MEMBER,
        }

        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 3)

    def test_create_user_with_preexisting_username(self):
        data = {
            'username': 'testmemberuser',
            'email': 'testuser@users.com',
            'password': 'testpassword',
            'role': User.MEMBER,
        }

        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 3)

    def test_create_user_with_preexisting_email(self):
        data = {
            'username': 'testuser',
            'email': 'testadminuser@users.com',
            'password': 'testpassword',
            'role': User.MEMBER,
        }

        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 3)

    def test_create_user_with_invalid_email(self):
        data = {
            'username': 'testuser',
            'email': 'test@user@users.com',
            'password': 'testpassword',
            'role': User.MEMBER,
        }

        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 3)

    def test_create_user_with_no_email(self):
        data = {
            'username': 'testuser',
            'email': '',
            'password': 'testpassword',
            'role': User.MEMBER,
        }

        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 3)

    def test_anonymous_can_create_member(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@users.com',
            'password': 'testpassword',
            'role': User.MEMBER,
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(User.objects.count(), 4)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_anonymous_cant_create_manager(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@users.com',
            'password': 'testpassword',
            'role': User.MANAGER,
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_anonymous_cant_create_admin(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@users.com',
            'password': 'testpassword',
            'role': User.ADMIN,
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_anonymous_cant_list_users(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_member_can_only_list_himself(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@users.com',
            'password': 'testpassword',
            'role': User.MEMBER,
        }
        self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(User.objects.count(), 4)
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'], [{
            'id': 4,
            'username': 'testuser',
            'email': 'testuser@users.com',
            'role': User.MEMBER,
        }])

    def test_member_can_create_member(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@users.com',
            'password': 'testpassword',
            'role': User.MEMBER,
        }
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.member_token)
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(User.objects.count(), 4)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_member_cant_create_manager(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@users.com',
            'password': 'testpassword',
            'role': User.MANAGER,
        }
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.member_token)
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_member_cant_create_admin(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@users.com',
            'password': 'testpassword',
            'role': User.ADMIN,
        }
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.member_token)
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_member_can_detail_edit_delete_himself(self):
        data = {
            'username': 'testmemberuser',
            'email': 'testuser@users.com',
            'password': 'testmemberpassword',
            'role': User.MEMBER,
        }
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.member_token)
        response = self.client.get(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_member_user.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': self.test_member_user.id,
            'username': 'testmemberuser',
            'email': 'testmemberuser@users.com',
            'role': User.MEMBER
        })
        response = self.client.put(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_member_user.id}),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': self.test_member_user.id,
            'username': 'testmemberuser',
            'email': 'testuser@users.com',
            'role': User.MEMBER
        })

        response = self.client.get(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_member_user.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': self.test_member_user.id,
            'username': 'testmemberuser',
            'email': 'testuser@users.com',
            'role': User.MEMBER
        })

        response = self.client.patch(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_member_user.id}),
            {'email': 'newuser@users.com'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': self.test_member_user.id,
            'username': 'testmemberuser',
            'email': 'newuser@users.com',
            'role': User.MEMBER
        })

        response = self.client.get(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_member_user.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': self.test_member_user.id,
            'username': 'testmemberuser',
            'email': 'newuser@users.com',
            'role': User.MEMBER
        })

        response = self.client.delete(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_member_user.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_member_can_edit_his_password(self):
        data = {
            'password': 'testpassword',
        }
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.member_token)
        response = self.client.patch(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_member_user.id}),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(
            self.token_url,
            {'username': self.memberusername, 'password': 'testpassword'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)

    def test_member_cant_detail_edit_delete_other_member(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@users.com',
            'password': 'testpassword',
            'role': User.MEMBER,
        }
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.member_token)
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(User.objects.count(), 4)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(
            reverse('user-detail-update-delete',
                    kwargs={'pk': User.objects.filter(username='testuser').first().id}),
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_member_cant_change_permission_level_to_manager(self):
        data = {
            'username': 'testmemberuser',
            'email': 'testmemberuser@users.com',
            'password': 'testmemberpassword',
            'role': User.MANAGER,
        }
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.member_token)
        response = self.client.put(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_member_user.id}),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.patch(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_member_user.id}),
            {'role': User.MANAGER},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_member_cant_change_permission_level_to_admin(self):
        data = {
            'username': 'testmemberuser',
            'email': 'testmemberuser@users.com',
            'password': 'testmemberpassword',
            'role': User.ADMIN,
        }
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.member_token)
        response = self.client.put(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_member_user.id}),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.patch(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_member_user.id}),
            {'role': User.ADMIN},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_member_cant_detail_edit_delete_manager(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.member_token)
        response = self.client.get(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_manager_user.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_member_cant_detail_edit_delete_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.member_token)
        response = self.client.get(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_manager_user.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_manager_can_create_member(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@users.com',
            'password': 'testpassword',
            'role': User.MEMBER,
        }
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.manager_token)
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(User.objects.count(), 4)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_manager_can_create_manager(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@users.com',
            'password': 'testpassword',
            'role': User.MANAGER,
        }
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.manager_token)
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(User.objects.count(), 4)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_manager_cant_create_admin(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@users.com',
            'password': 'testpassword',
            'role': User.ADMIN,
        }
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.manager_token)
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_manager_can_list_all_users(self):
        self.assertEqual(User.objects.count(), 3)
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.manager_token)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        self.assertEqual(response.data['results'], [
            {
                'id': self.test_member_user.id,
                'username': 'testmemberuser',
                'email': 'testmemberuser@users.com',
                'role': User.MEMBER,
            },
            {
                'id': self.test_manager_user.id,
                'username': 'testmanageruser',
                'email': 'testmanageruser@users.com',
                'role': User.MANAGER,
            },
            {
                'id': self.test_admin_user.id,
                'username': 'testadminuser',
                'email': 'testadminuser@users.com',
                'role': User.ADMIN,
            },
        ])

    def test_manager_can_detail_edit_delete_himself(self):
        data = {
            'username': 'testmanageruser',
            'email': 'testuser@users.com',
            'password': 'testmanagerpassword',
            'role': User.MANAGER,
        }
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.manager_token)
        response = self.client.get(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_manager_user.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': self.test_manager_user.id,
            'username': 'testmanageruser',
            'email': 'testmanageruser@users.com',
            'role': User.MANAGER
        })
        response = self.client.put(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_manager_user.id}),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': self.test_manager_user.id,
            'username': 'testmanageruser',
            'email': 'testuser@users.com',
            'role': User.MANAGER
        })
        response = self.client.get(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_manager_user.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': self.test_manager_user.id,
            'username': 'testmanageruser',
            'email': 'testuser@users.com',
            'role': User.MANAGER
        })

        response = self.client.patch(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_manager_user.id}),
            {"password": "testpassword"},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': self.test_manager_user.id,
            'username': 'testmanageruser',
            'email': 'testuser@users.com',
            'role': User.MANAGER
        })
        response = self.client.get(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_manager_user.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': self.test_manager_user.id,
            'username': 'testmanageruser',
            'email': 'testuser@users.com',
            'role': User.MANAGER
        })

        response = self.client.patch(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_manager_user.id}),
            {"role": User.MEMBER},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': self.test_manager_user.id,
            'username': 'testmanageruser',
            'email': 'testuser@users.com',
            'role': User.MEMBER
        })
        response = self.client.get(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_manager_user.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': self.test_manager_user.id,
            'username': 'testmanageruser',
            'email': 'testuser@users.com',
            'role': User.MEMBER
        })

        response = self.client.delete(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_manager_user.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_manager_can_edit_his_password(self):
        data = {
            'password': 'testpassword',
        }
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.manager_token)
        response = self.client.patch(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_manager_user.id}),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(
            self.token_url,
            {'username': self.managerusername, 'password': 'testpassword'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)

    def test_manager_can_detail_edit_delete_member(self):
        data = {
            'username': 'testmemberuser',
            'email': 'testuser@users.com',
            'password': 'testmemberpassword',
            'role': User.MEMBER,
        }
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.manager_token)
        response = self.client.get(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_member_user.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': self.test_member_user.id,
            'username': 'testmemberuser',
            'email': 'testmemberuser@users.com',
            'role': User.MEMBER
        })
        response = self.client.put(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_member_user.id}),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': self.test_member_user.id,
            'username': 'testmemberuser',
            'email': 'testuser@users.com',
            'role': User.MEMBER
        })
        response = self.client.get(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_member_user.id}),
        )
        self.assertEqual(response.data, {
            'id': self.test_member_user.id,
            'username': 'testmemberuser',
            'email': 'testuser@users.com',
            'role': User.MEMBER
        })

        response = self.client.patch(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_member_user.id}),
            {'email': 'newuser@users.com', 'role': User.MANAGER},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': self.test_member_user.id,
            'username': 'testmemberuser',
            'email': 'newuser@users.com',
            'role': User.MANAGER
        })
        response = self.client.get(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_member_user.id}),
        )
        self.assertEqual(response.data, {
            'id': self.test_member_user.id,
            'username': 'testmemberuser',
            'email': 'newuser@users.com',
            'role': User.MANAGER
        })

        response = self.client.delete(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_member_user.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_manager_can_detail_edit_delete_other_manager(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@users.com',
            'password': 'testpassword',
            'role': User.MANAGER,
        }
        data_2 = {
            'username': 'testuser',
            'email': 'test@users.com',
            'password': 'testpassword',
            'role': User.MANAGER,
        }
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.manager_token)
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(User.objects.count(), 4)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(
            reverse('user-detail-update-delete',
                    kwargs={'pk': User.objects.filter(username='testuser').first().id}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': User.objects.filter(username='testuser').first().id,
            'username': 'testuser',
            'email': 'testuser@users.com',
            'role': User.MANAGER,
        })
        response = self.client.put(
            reverse('user-detail-update-delete',
                    kwargs={'pk': User.objects.filter(username='testuser').first().id}),
            data_2,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': User.objects.filter(username='testuser').first().id,
            'username': 'testuser',
            'email': 'test@users.com',
            'role': User.MANAGER
        })
        response = self.client.get(
            reverse('user-detail-update-delete',
                    kwargs={'pk': User.objects.filter(username='testuser').first().id}),
        )
        self.assertEqual(response.data, {
            'id': User.objects.filter(username='testuser').first().id,
            'username': 'testuser',
            'email': 'test@users.com',
            'role': User.MANAGER
        })

        response = self.client.patch(
            reverse('user-detail-update-delete',
                    kwargs={'pk': User.objects.filter(username='testuser').first().id}),
            {'role': User.MEMBER},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': User.objects.filter(username='testuser').first().id,
            'username': 'testuser',
            'email': 'test@users.com',
            'role': User.MEMBER
        })
        response = self.client.get(
            reverse('user-detail-update-delete',
                    kwargs={'pk': User.objects.filter(username='testuser').first().id}),
        )
        self.assertEqual(response.data, {
            'id': User.objects.filter(username='testuser').first().id,
            'username': 'testuser',
            'email': 'test@users.com',
            'role': User.MEMBER
        })

        response = self.client.delete(
            reverse('user-detail-update-delete',
                    kwargs={'pk': User.objects.filter(username='testuser').first().id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_manager_cant_detail_edit_delete_admin(self):
        data = {
            'username': 'testadminuser',
            'email': 'testuser@users.com',
            'password': 'testadminpassword',
            'role': User.ADMIN,
        }
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.manager_token)
        response = self.client.get(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_admin_user.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.put(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_admin_user.id}),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.patch(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_admin_user.id}),
            {'email': 'testuser@users.com'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.delete(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_admin_user.id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_manager_can_change_permission_level_to_manager(self):
        data = {
            'role': User.MANAGER,
        }
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.manager_token)
        response = self.client.patch(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_member_user.id}),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_member_user.id}),
        )
        self.assertEqual(response.data, {
            'id': self.test_member_user.id,
            'username': 'testmemberuser',
            'email': 'testmemberuser@users.com',
            'role': User.MANAGER
        })

    def test_manager_can_change_permission_level_to_member(self):
        data = {
            'role': User.MEMBER,
        }
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.manager_token)
        response = self.client.patch(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_manager_user.id}),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_manager_user.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': self.test_manager_user.id,
            'username': 'testmanageruser',
            'email': 'testmanageruser@users.com',
            'role': User.MEMBER
        })

    def test_manager_cant_change_permission_level_to_admin(self):
        data = {
            'role': User.ADMIN,
        }
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.manager_token)
        response = self.client.patch(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_member_user.id}),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_can_create_member(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@users.com',
            'password': 'testpassword',
            'role': User.MEMBER,
        }
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.admin_token)
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(User.objects.count(), 4)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_can_create_manager(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@users.com',
            'password': 'testpassword',
            'role': User.MANAGER,
        }
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.admin_token)
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(User.objects.count(), 4)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_can_create_admin(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@users.com',
            'password': 'testpassword',
            'role': User.ADMIN,
        }
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.admin_token)
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(User.objects.count(), 4)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_can_list_all_users(self):
        self.assertEqual(User.objects.count(), 3)
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.admin_token)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        self.assertEqual(response.data['results'], [
            {
                'id': self.test_member_user.id,
                'username': 'testmemberuser',
                'email': 'testmemberuser@users.com',
                'role': User.MEMBER,
            },
            {
                'id': self.test_manager_user.id,
                'username': 'testmanageruser',
                'email': 'testmanageruser@users.com',
                'role': User.MANAGER,
            },
            {
                'id': self.test_admin_user.id,
                'username': 'testadminuser',
                'email': 'testadminuser@users.com',
                'role': User.ADMIN,
            },
        ])

    def test_admin_can_detail_edit_delete_himself(self):
        data = {
            'username': 'testadminuser',
            'email': 'testuser@users.com',
            'password': 'testadminpassword',
            'role': User.ADMIN,
        }

        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.admin_token)
        response = self.client.get(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_admin_user.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': self.test_admin_user.id,
            'username': 'testadminuser',
            'email': 'testadminuser@users.com',
            'role': User.ADMIN
        })
        response = self.client.put(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_admin_user.id}),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': self.test_admin_user.id,
            'username': 'testadminuser',
            'email': 'testuser@users.com',
            'role': User.ADMIN
        })
        response = self.client.get(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_admin_user.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': self.test_admin_user.id,
            'username': 'testadminuser',
            'email': 'testuser@users.com',
            'role': User.ADMIN
        })

        response = self.client.patch(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_admin_user.id}),
            {'email': 'newuser@users.com'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': self.test_admin_user.id,
            'username': 'testadminuser',
            'email': 'newuser@users.com',
            'role': User.ADMIN
        })
        response = self.client.get(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_admin_user.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': self.test_admin_user.id,
            'username': 'testadminuser',
            'email': 'newuser@users.com',
            'role': User.ADMIN
        })

        response = self.client.delete(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_admin_user.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_admin_can_edit_his_password(self):
        data = {
            'password': 'testpassword',
        }
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.admin_token)
        response = self.client.patch(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_admin_user.id}),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(
            self.token_url,
            {'username': self.adminusername, 'password': 'testpassword'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)

    def test_admin_can_detail_edit_delete_member(self):
        data = {
            'username': 'testmemberuser',
            'email': 'testuser@users.com',
            'password': 'testmemberpassword',
            'role': User.MEMBER,
        }
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.admin_token)
        response = self.client.get(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_member_user.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': self.test_member_user.id,
            'username': 'testmemberuser',
            'email': 'testmemberuser@users.com',
            'role': User.MEMBER
        })
        response = self.client.put(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_member_user.id}),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': self.test_member_user.id,
            'username': 'testmemberuser',
            'email': 'testuser@users.com',
            'role': User.MEMBER
        })
        response = self.client.get(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_member_user.id}),
        )
        self.assertEqual(response.data, {
            'id': self.test_member_user.id,
            'username': 'testmemberuser',
            'email': 'testuser@users.com',
            'role': User.MEMBER
        })

        response = self.client.patch(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_member_user.id}),
            {'email': 'newuser@users.com', 'role': User.ADMIN},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': self.test_member_user.id,
            'username': 'testmemberuser',
            'email': 'newuser@users.com',
            'role': User.ADMIN
        })
        response = self.client.get(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_member_user.id}),
        )
        self.assertEqual(response.data, {
            'id': self.test_member_user.id,
            'username': 'testmemberuser',
            'email': 'newuser@users.com',
            'role': User.ADMIN
        })

        response = self.client.delete(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_member_user.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_admin_can_detail_edit_delete_manager(self):
        data = {
            'username': 'testmanageruser',
            'email': 'testuser@users.com',
            'password': 'testmanagerpassword',
            'role': User.MANAGER,
        }
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.admin_token)
        response = self.client.get(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_manager_user.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': self.test_manager_user.id,
            'username': 'testmanageruser',
            'email': 'testmanageruser@users.com',
            'role': User.MANAGER
        })
        response = self.client.put(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_manager_user.id}),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': self.test_manager_user.id,
            'username': 'testmanageruser',
            'email': 'testuser@users.com',
            'role': User.MANAGER
        })
        response = self.client.get(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_manager_user.id}),
        )
        self.assertEqual(response.data, {
            'id': self.test_manager_user.id,
            'username': 'testmanageruser',
            'email': 'testuser@users.com',
            'role': User.MANAGER
        })

        response = self.client.patch(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_manager_user.id}),
            {'email': 'newuser@users.com'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': self.test_manager_user.id,
            'username': 'testmanageruser',
            'email': 'newuser@users.com',
            'role': User.MANAGER
        })
        response = self.client.get(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_manager_user.id}),
        )
        self.assertEqual(response.data, {
            'id': self.test_manager_user.id,
            'username': 'testmanageruser',
            'email': 'newuser@users.com',
            'role': User.MANAGER
        })

        response = self.client.delete(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_manager_user.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_admin_can_detail_edit_delete_other_admin(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@users.com',
            'password': 'testpassword',
            'role': User.ADMIN,
        }
        data_2 = {
            'username': 'testuser',
            'email': 'test@users.com',
            'password': 'testpassword',
            'role': User.ADMIN,
        }
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.admin_token)
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(User.objects.count(), 4)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(
            reverse('user-detail-update-delete',
                    kwargs={'pk': User.objects.filter(username='testuser').first().id}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': User.objects.filter(username='testuser').first().id,
            'username': 'testuser',
            'email': 'testuser@users.com',
            'role': User.ADMIN,
        })
        response = self.client.put(
            reverse('user-detail-update-delete',
                    kwargs={'pk': User.objects.filter(username='testuser').first().id}),
            data_2,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': User.objects.filter(username='testuser').first().id,
            'username': 'testuser',
            'email': 'test@users.com',
            'role': User.ADMIN
        })
        response = self.client.get(
            reverse('user-detail-update-delete',
                    kwargs={'pk': User.objects.filter(username='testuser').first().id}),
        )
        self.assertEqual(response.data, {
            'id': User.objects.filter(username='testuser').first().id,
            'username': 'testuser',
            'email': 'test@users.com',
            'role': User.ADMIN
        })

        response = self.client.patch(
            reverse('user-detail-update-delete',
                    kwargs={'pk': User.objects.filter(username='testuser').first().id}),
            {'email': 'newtest@users.com'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'id': User.objects.filter(username='testuser').first().id,
            'username': 'testuser',
            'email': 'newtest@users.com',
            'role': User.ADMIN
        })
        response = self.client.get(
            reverse('user-detail-update-delete',
                    kwargs={'pk': User.objects.filter(username='testuser').first().id}),
        )
        self.assertEqual(response.data, {
            'id': User.objects.filter(username='testuser').first().id,
            'username': 'testuser',
            'email': 'newtest@users.com',
            'role': User.ADMIN
        })

        response = self.client.delete(
            reverse('user-detail-update-delete',
                    kwargs={'pk': User.objects.filter(username='testuser').first().id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_admin_can_change_permission_level_to_manager(self):
        data = {
            'role': User.MANAGER,
        }
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.admin_token)
        response = self.client.patch(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_member_user.id}),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_member_user.id}),
        )
        self.assertEqual(response.data, {
            'id': self.test_member_user.id,
            'username': 'testmemberuser',
            'email': 'testmemberuser@users.com',
            'role': User.MANAGER,
        })

    def test_admin_can_change_permission_level_to_member(self):
        data = {
            'role': User.MEMBER,
        }
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.admin_token)
        response = self.client.patch(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_manager_user.id}),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_manager_user.id}),
        )
        self.assertEqual(response.data, {
            'id': self.test_manager_user.id,
            'username': 'testmanageruser',
            'email': 'testmanageruser@users.com',
            'role': User.MEMBER
        })

    def test_admin_can_change_permission_level_to_admin(self):
        data = {
            'role': User.ADMIN,
        }
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.admin_token)
        response = self.client.patch(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_manager_user.id}),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(
            reverse('user-detail-update-delete',
                    kwargs={'pk': self.test_manager_user.id}),
        )
        self.assertEqual(response.data, {
            'id': self.test_manager_user.id,
            'username': 'testmanageruser',
            'email': 'testmanageruser@users.com',
            'role': User.ADMIN
        })
