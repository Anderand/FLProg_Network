"""Visibility policy for shipped and imported STM32 OTA profiles."""

VERIFIED_ID = "fle4d_30mt_ota_block_1_0_1"
VERIFIED_HASHES = {
    "bootloader": "5723f837c36ddba8a7e72acd389773da9d1e7273666282dda0d46dd0c35f8ec6",
    "application": "7b91d259bcce08768ed08533ca69ab3c78aae406a4106754223db251683e61c0",
}
OBSOLETE_IDS = frozenset({
    "fle4d_30mt_ota_block_1_0_0",
    "fle4d_30mt_stm32f407vg_w5500_ota_diag_test_v1",
    "fle4d_30mt_stm32f407vg_w5500_ota_diag_uart_first_v2",
    "fle4d_30mt_stm32f407vg_w5500_v1",
})


def is_verified(profile):
    return (profile.get("id") == VERIFIED_ID
            and all(profile.get("artifacts", {}).get(key, {}).get("sha256") == value
                    for key, value in VERIFIED_HASHES.items()))


def is_visible(profile, show_unverified=False):
    return (profile.get("id") not in OBSOLETE_IDS
            and (show_unverified or is_verified(profile)))
