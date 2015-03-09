#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define ENCRYPTION 0
#define DECRYPTION 1

#define DEBUG

/******************************************************************************/
static uint8_t s_blocks[8][16] =
{
    { 0x4, 0xA, 0x9, 0x2, 0xD, 0x8, 0x0, 0xE, 0x6, 0xB, 0x1, 0xC, 0x7, 0xF, 0x5, 0x3 },
    { 0xE, 0xB, 0x4, 0xC, 0x6, 0xD, 0xF, 0xA, 0x2, 0x3, 0x8, 0x1, 0x0, 0x7, 0x5, 0x9 },
    { 0x5, 0x8, 0x1, 0xD, 0xA, 0x3, 0x4, 0x2, 0xE, 0xF, 0xC, 0x7, 0x6, 0x0, 0x9, 0xB },
    { 0x7, 0xD, 0xA, 0x1, 0x0, 0x8, 0x9, 0xF, 0xE, 0x4, 0x6, 0xC, 0xB, 0x2, 0x5, 0x3 },
    { 0x6, 0xC, 0x7, 0x1, 0x5, 0xF, 0xD, 0x8, 0x4, 0xA, 0x9, 0xE, 0x0, 0x3, 0xB, 0x2 },
    { 0x4, 0xB, 0xA, 0x0, 0x7, 0x2, 0x1, 0xD, 0x3, 0x6, 0x8, 0x5, 0x9, 0xC, 0xF, 0xE },
    { 0xD, 0xB, 0x4, 0x1, 0x3, 0xF, 0x5, 0x9, 0x0, 0xA, 0xE, 0x7, 0x6, 0x8, 0x2, 0xC },
    { 0x1, 0xF, 0xD, 0x0, 0x5, 0x7, 0xA, 0x4, 0x9, 0x2, 0x3, 0xE, 0x6, 0xB, 0x8, 0xC }
};
/******************************************************************************/

/* Aux function, swap 2 32-bit numbers */
static inline void swap(uint32_t *a, uint32_t *b)
{
    uint32_t temp = *a;
    *a = *b;
    *b = temp;
}

/* Circular shift */
static inline uint32_t circular_shift(uint32_t number, unsigned short used_bits, unsigned short rotations)
{
    return (number << rotations) | (number >> (used_bits - rotations));
}

/* Calculate subkeys for all rounds */
static void calculate_subkeys(uint32_t subkeys[32], uint64_t key[4])
{
    uint32_t key_parts[] = {
        key[0], key[0] >> 32,
        key[1], key[1] >> 32,
        key[2], key[2] >> 32,
        key[3], key[3] >> 32,
    };

    for (unsigned i = 0; i < 24; ++i)
        subkeys[i] = key_parts[i % 8];
    for (unsigned i = 24; i < 32; ++i)
        subkeys[i] = subkeys[7 - i % 8];
}

static uint32_t f(uint32_t a, uint32_t k)
{
    uint32_t sum = ((uint64_t)a + (uint64_t)k) % 0xFFFFFFFF; /* add 32-bit subkey modulo 32 */

    uint32_t combined = 0;
    for (unsigned i = 0; i < 8; ++i) {
        uint8_t four_bit_sequence = (sum >> (i * 4)) & 0x0F;
        four_bit_sequence = s_blocks[i][four_bit_sequence];
        combined |= ((uint32_t)four_bit_sequence << 4 * i);
    }

    return circular_shift(combined, 32, 11);
}

/* GOST algorithm itself */
static uint64_t gost(uint64_t input, uint64_t key[4], bool mode)
{
    uint32_t a = input;
    uint32_t b = input >> 32;
    
    uint32_t subkeys[32];
    calculate_subkeys(subkeys, key);
    for (unsigned i = 0; i < 32; ++i) {
        uint32_t current_subkey = (mode == ENCRYPTION ? subkeys[i] : subkeys[32-i-1]);
        a ^= f(b, current_subkey);
        swap(&a, &b);
    }
    swap(&a, &b);

    uint64_t result = ((uint64_t)b << 32) | (uint64_t)a;
    return result;
}

int main()
{
    uint64_t key[4];
    char input_text[240];
    memset(input_text, 0, sizeof(input_text));

    puts("Enter the 256-bit key: ");
    scanf("%llx%llx%llx%llx", &key[3], &key[2], &key[1], &key[0]);
    getchar();
    puts("Enter the text to be encrypted: ");
    fgets(input_text, 240, stdin);

    const unsigned block_size = sizeof(uint64_t);
    const unsigned block_count = (strlen(input_text) + sizeof(uint64_t) - 1) / block_size;
    char encrypted_str[strlen(input_text)];
    char decrypted_str[strlen(input_text)];
    for (unsigned i = 0; i < block_count; ++i) {
        uint64_t to_be_encrypted = ((const uint64_t*)input_text)[i];

        uint64_t encrypted = gost(to_be_encrypted, key, ENCRYPTION);
        uint64_t decrypted = gost(encrypted, key, DECRYPTION);
        *(uint64_t*)(encrypted_str + i * block_size) = encrypted;
        *(uint64_t*)(decrypted_str + i * block_size) = decrypted;

#ifdef DEBUG
        printf("to_be_encrypted = %llx, encrypted = %llx, decrypted = %llx\n", to_be_encrypted, encrypted, decrypted);
#endif
    }

    printf("\n Encryption result string representation: %s\n", encrypted_str);
    printf("\n Decryption result string representation: %s\n", decrypted_str);

    return 0;
}
