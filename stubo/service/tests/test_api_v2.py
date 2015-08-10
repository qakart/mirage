"""  
    :copyright: (c) 2015 by OpenCredo.
    :license: GPLv3, see LICENSE for more details.
"""

# -*- coding: utf-8 -*-
import json
from stubo.testing import Base
import logging

log = logging.getLogger(__name__)


class TestScenarioOperations(Base):

    def test_put_scenario(self):
        """

        Test scenario insertion with correct details
        """
        response = self._test_insert_scenario()
        self.assertEqual(response.code, 201)
        self.assertEqual(response.headers["Content-Type"],
                         'application/json; charset=UTF-8')
        payload = json.loads(response.body)
        # check if scenario ref link and name are available in payload
        self.assertEqual(payload['scenarioRef'], '/stubo/api/v2/scenarios/objects/localhost:scenario_0001')
        self.assertEqual(payload['name'], 'localhost:scenario_0001')

    def _test_insert_scenario(self, name="scenario_0001"):
        """
        Inserts test scenario
        :return: response from future
        """
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios'), self.stop,
                               method="PUT", body='{"scenario": "%s"}' % name)

        response = self.wait()
        return response

    def test_put_scenario_no_body(self):
        """

        Test scenario insertion with empty body
        """
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios'), self.stop,
                               method="PUT", body="")
        response = self.wait()
        self.assertEqual(response.code, 415, response.reason)
        self.assertEqual(response.reason, 'No JSON body found')

    def test_put_scenario_wrong_body(self):
        """

        Pass a JSON body to put scenario function although do not supply "scenario" key with name
        """
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios'), self.stop,
                               method="PUT", body='{"foo": "bar"}')
        response = self.wait()
        self.assertEqual(response.code, 400, response.reason)
        self.assertEqual(response.reason, 'Scenario name not supplied')

    def test_put_duplicate_scenario(self):
        """

        Test duplicate insertion and error handling
        """
        response = self._test_insert_scenario()
        self.assertEqual(response.code, 201)
        # insert it second time
        response = self._test_insert_scenario()
        self.assertEqual(response.code, 422, response.reason)
        self.assertTrue('already exists' in response.reason)

    def test_put_scenario_name_none(self):
        """

        Test blank scenario name insertion
        """
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios'), self.stop,
                               method="PUT", body='{"scenario": "" }')
        response = self.wait()
        self.assertEqual(response.code, 400, response.reason)
        self.assertTrue('name is blank or contains illegal characters' in response.reason)

    def test_put_scenario_name_w_illegal_chars(self):
        """

        Test scenario name with illegal characters insertion
        """
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios'), self.stop,
                               method="PUT", body='{"scenario": "@foo" }')
        response = self.wait()
        self.assertEqual(response.code, 400, response.reason)
        self.assertTrue('name is blank or contains illegal characters' in response.reason)
        self.assertTrue('@foo' in response.reason)

    def test_put_scenario_name_w_hostname(self):
        """

        Test override function - providing hostname for stubo to create a scenario with it
        """
        response = self._test_insert_scenario(name="hostname:scenario_name_x")
        self.assertEqual(response.code, 201)
        payload = json.loads(response.body)
        # check if scenario ref link and name are available in payload
        self.assertEqual(payload['scenarioRef'], '/stubo/api/v2/scenarios/objects/hostname:scenario_name_x')
        self.assertEqual(payload['name'], 'hostname:scenario_name_x')

    def test_get_all_scenarios(self):
        """

        Test getting multiple scenarios
        """
        # creating some scenarios
        for scenario_number in xrange(5):
            response = self._test_insert_scenario(name="scenario_name_with_no_%s" % scenario_number)
            self.assertEqual(response.code, 201)

        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios'), self.stop, method="GET")
        response = self.wait()
        self.assertEqual(response.code, 200)
        payload = json.loads(response.body)
        self.assertTrue('scenarios' in payload)
        self.assertEqual(len(payload['scenarios']), 5)

    def test_get_all_scenarios_with_details(self):
        """

        Test getting multiple scenarios with details
        """
        # creating some scenarios
        for scenario_number in xrange(5):
            response = self._test_insert_scenario(name="scenario_name_with_no_%s" % scenario_number)
            self.assertEqual(response.code, 201)

        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/detail'), self.stop, method="GET")
        response = self.wait()
        self.assertEqual(response.code, 200)
        payload = json.loads(response.body)
        self.assertTrue('scenarios' in payload)
        self.assertTrue('name' in payload['scenarios'][1])
        self.assertTrue('recorded' in payload['scenarios'][1])
        self.assertTrue('space_used_kb' in payload['scenarios'][1])
        self.assertTrue('stub_count' in payload['scenarios'][1])
        self.assertEqual(len(payload['scenarios']), 5)

    def test_get_all_scenarios_with_post_method(self):
        """

        Test getting multiple scenarios with details using POST, PUT methods
        """
        # using PUT method
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/detail'), self.stop,
                               method="PUT", body='{"foo": "bar"}')
        response = self.wait()
        self.assertEqual(response.code, 405, response.reason)

        # using POST method
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/detail'), self.stop,
                               method="POST", body='{"foo": "bar"}')
        response = self.wait()
        self.assertEqual(response.code, 405, response.reason)

        # using DELETE method
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/detail'), self.stop,
                               method="DELETE")
        response = self.wait()
        self.assertEqual(response.code, 405, response.reason)

    def test_get_scenario_details(self):
        """

        Test get scenario details, should also do a basic check of details provided
        """
        response = self._test_insert_scenario("new_scenario_details")
        self.assertEqual(response.code, 201)

        # get inserted scenario
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/objects/new_scenario_details'),
                               self.stop, method="GET")
        response = self.wait()
        self.assertEqual(response.code, 200, response.reason)
        payload = json.loads(response.body)
        self.assertEqual(payload['scenarioRef'], '/stubo/api/v2/scenarios/objects/localhost:new_scenario_details')
        self.assertEqual(payload['name'], 'localhost:new_scenario_details')
        self.assertEqual(payload['space_used_kb'], 0)

    def test_delete_scenario(self):
        """

        Test scenario deletion
        """
        response = self._test_insert_scenario("new_scenario_for_deletion")
        self.assertEqual(response.code, 201)

        # delete scenario
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/objects/new_scenario_for_deletion'),
                               self.stop, method="DELETE")
        response = self.wait()
        self.assertEqual(response.code, 200, response.reason)

    def test_non_existing_delete_scenario(self):
        """

        Test scenario deletion
        """
        response = self._test_insert_scenario("new_scenario_for_deletion")
        self.assertEqual(response.code, 201)

        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/objects/new_scenario_for_deletion'),
                               self.stop, method="DELETE")
        response = self.wait()
        self.assertEqual(response.code, 200, response.reason)

        # trying to delete scenario again
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/objects/new_scenario_for_deletion'),
                               self.stop, method="DELETE")
        response = self.wait()
        # expecting to get "precondition failed"
        self.assertEqual(response.code, 412, response.reason)

