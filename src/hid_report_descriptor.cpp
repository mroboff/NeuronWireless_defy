/*
 * Copyright (C) 2020  Dygma Lab S.L.
 *
 * This program is free software: you can redistribute it and/or modify it under
 * the terms of the GNU General Public License as published by the Free Software
 * Foundation, version 3.
 *
 * This program is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 * FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
 * details.
 *
 * You should have received a copy of the GNU General Public License along with
 * this program. If not, see <http://www.gnu.org/licenses/>.
 */

/*
 * The purpose of this module is for defining the HID descriptors and functions for
 * getting the USB and BLE HID descriptor versions in hidDefy module
 */

#include "hidDefy.h"

// BLE descriptor: full 200-byte Raw HID report (report ID 5)
const uint8_t hid_report_descriptor_defy[] = HID_DEFY_REPORT_DESCRIPTOR( RAW_USAGE_DEFY );

void hid_report_descriptor_get( const uint8_t ** pp_desc, uint32_t * p_desc_len )
{
    *pp_desc = &hid_report_descriptor_defy[0];
    *p_desc_len = sizeof( hid_report_descriptor_defy );
}

// ── USB descriptor: same reports as BLE but Raw HID uses 63-byte reports ────
//
// USB Full Speed interrupt endpoints are limited to 64 bytes per packet.
// With the 1-byte report ID prepended, the maximum data payload is 63 bytes.
//
// OUTPUT_REPORT_LEN_RAW is only referenced by the Raw HID section of
// HID_DEFY_REPORT_DESCRIPTOR, so expanding the same macro with it redefined to
// 63 yields the USB variant, identical to the BLE one everywhere else. Built
// this way it is a const array in flash: the previous approach patched a RAM
// copy at runtime, which cost 236 bytes of RAM the nRF52833 cannot spare.

#define USB_RAW_HID_REPORT_SIZE 63  // 63 data bytes + 1 report ID = 64-byte USB packet

#pragma push_macro("OUTPUT_REPORT_LEN_RAW")
#undef OUTPUT_REPORT_LEN_RAW
#define OUTPUT_REPORT_LEN_RAW USB_RAW_HID_REPORT_SIZE
static const uint8_t hid_report_descriptor_defy_usb[] = HID_DEFY_REPORT_DESCRIPTOR( RAW_USAGE_DEFY );
#pragma pop_macro("OUTPUT_REPORT_LEN_RAW")

// Both 63 and 200 fit in a 1-byte REPORT_COUNT value, so the two variants must
// have the same length. A mismatch means the macro changed shape.
static_assert( sizeof( hid_report_descriptor_defy_usb ) == sizeof( hid_report_descriptor_defy ),
               "USB and BLE HID descriptors must have the same length" );

void hid_report_descriptor_usb_get( const uint8_t ** pp_desc, uint32_t * p_desc_len )
{
    *pp_desc    = &hid_report_descriptor_defy_usb[0];
    *p_desc_len = sizeof( hid_report_descriptor_defy_usb );
}

void hid_report_descriptor_ble_get( const uint8_t ** pp_desc, uint32_t * p_desc_len )
{
    /* Get the valid descriptor */
    hid_report_descriptor_get( pp_desc, p_desc_len );
}
