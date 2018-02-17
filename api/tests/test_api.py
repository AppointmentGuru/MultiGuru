# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

from .testutils import (create_fake_user,
                        create_fake_group)

class ProxyTestCase(TestCase):

    def setUp(self):

        self.url = reverse('proxy-list')
        self.group_owner = create_fake_user('jack')
        self.group_member = create_fake_user('jill')
        self.non_member = create_fake_user('jane')

        members = [self.group_owner.id, self.group_member.id]

        self.group = create_fake_group(
                        name='test group',
                        owners=[self.group_owner.id],
                        members=members)

        self.base_params = {
            "group": self.group.id,
            "resource": 'profile'
        }

    def test_gets_appointments_for_all_members(self):
        self.client.login(username=self.group_member.username, password='testtest')
        res = self.client.get(self.url, self.base_params)
        assert res.status_code == 200


    def test_404_if_not_member(self):

        self.client.login(username=self.non_member.username, password='testtest')
        res = self.client.get(self.url, self.base_params)
        assert res.status_code == 404