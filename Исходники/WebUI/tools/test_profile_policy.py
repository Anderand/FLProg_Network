import copy
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
FILE=ROOT/'hardware_gates/STM32_W5500_GATE/STM32_OTA_MANAGER/profile_policy.py'
spec=importlib.util.spec_from_file_location('transfer_profile_policy',FILE)
policy=importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)

class ProfilePolicyTest(unittest.TestCase):
    def setUp(self):
        self.profile=dict(id='transfer_profile',firmware_version='1.0.4-PROFILE',
                          artifacts=dict(bootloader=dict(sha256='a'*64),application=dict(sha256='b'*64)))
        self.pin=dict(firmware_version='1.0.4-PROFILE',artifacts=dict(bootloader='a'*64,application='b'*64))

    def test_bundled_build_visible_without_claiming_hardware_validation(self):
        with patch.dict(policy.BUNDLED_PROFILES,{'transfer_profile':self.pin}):
            self.assertTrue(policy.is_visible(self.profile))
            self.assertFalse(policy.is_verified(self.profile))
            self.assertIn('1.0.4-PROFILE',policy.profile_status(self.profile))
            self.assertIn('не испытывалась',policy.profile_status(self.profile))

    def test_changed_hash_or_version_is_hidden_by_default(self):
        with patch.dict(policy.BUNDLED_PROFILES,{'transfer_profile':self.pin}):
            for kind in ('bootloader','application'):
                changed=copy.deepcopy(self.profile)
                changed['artifacts'][kind]['sha256']='0'*64
                self.assertFalse(policy.is_visible(changed))
            changed=copy.deepcopy(self.profile)
            changed['firmware_version']='other'
            self.assertFalse(policy.is_visible(changed))

    def test_unknown_profile_flag_cannot_claim_default_visibility(self):
        profile=copy.deepcopy(self.profile)
        profile.update(verified=True,hardware_verified=True,bundled=True)
        self.assertFalse(policy.is_visible(profile))
        self.assertTrue(policy.is_visible(profile,True))

    def test_old_verified_profile_and_obsolete_filter_preserved(self):
        profile=dict(id=policy.VERIFIED_ID,firmware_version='1.0.1',artifacts={
            key:dict(sha256=value) for key,value in policy.VERIFIED_HASHES.items()})
        self.assertTrue(policy.is_verified(profile))
        self.assertTrue(policy.is_visible(profile))
        self.assertIn('1.0.1',policy.profile_status(profile))
        profile['id']=next(iter(policy.OBSOLETE_IDS))
        self.assertFalse(policy.is_visible(profile,True))

if __name__=='__main__':unittest.main()
