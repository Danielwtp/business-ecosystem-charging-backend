# -*- coding: utf-8 -*-

# Copyright (c) 2013 CoNWeT Lab., Universidad Politécnica de Madrid

# This file is part of WStore.

# WStore is free software: you can redistribute it and/or modify
# it under the terms of the European Union Public Licence (EUPL)
# as published by the European Commission, either version 1.1
# of the License, or (at your option) any later version.

# WStore is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# European Union Public Licence for more details.

# You should have received a copy of the European Union Public Licence
# along with WStore.
# If not, see <https://joinup.ec.europa.eu/software/page/eupl/licence-eupl>.

import json
import types
from mock import MagicMock
from nose_parameterized import parameterized
from urllib2 import HTTPError

from django.test import TestCase
from wstore.store_commons.utils.testing import decorator_mock, build_response_mock, decorator_mock_callable


class ExpenditureMock():

    _refresh = False

    def ExpenditureManager(self, rss, cred):
        # build object
        return self.ExpAux(self)

    class ExpAux():
        def __init__(self, classCont):
            self._context = classCont

        def set_credentials(self, cred):
            pass

        def set_provider_limit(self):
            if not self._context._refresh:
                self._context._refresh = True
                raise HTTPError('http://rss.test.com', 401, 'Unauthorized', None, None)


