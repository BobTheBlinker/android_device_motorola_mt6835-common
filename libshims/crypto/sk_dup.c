/*
 * SPDX-FileCopyrightText: The LineageOS Project
 * SPDX-License-Identifier: Apache-2.0
 */

#include <openssl/stack.h>

// BoringSSL now only exports OPENSSL_sk_dup; the stock wifi blobs import sk_dup.
OPENSSL_STACK* sk_dup(const OPENSSL_STACK* sk) {
    return OPENSSL_sk_dup(sk);
}
