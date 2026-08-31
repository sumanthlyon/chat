import os
import statistics
import time
from pathlib import Path

import pandas as pd

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import (
    padding,
    rsa,
)
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


ITERATIONS = 100

MESSAGE_SIZES = {
    "10 B": 10,
    "100 B": 100,
    "1 KB": 1024,
    "10 KB": 10 * 1024,
    "100 KB": 100 * 1024,
}


RESULTS_DIR = (
    Path(__file__).resolve().parent
    / "results"
)

RESULTS_DIR.mkdir(
    exist_ok=True
)


print("=" * 70)
print("CRYPTOGRAPHIC PERFORMANCE BENCHMARK")
print("=" * 70)


# ============================================
# GENERATE RSA KEY PAIR ONCE
# ============================================

print("\nGenerating RSA key pair...")

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

public_key = private_key.public_key()


# ============================================
# BENCHMARK
# ============================================

all_results = []


for size_name, size_bytes in MESSAGE_SIZES.items():

    print(
        f"\nTesting message size: {size_name}"
    )

    aes_encrypt_times = []
    aes_decrypt_times = []

    rsa_encrypt_times = []
    rsa_decrypt_times = []

    total_encrypt_times = []
    total_decrypt_times = []

    ciphertext_sizes = []


    for iteration in range(ITERATIONS):

        plaintext = os.urandom(
            size_bytes
        )

        # ------------------------------------
        # Generate AES-256 key
        # ------------------------------------

        aes_key = AESGCM.generate_key(
            bit_length=256
        )

        aesgcm = AESGCM(
            aes_key
        )

        nonce = os.urandom(
            12
        )


        # ====================================
        # TOTAL ENCRYPTION TIMER
        # ====================================

        total_encrypt_start = (
            time.perf_counter_ns()
        )


        # AES encryption
        aes_encrypt_start = (
            time.perf_counter_ns()
        )

        ciphertext = aesgcm.encrypt(
            nonce,
            plaintext,
            None,
        )

        aes_encrypt_end = (
            time.perf_counter_ns()
        )


        # RSA wrap AES key
        rsa_encrypt_start = (
            time.perf_counter_ns()
        )

        encrypted_aes_key = (
            public_key.encrypt(
                aes_key,
                padding.OAEP(
                    mgf=padding.MGF1(
                        algorithm=hashes.SHA256()
                    ),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )
        )

        rsa_encrypt_end = (
            time.perf_counter_ns()
        )


        total_encrypt_end = (
            time.perf_counter_ns()
        )


        # ====================================
        # TOTAL DECRYPTION TIMER
        # ====================================

        total_decrypt_start = (
            time.perf_counter_ns()
        )


        # RSA unwrap AES key
        rsa_decrypt_start = (
            time.perf_counter_ns()
        )

        decrypted_aes_key = (
            private_key.decrypt(
                encrypted_aes_key,
                padding.OAEP(
                    mgf=padding.MGF1(
                        algorithm=hashes.SHA256()
                    ),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )
        )

        rsa_decrypt_end = (
            time.perf_counter_ns()
        )


        decrypted_aesgcm = AESGCM(
            decrypted_aes_key
        )


        # AES decryption
        aes_decrypt_start = (
            time.perf_counter_ns()
        )

        decrypted_plaintext = (
            decrypted_aesgcm.decrypt(
                nonce,
                ciphertext,
                None,
            )
        )

        aes_decrypt_end = (
            time.perf_counter_ns()
        )


        total_decrypt_end = (
            time.perf_counter_ns()
        )


        if decrypted_plaintext != plaintext:
            raise RuntimeError(
                "Decryption verification failed"
            )


        # Convert nanoseconds to milliseconds
        aes_encrypt_times.append(
            (
                aes_encrypt_end
                - aes_encrypt_start
            )
            / 1_000_000
        )

        aes_decrypt_times.append(
            (
                aes_decrypt_end
                - aes_decrypt_start
            )
            / 1_000_000
        )

        rsa_encrypt_times.append(
            (
                rsa_encrypt_end
                - rsa_encrypt_start
            )
            / 1_000_000
        )

        rsa_decrypt_times.append(
            (
                rsa_decrypt_end
                - rsa_decrypt_start
            )
            / 1_000_000
        )

        total_encrypt_times.append(
            (
                total_encrypt_end
                - total_encrypt_start
            )
            / 1_000_000
        )

        total_decrypt_times.append(
            (
                total_decrypt_end
                - total_decrypt_start
            )
            / 1_000_000
        )

        ciphertext_sizes.append(
            len(ciphertext)
        )


    result = {
        "message_size":
            size_name,

        "message_bytes":
            size_bytes,

        "iterations":
            ITERATIONS,

        "aes_encrypt_mean_ms":
            statistics.mean(
                aes_encrypt_times
            ),

        "aes_encrypt_median_ms":
            statistics.median(
                aes_encrypt_times
            ),

        "aes_decrypt_mean_ms":
            statistics.mean(
                aes_decrypt_times
            ),

        "aes_decrypt_median_ms":
            statistics.median(
                aes_decrypt_times
            ),

        "rsa_wrap_mean_ms":
            statistics.mean(
                rsa_encrypt_times
            ),

        "rsa_unwrap_mean_ms":
            statistics.mean(
                rsa_decrypt_times
            ),

        "total_encrypt_mean_ms":
            statistics.mean(
                total_encrypt_times
            ),

        "total_decrypt_mean_ms":
            statistics.mean(
                total_decrypt_times
            ),

        "ciphertext_mean_bytes":
            statistics.mean(
                ciphertext_sizes
            ),
    }


    all_results.append(
        result
    )


    print(
        f"AES encrypt mean: "
        f"{result['aes_encrypt_mean_ms']:.4f} ms"
    )

    print(
        f"AES decrypt mean: "
        f"{result['aes_decrypt_mean_ms']:.4f} ms"
    )

    print(
        f"RSA wrap mean: "
        f"{result['rsa_wrap_mean_ms']:.4f} ms"
    )

    print(
        f"RSA unwrap mean: "
        f"{result['rsa_unwrap_mean_ms']:.4f} ms"
    )

    print(
        f"Total encrypt mean: "
        f"{result['total_encrypt_mean_ms']:.4f} ms"
    )

    print(
        f"Total decrypt mean: "
        f"{result['total_decrypt_mean_ms']:.4f} ms"
    )


# ============================================
# SAVE RESULTS
# ============================================

results_df = pd.DataFrame(
    all_results
)


output_file = (
    RESULTS_DIR
    / "crypto_benchmark.csv"
)


results_df.to_csv(
    output_file,
    index=False,
)


print("\n")
print("=" * 70)
print("BENCHMARK FINISHED")
print("=" * 70)


print(
    f"\nResults saved to:\n"
    f"{output_file}"
)