# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse
from django.test import TestCase
from .testutils import create_fake_hub

class HubModelTestCase(TestCase):

    def setUp(self):
        self.hub = create_fake_hub({"title": "Some Hub"})

    def test_it_sets_slug(self):
        assert self.hub.slug == 'some-hub'

    def test_it_doesnt_override_existing_slug(self):
        data = {
            "title": "Some Hub",
            "slug": "some-slug"
        }
        hub = create_fake_hub(data)
        assert hub.slug == "some-slug"