class RSSViewTestCase(TestCase):

    tags = ('rss-view')

    @classmethod
    def setUpClass(cls):
        from wstore.store_commons.utils import http
        # Save the reference of the decorators
        cls._old_auth = types.FunctionType(
            http.authentication_required.func_code,
            http.authentication_required.func_globals,
            name=http.authentication_required.func_name,
            argdefs=http.authentication_required.func_defaults,
            closure=http.authentication_required.func_closure
        )

        cls._old_supp = types.FunctionType(
            http.supported_request_mime_types.func_code,
            http.supported_request_mime_types.func_globals,
            name=http.supported_request_mime_types.func_name,
            argdefs=http.supported_request_mime_types.func_defaults,
            closure=http.supported_request_mime_types.func_closure
        )

        # Mock class decorators
        http.authentication_required = decorator_mock
        http.supported_request_mime_types = decorator_mock_callable

        from wstore.admin.rss import views
        cls.views = views
        cls.views.build_response = build_response_mock
        super(RSSViewTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        # Restore mocked decorators
        from wstore.store_commons.utils import http
        http.authentication_required = cls._old_auth
        http.supported_request_mime_types = cls._old_supp
        super(RSSViewTestCase, cls).tearDownClass()

    def setUp(self):
        # Create user mock
        self.user = MagicMock()
        self.user.userprofile = MagicMock()
        self.user.userprofile.access_token = 'accesstoken'
        self.user.userprofile.refresh_token = 'refreshtoken'
        self.user.is_staff = True

        # Create request mock
        self.request = MagicMock()
        self.request.user = self.user

        # Create context mock
        self.cont_instance = MagicMock()
        self.cont_instance.allowed_currencies = {
            'default': 'EUR',
            'allowed': [{
                'currency': 'EUR'
            }]
        }
        self.cont_instance.is_valid_currency.return_value = True
        self.views.Context = MagicMock()
        self.views.Context.objects = MagicMock()
        self.views.Context.objects.all.return_value = [self.cont_instance]

        # Create RSS mock
        self.rss_object = MagicMock()
        self.views.RSS = MagicMock()
        self.views.RSS.objects = MagicMock()
        self.views.RSS.objects.create.return_value = self.rss_object
        self.views.RSS.objects.get.return_value = self.rss_object
        self.views.RSS.objects.delete = MagicMock()
        self.views.RSS.objects.filter.return_value = []

        from django.conf import settings
        settings.OILAUTH = True

    # Different side effects that can occur
    def _revoke_staff(self):
        self.user.is_staff = False

    def _existing_rss(self):
        self.views.RSS.objects.filter.return_value = [self.rss_object]

    def _invalid_currencies(self):
        self.cont_instance.is_valid_currency.return_value = False

    def _unauthorized(self):
        set_mock = MagicMock()
        set_mock.set_provider_limit.side_effect = HTTPError('http://rss.test.com', 401, 'Unauthorized', None, None)
        self.views.ExpenditureManager = MagicMock()
        self.views.ExpenditureManager.return_value = set_mock

    def _manager_failure(self):
        set_mock = MagicMock()
        set_mock.set_provider_limit.side_effect = Exception('Failure')
        self.views.ExpenditureManager = MagicMock()
        self.views.ExpenditureManager.return_value = set_mock

    def _rss_failure(self):
        set_mock = MagicMock()
        set_mock.set_provider_limit.side_effect = HTTPError('http://rss.test.com', 500, 'Unauthorized', None, None)
        self.views.ExpenditureManager = MagicMock()
        self.views.ExpenditureManager.return_value = set_mock

    @parameterized.expand([
    ({
        'name': 'testrss',
        'host': 'http://rss.test.com/'
    }, False, (201, 'Created', 'correct'), True, {
        'currency': 'EUR',
        'perTransaction':10000,
        'weekly': 100000,
        'daily': 10000,
        'monthly': 100000
    }),
    ({
        'name': 'testrss',
        'host': 'http://rss.test.com/',
        'limits': {
            'currency': 'EUR',
            'perTransaction': '10000',
            'daily': '10000',
            'weekly': '10000',
            'monthly': '10000'
        }
    }, True, (201, 'Created', 'correct'), True, {
        'currency': 'EUR',
        'perTransaction':10000.0,
        'weekly': 10000.0,
        'daily': 10000.0,
        'monthly': 10000.0
    }),
    ({
        'name': 'testrss',
        'host': 'http://rss.test.com/',
        'limits': {
            'currency': 'EUR'
        }
    }, False, (201, 'Created', 'correct'), True, {
        'currency': 'EUR',
        'perTransaction':10000,
        'weekly': 100000,
        'daily': 10000,
        'monthly': 100000
    }),
    ({
        'name': 'testrss',
        'host': 'http://rss.test.com/',
        'limits': {
            'weekly': '1000'
        }
    }, False, (201, 'Created', 'correct'), True, {
        'currency': 'EUR',
        'weekly': 1000.0,
    }),
    ({
        'limits': {
            'currency': 'EUR'
        }
    }, False, (400, 'Invalid JSON content', 'error'), False, {}),
    ({
        'name': 'testrss',
        'host': 'http://rss.test.com/'
    }, False, (403, 'Forbidden', 'error'), False, {}, _revoke_staff),
    ({
        'name': 'testrss',
        'host': 'http://rss.test.com/'
    }, False, (400, 'Invalid JSON content', 'error'), False, {}, _existing_rss),
    ({
        'name': 'testrss',
        'host': 'http://rss.test.com/',
        'limits': {
            'currency': 'euro'
        }
    }, False, (400, 'Invalid currency', 'error'), False, {}, _invalid_currencies),
    ({
        'name': 'testrss',
        'host': 'http://rss.test.com/'
    }, False, (401, "You don't have access to the RSS instance requested", 'error'), False, {}, _unauthorized),
    ({
        'name': 'testrss',
        'host': 'http://rss.test.com/'
    }, False, (400, 'Failure', 'error'), False, {}, _manager_failure),
    ({
        'name': 'testrss',
        'host': 'http://rss.test.com/'
    }, False, (502, 'The RSS has failed creating the expenditure limits', 'error'), False, {}, _rss_failure),
    ])
    def test_rss_creation(self, data, refresh, resp, created, expected_request, side_effect=None):

        # Include data to mock
        self.request.raw_post_data = json.dumps(data)

        # Mock ExpenditureManager
        self.views.ExpenditureManager = MagicMock()

        # Create a mock method to manage the token refresh
        # if needed
        if refresh:
            exp_mock = ExpenditureMock()
            self.views.ExpenditureManager = exp_mock.ExpenditureManager
            # Create social auth mocks
            social_mock = MagicMock()
            filter_mock = MagicMock()
            object_mock = MagicMock()
            object_mock.extra_data = {
                'access_token': 'accesstoken',
                'refresh_token': 'refreshtoken'
            }
            filter_mock.return_value = [object_mock]
            social_mock.filter = filter_mock
            self.request.user.social_auth = social_mock

        # Create the corresponding side effect if needed
        if side_effect:
            side_effect(self)

        # Call the view
        collection = self.views.RSSCollection(permitted_methods=('GET', 'POST'))
        response = collection.create(self.request)

        # Check response
        val = json.loads(response.content)
        self.assertEquals(response.status_code, resp[0])
        self.assertEquals(val['message'], resp[1])
        self.assertEquals(val['result'], resp[2])

        # Check the result depending if the model should
        # have been created
        if created:
            # Check rss call
            self.views.RSS.objects.create.assert_called_with(name=data['name'], host=data['host'], expenditure_limits=expected_request)
            self.assertEquals(self.rss_object.access_token, self.user.userprofile.access_token)
        else:
            self.views.RSS.objects.delete.assert_called_once()

    def _not_found(self):
        self.views.RSS.objects.get = MagicMock()
        self.views.RSS.objects.get.side_effect = Exception('Not found')

    def _invalid_data(self):
        self.request.raw_post_data = None

    def _make_limit_failure(self):
        self.views._make_expenditure_request.return_value = (True, 502, 'RSS failure')

    @parameterized.expand([
    ({
        'name': 'test',
        'limits': {
            'currency': 'EUR',
            'weekly': 100.0
        }
    }, (200, 'OK', 'correct'), False),
    ({}, (200, 'OK', 'correct'), False),
    ({
        'name': 'test',
        'limits': {
            'currency': 'EUR',
            'weekly': 100.0
        }
    }, (404, 'Not found', 'error'), True, _not_found),
    ({
        'name': 'test',
        'limits': {
            'currency': 'EUR',
            'weekly': 100.0
        }
    }, (403, 'Forbidden', 'error'), True, _revoke_staff),
    ({}, (400, 'Invalid JSON data', 'error'), True, _invalid_data),
    ({
        'name': 'existingrss',
        'limits': {
            'currency': 'EUR',
            'weekly': 100.0
        }
    }, (400, 'The selected name is in use', 'error'), True),
    ({
        'name': 'test',
        'limits': {
            'currency': 'EUR',
            'weekly': 100.0
        }
    }, (502, 'RSS failure', 'error'), True, _make_limit_failure),
    ])
    def test_rss_update(self, data, resp, error, side_effect=None):
        # Mock RSS response
        self.views.RSS.objects.filter.return_value = [self.rss_object]

        def get_mock(name=''):
            if name == 'testrss' or name == 'existingrss':
                return self.rss_object
            else:
                raise Exception('')

        self.views.RSS.objects.get = get_mock

        self.request.raw_post_data = json.dumps(data)

        # Mock expenditure manager
        exp_object = MagicMock()
        exp_object.set_provider_limit = MagicMock()
        self.views.ExpenditureManager = MagicMock()
        self.views.ExpenditureManager.return_value = exp_object
        # Mock _make_requests
        self.views._make_expenditure_request = MagicMock()
        self.views._make_expenditure_request.return_value = (False, None, None)

        self.views._check_limits = MagicMock()
        self.views._check_limits.return_value = {
            'currency': 'EUR',
            'weekly': 100.0
        }

        if side_effect:
            side_effect(self)

        # Get entry
        entry = self.views.RSSEntry(permitted_methods=('GET', 'PUT', 'DELETE'))

        response = entry.update(self.request, 'testrss')

        # Check response
        val = json.loads(response.content)
        self.assertEquals(response.status_code, resp[0])
        self.assertEquals(val['message'], resp[1])
        self.assertEquals(val['result'], resp[2])

        if not error and 'limits' in data:
            # Check calls
            self.views._check_limits.assert_called_with(data['limits'])
            self.views._make_expenditure_request.assert_called_with(exp_object, exp_object.set_provider_limit, self.user)

    def test_rss_retrieving(self):
        # Create mocks
        rss_1 = MagicMock()
        rss_1.name = 'test_rss1'
        rss_1.host = 'http://testrss1.org/'
        rss_1.expenditure_limits = {
            'currency': 'EUR',
            'weekly': 100
        }
        rss_2 = MagicMock()
        rss_2.name = 'test_rss2'
        rss_2.host = 'http://testrss2.org/'
        rss_2.expenditure_limits = {
            'currency': 'EUR',
            'monthly': 500
        }
        self.views.RSS.objects.all = MagicMock()
        self.views.RSS.objects.all.return_value = [rss_1, rss_2]

        # Create collection
        coll = self.views.RSSCollection(permitted_methods=('GET', 'POST'))

        response = coll.read(self.request)
        val = json.loads(response.content)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(val), 2)

        for resp in val:
            if resp['name'] == 'test_rss1':
                self.assertEquals(resp['host'], 'http://testrss1.org/')
                limits = resp['limits']
                self.assertEquals(limits['currency'], 'EUR')
                self.assertEquals(limits['weekly'], 100)
            else:
                self.assertEquals(resp['name'], 'test_rss2')
                self.assertEquals(resp['host'], 'http://testrss2.org/')
                limits = resp['limits']
                self.assertEquals(limits['currency'], 'EUR')
                self.assertEquals(limits['monthly'], 500)

    def test_rss_retrieving_entry(self):
        # Create mocks
        rss_1 = MagicMock()
        rss_1.name = 'test_rss1'
        rss_1.host = 'http://testrss1.org/'
        rss_1.expenditure_limits = {
            'currency': 'EUR',
            'weekly': 100
        }
        self.views.RSS.objects.get = MagicMock()
        self.views.RSS.objects.get.return_value = rss_1

        # Create collection
        entry = self.views.RSSEntry(permitted_methods=('GET', 'PUT', 'DELETE'))

        # Check response
        response = entry.read(self.request, 'test_rss1')

        self.views.RSS.objects.get.assert_called_with(name='test_rss1')
        val = json.loads(response.content)
        self.assertEquals(response.status_code, 200)

        self.assertEquals(val['name'], 'test_rss1')
        self.assertEquals(val['host'], 'http://testrss1.org/')
        limits = val['limits']
        self.assertEquals(limits['currency'], 'EUR')
        self.assertEquals(limits['weekly'], 100)

    @parameterized.expand([
    ('test_rss', (204, 'No content', 'correct')),
    ('test_rss1', (404, 'Not found', 'error'), _not_found),
    ('test_rss1', (403, 'Forbidden', 'error'), _revoke_staff),
    ('test_rss1', (502, 'RSS failure', 'error'), _make_limit_failure)
    ])
    def test_rss_deletion(self, name, resp, side_effect=None):
        # create mocks
        self.views._make_expenditure_request = MagicMock()
        self.views._make_expenditure_request.return_value = (False, None, None)

        exp_man = MagicMock()
        self.views.ExpenditureManager = MagicMock()
        self.views.ExpenditureManager.return_value = exp_man

        # Create collection
        entry = self.views.RSSEntry(permitted_methods=('GET', 'PUT', 'DELETE'))

        if side_effect:
            side_effect(self)

        # Check response
        response = entry.delete(self.request, name)

        val = json.loads(response.content)
        self.assertEquals(response.status_code, resp[0])
        self.assertEquals(val['message'], resp[1])
        self.assertEquals(val['result'], resp[2])
