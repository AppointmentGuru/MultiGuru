# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase

from .testutils import (
    create_fake_group,
    create_fake_group_and_members
)

from ..helpers import can_become

class CanBecomeTestCase(TestCase):

    def setUp(self):
        self.group1, self.owner = create_fake_group_and_members('test group')
        self.group2, owner2 = create_fake_group_and_members('test group 2')

    def test_can_become_positive_case(self):
        member1 = self.group1.members[0]
        member2 = self.group1.members[1]
        assert can_become(member1, member2) == True

    def test_become_fails_if_they_are_not_members_of_the_same_group(self):

        member1 = self.group1.members[0]
        member2 = self.group2.members[0]
        assert can_become(member1, member2) == False