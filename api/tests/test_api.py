# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse
from django.test import TestCase
from django.conf import settings
from django.contrib.auth import get_user_model

from .testutils import (add_response,
                        create_fake_user,
                        create_fake_group,
                        create_fake_group_and_members)

import requests, responses

class AuthTestCase(TestCase):

    def test_auths_user(self):
        pass

class GroupTestCase(TestCase):

    def setUp(self):
        self.group, self.owner = create_fake_group_and_members('test group')
        self.url = reverse('group-expand', args=(self.group.id,))

    @responses.activate
    def test_get_expanded_group(self):
        self.client.login(username=self.owner.username, password='testtest')
        for member in self.group.members:
            path = '/api/client/practitioners/{}/'.format(member)
            add_response(path=path, response_data={"id": member})
        res = self.client.get(self.url)
        assert res.status_code == 200
        assert res.json().get('data') is not None

class ProxyTestCase(TestCase):

    def __add_response(self, path='/api/clients/', response_data={}, status=200):
        url = 'http://appointmentguru{}'.format(path)
        responses.add(
            responses.GET,
            url,
            json=response_data,
            status=status)

    def setUp(self):

        self.url = reverse('proxy-list')
        self.group_owner = create_fake_user('jack')
        self.group_member = create_fake_user('jill')
        self.non_member = create_fake_user('jane')

        self.member_ids = [self.group_owner.id, self.group_member.id]

        self.group = create_fake_group(
                        name='test group',
                        owners=[self.group_owner.id],
                        members=self.member_ids)

        self.base_params = {
            "group": self.group.id,
            "resource": 'client'
        }

    @responses.activate
    def test_gets_appointments_for_all_members(self):
        self.__add_response()
        self.client.login(username=self.group_member.username, password='testtest')
        res = self.client.get(self.url, self.base_params)
        assert res.status_code == 200

    @responses.activate
    def test_gets_all_params_passed(self):
        self.__add_response()
        params = self.base_params

        self.client.login(username=self.group_member.username, password='testtest')
        res = self.client.get(self.url, params)

    @responses.activate
    def test_it_works_with_urls_with_ids(self):
        for id in self.member_ids:
            self.__add_response(path='/api/client/practitioners/{}/'.format(id))
        params = self.base_params
        params['resource'] = 'profile'
        self.client.login(username=self.group_member.username, password='testtest')

        res = self.client.get(self.url, params)
        assert res.status_code == 200

    @responses.activate
    def test_404_if_not_member(self):

        self.client.login(username=self.non_member.username, password='testtest')
        res = self.client.get(self.url, self.base_params)
        assert res.status_code == 404