class TestSessionOperations(Base):

    def _test_insert_scenario(self, name="scenario_0001"):
        """
        Inserts test scenario
        :return: response from future
        """
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios'), self.stop,
                               method="PUT", body='{"scenario": "%s"}' % name)

        response = self.wait()
        return response

    def test_begin_n_end_session(self):
        """

        Test begin session
        """
        response = self._test_insert_scenario("new_scenario_0x")
        self.assertEqual(response.code, 201)

        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/objects/new_scenario_0x/action'),
                               self.stop,
                               method="POST",
                               body='{ "begin": null, "session": "session_name", "mode": "record" }')
        response = self.wait()
        self.assertEqual(response.code, 200, response.reason)
        body_dict = json.loads(response.body)['data']
        self.assertEqual(body_dict['status'], 'record')
        self.assertEqual(body_dict['session'], 'session_name')
        # splitting scenario name and comparing only scenario name (removing hostname)
        self.assertEqual(body_dict['scenario'].split(":")[1], 'new_scenario_0x')
        self.assertTrue('scenarioRef' in body_dict)
        self.assertTrue('message' in body_dict)

        # ending session
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/objects/new_scenario_0x/action'),
                               self.stop,
                               method="POST",
                               body='{ "end": null, "session": "session_name" }')
        response = self.wait()
        self.assertEqual(response.code, 200, response.reason)

    def test_end_all_sessions(self):
        """

        Test end all sessions - creating scenario, then multiple sessions setting to record, then to dormant.
        """
        response = self._test_insert_scenario("new_scenario_0x")
        self.assertEqual(response.code, 201)

        session_count = 10
        # inserting some sessions
        for session_number in xrange(session_count):
            self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/objects/new_scenario_0x/action'),
                                   self.stop,
                                   method="POST",
                                   body='{ "begin": null, "session": "session_name_%s", "mode": "record" }'
                                        % session_number)
            response = self.wait()
            self.assertEqual(response.code, 200, response.reason)

        # ordering stubo to finish them all!
        self.http_client.fetch(self.get_url('/stubo/api/v2/scenarios/objects/new_scenario_0x/action'),
                               self.stop,
                               method="POST",
                               body='{ "end": "sessions"}')
        response = self.wait()
        self.assertEqual(response.code, 200, response.reason)
        # checking whether 10 sessions were affected
        self.assertEqual(len(json.loads(response.body)['data']), 10)

    def test_setting_playback(self):
        """

        Test playback
        """
        # TODO: implement this test after stub creation through API v2 is available
        pass


