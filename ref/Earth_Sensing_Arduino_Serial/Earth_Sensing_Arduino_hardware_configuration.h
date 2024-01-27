/** Hardware Configuration Header File **/
/** This header file contains hardware configurations for current microcontroller mappings with existing system.
    Microcontroller: Arduino Nano (ATmega328P)
    Devices:
    - ACS712 Current Sensor - Analog Voltage Signal (ACS712)
    X ADS1115 I2C Analog to Digital Converter - Voltage Sensor - I2C Communication (ADS1115)
    - GY-MCP3424 Analog to Digital Converter - Voltage Sensor - I2C Communication (MCP3424)
    - Relay 4 Channel - Active Low ? High ? (RLY[X]) 1 ... 4
    Microcontroller Pin References: A000005-full-pinout.pdf
**/
/*=========================================================================*/
/** Including this header only once in a single compliation **/
#pragma once
/*=========================================================================*/
/** Microcontroller to ACS712 **/
//PIN_ACS_VCC
//PIN_ACS_GND
#define PIN_ACS_OUT 14 //A0
/*=========================================================================*/
/** Microcontroller to MCP3424 **/
//Pullup Resistor 1kOhm s.d. 10kOhm for SDA, SCL, GPIO, close to ADS1115
//PIN_MCP_VCC
//PIN_MCP_GND
#define PIN_MCP_SDA 18 //A4
#define PIN_MCP_SCL 19 //A5
//PIN_MCP_AD0
//PIN_MCP_AD1
//
//https://wiki.dfrobot.com/MCP3424_18-Bit_ADC-4_Channel_with_Programmable_Gain_Amplifier__SKU_DFR0316_

//PIN_MCP_CH2- --- Coupled with PIN_MCP_GND
//PIN_MCP_CH2+
//PIN_MCP_CH1- --- Coupled with PIN_MCP_GND
//PIN_MCP_CH1+
//PIN_MCP_CH3- --- Coupled with PIN_MCP_GND
//PIN_MCP_CH3+
//PIN_MCP_CH4- --- Coupled with PIN_MCP_GND
//PIN_MCP_CH4+
/*=========================================================================*/
/** Microcontroller to RLY[X] **/
//PIN_RLY_VCC
//PIN_RLY_GND
const int PIN_RLY_IN[4] = {4, 7, 8, 2};//IN1-D4, IN2-D7, IN3-D8, IN4-D2
/*=========================================================================*/
