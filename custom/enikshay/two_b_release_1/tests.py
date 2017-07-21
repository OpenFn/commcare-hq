from django.test import TestCase, override_settings

from casexml.apps.case.const import CASE_INDEX_CHILD
from casexml.apps.case.mock import CaseFactory, CaseStructure, CaseIndex
from corehq.apps.domain.models import Domain
from corehq.form_processor.interfaces.dbaccessors import CaseAccessors

from custom.enikshay.const import ENROLLED_IN_PRIVATE
from custom.enikshay.tests.utils import (
    setup_enikshay_locations,
    get_person_case_structure,
    get_occurrence_case_structure,
    get_episode_case_structure,
    get_test_case_structure,
    get_referral_case_structure,
    get_trail_case_structure,
)
from .management.commands.enikshay_2b_case_properties import ENikshay2BMigrator


@override_settings(TESTS_SHOULD_USE_SQL_BACKEND=True)
class TestCreateEnikshayCases(TestCase):
    domain = 'enikshay-2b-migration'

    def setUp(self):
        self.project = Domain(name=self.domain)
        self.project.save()
        self.location_types, self.locations = setup_enikshay_locations(self.domain)
        self.factory = CaseFactory(domain=self.domain)
        self.cases = self.setup_cases()

    def tearDown(self):
        self.project.delete()

    def setup_cases(self):
        private_person = self._get_person_structure('susanna-dean', self.locations['PHI'].location_id)
        private_person.attrs['update'][ENROLLED_IN_PRIVATE] = 'true'  # should be excluded
        person = self._get_person_structure('roland-deschain', self.locations['PHI'].location_id)
        occurrence = self._get_occurrence_structure(person)
        episode = self._get_episode_structure(occurrence)
        test = self._get_test_structure(occurrence)
        referral = self._get_referral_structure(person)
        trail = self._get_trail_structure(referral)
        return {c.case_id: c for c in self.factory.create_or_update_cases([
            private_person, episode, test, referral, trail
        ])}

    def _get_person_structure(self, person_id, owner_id):
        person_fields = {ENROLLED_IN_PRIVATE: ""}
        person = get_person_case_structure(person_id, owner_id, extra_update=person_fields)
        person.attrs['owner_id'] = owner_id
        person.attrs['update'].update({
            'phi_area': 'phi_area',
            'date_referred_out': 'date_referred_out',
            'date_by_id': 'date_by_id',
            'phone_number': '1234567890',
        })
        return person

    def _get_occurrence_structure(self, person):
        case_id = person.case_id + '-occurrence'
        return get_occurrence_case_structure(case_id, person)

    def _get_episode_structure(self, occurrence):
        case_id = occurrence.case_id + '-episode'
        episode = get_episode_case_structure(case_id, occurrence)
        episode.attrs['update'].update({
            'episode_type': "confirmed_tb",
            'alcohol_history': "alcohol_history",
            'alcohol_deaddiction': "alcohol_deaddiction",
            'tobacco_user': "tobacco_user",
            'occupation': "occupation",
            'nikshay_id': "nikshay_id",
            'phone_number_other': "phone_number_other",
            'disease_classification': 'disease_classification',
            'site_choice': 'site_choice',
            'site_detail': 'site_detail',
            'key_population_status': 'key_population_status',
            'key_populations': 'key_populations',
        })
        return episode

    def _get_test_structure(self, occurrence):
        case_id = occurrence.case_id + '-test'
        return get_test_case_structure(case_id, occurrence.case_id)

    def _get_referral_structure(self, person):
        case_id = person.case_id + '-referral'
        return get_referral_case_structure(case_id, person.case_id)

    def _get_trail_structure(self, referral):
        case_id = referral.case_id + '-trail'
        trail = get_trail_case_structure(case_id, "overriding this anyways")
        trail.indices = [CaseIndex(
            CaseStructure(case_id=referral.case_id, attrs={"create": False}),
            identifier='parent',
            relationship=CASE_INDEX_CHILD,
            related_type='referral',
        )]
        return trail

    def test(self):
        migrator = ENikshay2BMigrator(self.domain, self.locations['DTO'], commit=True)
        # first check some utils
        person_case_ids = migrator.get_relevant_person_case_ids()
        person_case_sets = list(migrator.get_relevant_person_case_sets(person_case_ids))
        self.assertEqual(1, len(person_case_sets))
        person = person_case_sets[0]
        self.assertEqual('roland-deschain', person.person.case_id)
        self.assertItemsEqual(['roland-deschain-occurrence'], [c.case_id for c in person.occurrences])
        self.assertItemsEqual(['roland-deschain-occurrence-episode'], [c.case_id for c in person.episodes])
        self.assertItemsEqual(['roland-deschain-occurrence-test'], [c.case_id for c in person.tests])
        self.assertItemsEqual(['roland-deschain-referral'], [c.case_id for c in person.referrals])
        self.assertItemsEqual(['roland-deschain-referral-trail'], [c.case_id for c in person.trails])

        # run the actual migration
        migrator.migrate()

        # check the results
        accessor = CaseAccessors(self.domain)
        new_person = accessor.get_case(person.person.case_id)
        self.assertDictContainsSubset({
            'area': 'phi_area',
            'referred_outside_enikshay_date': 'date_referred_out',
            'referred_outside_enikshay_by_id': 'date_by_id',
            'contact_phone_number': '911234567890',
            'current_episode_type': "confirmed_tb",
            'alcohol_history': "alcohol_history",
            'alcohol_deaddiction': "alcohol_deaddiction",
            'tobacco_user': "tobacco_user",
            'occupation': "occupation",
            'nikshay_id': "nikshay_id",
            'phone_number_other': "phone_number_other",
            'phi_name': 'PHI',
            'tu_name': 'TU',
            'tu_id': self.locations['TU'].location_id,
            'dto_name': 'DTO',
            'dto_id': self.locations['DTO'].location_id,
        }, new_person.dynamic_case_properties())

        new_occurrence = accessor.get_case(person.occurrences[0].case_id)
        self.assertDictContainsSubset({
            'current_episode_type': 'confirmed_tb',
            'disease_classification': 'disease_classification',
            'site_choice': 'site_choice',
            'site_detail': 'site_detail',
            'key_population_status': 'key_population_status',
            'key_populations': 'key_populations',
        }, new_occurrence.dynamic_case_properties())
