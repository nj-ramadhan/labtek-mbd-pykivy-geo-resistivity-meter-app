/** Main Earth Sensing Program **/
#include "Earth_Sensing_Arduino_software_configuration.h"

void setup() {
  Serial.begin(BAUD_RATE);
  //  Serial.println(BAUD_RATE);
  pinMode(PIN_ACS_OUT, INPUT);
  //  Serial.println(PIN_ACS_OUT);
  //Initializing ACS
  ACS.autoMidPointDC(100);
  mili_ampere = 0;
  //  Serial.println(mili_ampere);
  //Initializing MCP
  MCP.begin(0);
  MCP.setConfiguration(CH2, RESOLUTION_18_BITS, CONTINUOUS_MODE, PGA_X1); // Channel 2, 18 bits resolution, continous mode, amplifier gain = 1
  micro_volt = 0;
  mili_volt = 0;
  //  Serial.println(mili_volt);
  //Initializing RLY[X]
  for (int i = 0; i < 4; i++) {
    pinMode(PIN_RLY_IN[i], OUTPUT);
    state_in[i] = false;
    digitalWrite(PIN_RLY_IN[i], state_in[i]);
    //    Serial.println(state_in[i]);
  }

  //  Serial.println("void setup() done.");
  delay(DELAY_TIME);
  last_time = millis();

}

void sent_serial(float readings) {
  float sent_readings = readings;
  Serial.println(sent_readings); // sends a \n with text
  Serial.flush();

}

void read_voltage() {
  MCP.newConversion();
  micro_volt = MCP.measure();
  mili_volt = float(float(micro_volt) / 1000000.0);
  //  Serial.print("Voltage = ");
  //  Serial.print(mili_volt);
  //  Serial.println(" miliVolt");
  //  Serial.flush();

}

void read_current() {
  mili_ampere = ACS.mA_DC(100);
  //  Serial.print("Current = ");
  //  Serial.print(mili_ampere);
  //  Serial.println(" miliAmpere");
  //  Serial.flush();
}

void not_inject_current() {
  digitalWrite(PIN_RLY_IN[0], LOW); //IN1-D4
  digitalWrite(PIN_RLY_IN[1], LOW); //IN2-D7
  digitalWrite(PIN_RLY_IN[2], LOW); //IN3-D8
  digitalWrite(PIN_RLY_IN[3], LOW); //IN4-D2
}

void inject_positive_current() {
  digitalWrite(PIN_RLY_IN[1], LOW); //IN2-D7
  delay(DELAY_TIME);
  digitalWrite(PIN_RLY_IN[0], LOW); //IN1-D4
  digitalWrite(PIN_RLY_IN[2], LOW); //IN3-D8
  digitalWrite(PIN_RLY_IN[3], LOW); //IN4-D2
  delay(DELAY_TIME);
  digitalWrite(PIN_RLY_IN[1], HIGH); //IN2-D7
}

void inject_negative_current() {
  digitalWrite(PIN_RLY_IN[1], LOW); //IN2-D7
  delay(DELAY_TIME);
  digitalWrite(PIN_RLY_IN[0], HIGH); //IN1-D4
  digitalWrite(PIN_RLY_IN[2], HIGH); //IN3-D8
  digitalWrite(PIN_RLY_IN[3], LOW); //IN4-D2
  delay(DELAY_TIME);
  digitalWrite(PIN_RLY_IN[1], HIGH); //IN2-D7
}

void loop() {
  char RxedByte = 0;
  read_current();
  read_voltage();
  if (Serial.available())
  {

    RxedByte = Serial.read();

    switch (RxedByte)
    {
      case 'A':
        sent_serial(mili_ampere);
        break;

      case 'B':
        sent_serial(mili_volt);
        break;

      case 'C':
        not_inject_current();
        break;

      case 'D':
        inject_positive_current();
        break;

      case 'E':
        inject_negative_current();
        break;

      default:
        break;
    }
  }
}
