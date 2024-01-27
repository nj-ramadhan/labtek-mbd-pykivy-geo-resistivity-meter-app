

/** Software Configuration Header File **/
/** This header file contains software configurations for current microcontroller with existing system.
    Microcontroller: Arduino Nano (ATmega328P)
    Devices:
    - ACS712 Current Sensor - Analog Voltage Signal (ACS712)
    - ADS1115 I2C Analog to Digital Converter - Voltage Sensor - I2C Communication (ADS1115)
    ?  ADS1220 24-Bit ADC
    - Relay 4 Channel - Active Low ? High ? (RLY[X]) 1 ... 4
**/
/*=========================================================================*/
/** Including this header only once in a single compliation **/
#pragma once
/*=========================================================================*/
/** Including hardware_configuration header and required libraries**/
#include "Earth_Sensing_Arduino_hardware_configuration.h"
#include <ACS712.h> // ACS712 Library https://github.com/RobTillaart/ACS712
#include <Wire.h>
#include <MCP342x.h> // GY-MCP3424 Library https://github.com/battosai30/MCP3424
// RLY[X] Library ???
/*=========================================================================*/
/** Existing System Constants / Parameters **/

/*=========================================================================*/
/** Clock / Timing Parameters **/
#define SAMPLING_TIME 30 //miliseconds per sample
#define DELAY_TIME 3 //miliseconds
unsigned long current_time = 0;
unsigned long last_time = 0;
unsigned long difference_time = 0;
/*=========================================================================*/
/** Communication Parameters **/
#define BAUD_RATE 19200 // bits/s or ??? µs per byte
// 19200
// 57600 bits/s or 173.611 µs per byte or
// 9600 bits/s or 1.042 ms per byte --- https://www.wevolver.com/article/baud-rates-the-most-common-baud-rates
/*=========================================================================*/
/** Microcontroller to ACS712 **/
//  Arduino UNO has 5.0 volt with a max ADC value of 1023 steps
//  ACS712 5A  uses 185 mV per A
//  ACS712 20A uses 100 mV per A
//  ACS712 30A uses  66 mV per A
//  ACS758 Bidirectional 50A  uses 40 mV per A
//  ACS758 Unidirectional 50A  uses 60 mV per A
//  ACS758 Bidirectional 100A  uses 20 mV per A
//  ACS758 Unidirectional 100A  uses 40 mV per A
//  ACS758 Bidirectional 150A  uses 13,3 mV per A
//  ACS758 Unidirectional 150A  uses 26,7 mV per A
//  ACS758 Bidirectional 200A  uses 10 mV per A
//  ACS758 Unidirectional 200A  uses 20 mV per A
ACS712  ACS(PIN_ACS_OUT, 5.0, 1023, 185); //185 mV per A
int mili_ampere = 0;
#define DELAY_ACS 100 //miliseconds
/*=========================================================================*/
/** Microcontroller to MCP3424 **/
MCP342x MCP(0x68); // Declaration of MCP3424
long micro_volt = 0;
float mili_volt = 0;
/*=========================================================================*/
/** Microcontroller to RLY[X] **/
bool state_in[4] = {false, false, false, false};
/*=========================================================================*/
