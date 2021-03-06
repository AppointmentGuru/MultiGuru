# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse
from django.test import (TestCase, override_settings)
from django.conf import settings
from django.contrib.auth import get_user_model

from .testutils import (add_response,
                        get_proxy_headers,
                        create_fake_user,
                        create_fake_group,
                        create_fake_group_and_members,
                        create_fake_hub)
from ..models import Group
import os, requests, responses


class BecomeTestCase(TestCase):

    def setUp(self):
        self.url = reverse('become-list')
        self.group1, self.owner = create_fake_group_and_members('test group')
        self.group2, owner2 = create_fake_group_and_members('test group 2')

    @responses.activate
    def test_can_become(self):
        expected_url = os.environ.get('KONG_OAUTH_ENDPOINT')
        responses.add(
            responses.POST,
            expected_url,
            json={}
        )
        # self.client.login(username=self.owner, password='testtest')
        data = {
            'become_id': self.group1.members[0]
        }
        self.client.post(
            self.url,
            data,
            **get_proxy_headers(self.owner.id))
        # verification is that the request to oauth is made

    @responses.activate
    def test_cannot_become_without_permissions(self):
        self.client.login(username=self.owner, password='testtest')
        data = {
            'become_id': self.group2.members[0]
        }
        res = self.client.post(self.url, data)
        assert res.status_code == 403,\
            'Expected status: {}. Got: {}'.format(403, res.status_code)

class GroupTestCase(TestCase):

    def setUp(self):
        self.group, self.owner = create_fake_group_and_members('test group')
        self.url = reverse('group-expand')
        create_fake_group('group-2')

    @responses.activate
    def test_get_expanded_group(self):
        self.client.login(username=self.owner.username, password='testtest')
        for member in self.group.members:
            path = '/api/client/practitioners/{}/'.format(member)
            add_response(path=path, response_data={"id": member})
        res = self.client.get(self.url)
        assert res.status_code == 200
        assert len(res.json()) == 1
        assert res.json()[0].get('data') is not None

    def test_anon_cannot_create_group(self):
        res = self.client.post(self.url)
        assert res.status_code == 405, \
            'Expected 405. Got: {}'.format(res.status_code)

class HubTestCase(TestCase):

    def setUp(self):
        self.hub = create_fake_hub({"title": "Some Hub"})
        self.url = reverse('hub-list')

    def test_list_hubs(self):
        res = self.client.get(self.url)
        assert res.status_code == 200,\
            'Expected 200. Got: {}'.format(res.status_code)

    def test_anon_cannot_create(self):
        res = self.client.post(self.url)
        assert res.status_code == 403,\
            'Expected 403. Got: {}'.format(res.status_code)

    def test_get_hub_by_slug(self):
        url = reverse('hub-detail', args=(self.hub.slug,))
        res = self.client.get(url)
        assert res.status_code == 200,\
            'Expected 200 OK. Got: {}'.format(res.status_code)
        assert res.json().get('title') == 'Some Hub'

    def test_get_hub_by_id(self):
        url = reverse('hub-detail', args=(self.hub.id,))
        res = self.client.get(url)
        assert res.status_code == 200,\
            'Expected 200 OK. Got: {}'.format(res.status_code)
        assert res.json().get('title') == 'Some Hub'




class ProxyTestCase(TestCase):

    def __add_response(self, path='/api/v2/practitioner/clients/', response_data={}, status=200):
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

class ProxyPOSTTestCase(TestCase):

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

        self.url = '{}?group={}&resource={}'.format(
                        self.url,
                        self.group.id,
                        'appointment')

    @responses.activate
    def test_it_upstreams_a_post_request(self):
        payload = {
            "practitioner": 1,
            "create_process": False,
            "start_time": "2018-02-26 10:45",
            "end_time": "2018-02-26 11:15",
            "product": 16,
            "title": "Christo Crampton",
            "client": 1,
            "source": "dev.tests"
        }
        add_response('/api/appointments/', method='POST', status=201)
        self.client.login(username=self.group_member.username, password='testtest')
        res = self.client.post(self.url, payload)

    def test_upstream_payload(self):
        payload = {
            "practitioner": 1,
            "appointment": 13427,
            "name": "schedule.models.AppointmentProcess.cancel",
            "request_data": "{\"notifications\":false}"
        }
