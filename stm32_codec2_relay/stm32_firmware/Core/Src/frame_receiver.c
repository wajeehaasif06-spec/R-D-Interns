/*
 * frame_receiver.c
 *
 *  Created on: 20-Jul-2026
 *      Author: Rayan
 */
/*
 * frame_receiver.c
 *
 * Codec2 packet relay: receive framed packets from PC, validate, retransmit
 * -----------------------------------------------------------------------------
 * Packet format (matches crc8()/send_bits() in codec2_audio_chain.py exactly):
 *
 *     [0x55] [LEN] [LEN bytes of Codec2 payload] [CRC8 of payload]
 *
 * PC --(USART3, VCP)--> STM32 --(USART2, retransmit)--> Logic analyzer
 *                            |
 *                            +--> ENABLE GPIO, bracketing the retransmit
 *                            +--> stats echoed back to PC over USART3
 *                            +--> TIM2 (1us tick) measures inter-frame timing
 */

#include "main.h"
#include <string.h>
#include <stdio.h>

#define PACKET_START_BYTE   0x55
#define MAX_PAYLOAD_BYTES   32
#define STATS_REPORT_EVERY  50

extern UART_HandleTypeDef huart3;
extern UART_HandleTypeDef huart2;
extern TIM_HandleTypeDef htim2;

typedef enum {
    WAIT_START,
    WAIT_LEN,
    READ_PAYLOAD,
    WAIT_CRC
} rx_state_t;

static rx_state_t state = WAIT_START;
static uint8_t payload[MAX_PAYLOAD_BYTES];
static uint8_t payload_len = 0;
static uint8_t payload_pos = 0;
static uint8_t rx_byte;

static uint32_t frames_received = 0;
static uint32_t crc_errors = 0;
static uint32_t last_frame_time_us = 0;
static uint32_t last_interval_us = 0;

static uint8_t crc8(const uint8_t *data, uint8_t len)
{
    uint8_t crc = 0;
    for (uint8_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (uint8_t b = 0; b < 8; b++) {
            crc = (crc & 0x80) ? (uint8_t)((crc << 1) ^ 0x07) : (uint8_t)(crc << 1);
        }
    }
    return crc;
}

static void report_stats(void)
{
    char msg[80];
    int n = snprintf(msg, sizeof(msg),
                      "frames=%lu crc_errors=%lu last_interval_us=%lu\r\n",
                      (unsigned long)frames_received,
                      (unsigned long)crc_errors,
                      (unsigned long)last_interval_us);
    HAL_UART_Transmit(&huart3, (uint8_t *)msg, (uint16_t)n, 10);
}

void FrameReceiver_Start(void)
{
    state = WAIT_START;
    HAL_GPIO_WritePin(ENABLE_GPIO_Port, ENABLE_Pin, GPIO_PIN_RESET);
    HAL_UART_Receive_IT(&huart3, &rx_byte, 1);
}

void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
    if (huart->Instance != USART3) {
        return;
    }

    switch (state) {
        case WAIT_START:
            if (rx_byte == PACKET_START_BYTE) {
                state = WAIT_LEN;
            }
            break;

        case WAIT_LEN:
            if (rx_byte == 0 || rx_byte > MAX_PAYLOAD_BYTES) {
                state = WAIT_START;
            } else {
                payload_len = rx_byte;
                payload_pos = 0;
                state = READ_PAYLOAD;
            }
            break;

        case READ_PAYLOAD:
            payload[payload_pos++] = rx_byte;
            if (payload_pos >= payload_len) {
                state = WAIT_CRC;
            }
            break;

        case WAIT_CRC:
            if (rx_byte == crc8(payload, payload_len)) {
                uint32_t now = __HAL_TIM_GET_COUNTER(&htim2);
                last_interval_us = now - last_frame_time_us;
                last_frame_time_us = now;

                HAL_GPIO_WritePin(ENABLE_GPIO_Port, ENABLE_Pin, GPIO_PIN_SET);
                HAL_UART_Transmit(&huart2, payload, payload_len, 5);
                HAL_GPIO_WritePin(ENABLE_GPIO_Port, ENABLE_Pin, GPIO_PIN_RESET);

                BSP_LED_Toggle(LED_GREEN);

                frames_received++;
                if (frames_received % STATS_REPORT_EVERY == 0) {
                    report_stats();
                }
            } else {
                BSP_LED_Toggle(LED_RED);
                crc_errors++;
            }
            state = WAIT_START;
            break;
    }

    HAL_UART_Receive_IT(&huart3, &rx_byte, 1);
}

void HAL_UART_ErrorCallback(UART_HandleTypeDef *huart)
{
    if (huart->Instance != USART3) {
        return;
    }
    state = WAIT_START;
    HAL_UART_Receive_IT(&huart3, &rx_byte, 1);
}
