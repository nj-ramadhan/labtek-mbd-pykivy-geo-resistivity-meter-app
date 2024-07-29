#include "UT61E.h"
#include "74HC154.h"

#define PIN_DTR1 30
UT61E ut61e1 = UT61E(&Serial2, PIN_DTR1);

#define PIN_DTR2 28
UT61E ut61e2 = UT61E(&Serial1, PIN_DTR2);

//set relay pin
int Relay_Reset = 21;
int Pin_Up_Voltage_Inject = 41;
int Pin_Reset_Inject = 53;
int Pin_Inject_AB = 43;
int Pin_Inject_BA = 51;
//int Relay_pembalik = 26;

//System Variable
char Data_komunikasi[13];
char Data_komunikasi2[12];
char Data_komunikasi3[12];
char Data_komunikasi4[12];
char Data_komunikasi5[12];
char perintah_minta_data[12];
char perintah_minta_data2[12];
long Perintah_Kanal1;
long Perintah_Kanal2;
long Perintah_Kanal3;
long Perintah_Kanal4;
int steper_perintah = 0;
char jalur_komunikasi;
char* delim = ',';
int i, j, x, y, w = 0;
int penerimaan_berhenti = 0;
int baca_ok = 0;
int skip = 0;
int stop_baca = 0;
//unsigned long time;
int error1, error2;
float volt, volt_kirim3;
float ampere, ampere_kirim3;
byte type, type1;
int indikator_voltage_maksimal = 0;
unsigned long detik_pembacaaan, start_detik_pembacaan = 0;
String volt_kirim, volt_kirim2, ampere_kirim, ampere_kirim2;

//Spesial Set
int debug_mode = 0;
int one_time_report = 0;
float treshold_minimum_voltage = 10.00;
float treshold_maximum_voltage = 100.00;
float treshold_voltage = 20.00;
int step_voltage = 1;
int activate = 0;
int indicator_positif = 0;
int indicator_negatif = 0;
int for_test_batch = 1;
int indicator_voltase_cukup = 0;
int Stop_the_patok_a = 0;
int Stop_the_patok_b = 0;
int posisi_plus = 0;
int posisi_mines = 0;

DEV_74HC154 selector1(2, 4, 6, 8);
int Selector_E11 = 10;
int Selector_E12 = 12;
int Selector_E13 = 14;
uint8_t line1 = 0;

DEV_74HC154 selector2(15, 13, 11, 9);
int Selector_E21 = 7;
int Selector_E22 = 5;
int Selector_E23 = 3;
uint8_t line2 = 0;

DEV_74HC154 selector3(52, 50, 48, 47);
int Selector_E31 = 46;
int Selector_E32 = 44;
int Selector_E33 = 42;
uint8_t line3 = 0;

DEV_74HC154 selector4(40, 38, 36, 34);
int Selector_E41 = 39;
int Selector_E42 = 37;
int Selector_E43 = 35;
uint8_t line4 = 0;

void setup() {
  Serial.begin(9600);
  //startMillis = millis();
  selector1.enable();
  selector2.enable();
  selector3.enable();
  selector4.enable();

  pinMode(Selector_E11, OUTPUT);
  pinMode(Selector_E12, OUTPUT);
  pinMode(Selector_E13, OUTPUT);
  pinMode(Selector_E21, OUTPUT);
  pinMode(Selector_E22, OUTPUT);
  pinMode(Selector_E23, OUTPUT);
  pinMode(Selector_E31, OUTPUT);
  pinMode(Selector_E32, OUTPUT);
  pinMode(Selector_E33, OUTPUT);
  pinMode(Selector_E41, OUTPUT);
  pinMode(Selector_E42, OUTPUT);
  pinMode(Selector_E43, OUTPUT);

  pinMode(Relay_Reset, OUTPUT);
  pinMode(Pin_Up_Voltage_Inject, OUTPUT);
  pinMode(Pin_Reset_Inject, OUTPUT);
  pinMode(Pin_Inject_AB, OUTPUT);
  pinMode(Pin_Inject_BA, OUTPUT);

  digitalWrite(Selector_E11, HIGH);
  digitalWrite(Selector_E12, HIGH);
  digitalWrite(Selector_E13, HIGH);
  digitalWrite(Selector_E21, HIGH);
  digitalWrite(Selector_E22, HIGH);
  digitalWrite(Selector_E23, HIGH);
  digitalWrite(Selector_E31, HIGH);
  digitalWrite(Selector_E32, HIGH);
  digitalWrite(Selector_E33, HIGH);
  digitalWrite(Selector_E41, HIGH);
  digitalWrite(Selector_E42, HIGH);
  digitalWrite(Selector_E43, HIGH);

  digitalWrite(Pin_Up_Voltage_Inject, LOW);
  digitalWrite(Pin_Reset_Inject, LOW);
  digitalWrite(Pin_Inject_AB, HIGH);
  digitalWrite(Pin_Inject_BA, LOW);
  digitalWrite(Relay_Reset, LOW);
  digitalWrite(Pin_Inject_BA, LOW);
  digitalWrite(Pin_Inject_AB, LOW);

  digitalWrite(Pin_Reset_Inject, HIGH);
  delay(1500);
  digitalWrite(Pin_Reset_Inject, LOW);
  delay(500);
  digitalWrite(Pin_Reset_Inject, HIGH);
  delay(1500);
  digitalWrite(Pin_Reset_Inject, LOW);

  Data_komunikasi[0] = '*';
  Data_komunikasi[1] = 'N';
  Data_komunikasi[2] = 'N';
  Data_komunikasi[3] = 'N';
  Data_komunikasi[4] = 'N';
  Data_komunikasi[5] = 'N';
  Data_komunikasi[6] = 'N';
  Data_komunikasi[7] = 'N';
  Data_komunikasi[8] = 'N';
  Data_komunikasi[9] = 'N';
  Data_komunikasi[10] = 'N';
  Data_komunikasi[11] = 'N';
  Data_komunikasi[12] = 'N';
  Data_komunikasi[13] = 'N';
}

void loop() {
  Komunikasi();
  Get_Data_Multimeter();

  if (volt <= treshold_voltage && step_voltage < 4 && activate == 1)
  {
    indicator_voltase_cukup = 0;
    digitalWrite(Pin_Inject_AB, LOW);
    digitalWrite(Pin_Inject_BA, LOW);


    delay(200);
    digitalWrite(Pin_Up_Voltage_Inject, HIGH);
    delay(500);
    digitalWrite(Pin_Up_Voltage_Inject, LOW);

    step_voltage++;


    if (indicator_positif == 1 && indicator_negatif == 0)
    {
      digitalWrite(Pin_Inject_BA, LOW);
      digitalWrite(Pin_Inject_AB, HIGH);
    }

    else if (indicator_positif == 0 && indicator_negatif == 1)
    {
      digitalWrite(Pin_Inject_BA, HIGH);
      digitalWrite(Pin_Inject_AB, LOW);
    }


  }
  else if (step_voltage >= 4)
  {
    indicator_voltase_cukup = 1;
    //Serial.print("indicator_voltase = ");Serial.print(indicator_voltase_cukup);
    if (debug_mode == 1)
    {
      Serial.println("voltase inject pada posisi maksimal");
    }
  }
  else if (volt > treshold_voltage)
  {
    indicator_voltase_cukup = 1;
    digitalWrite(Pin_Inject_BA, LOW);
    digitalWrite(Pin_Inject_AB, LOW);
  }

  if (debug_mode == 1)
  {
    Serial.print("Step inject voltage saat ini ="); Serial.println(step_voltage);
    Serial.print("Threshold inject voltage saat ini = "); Serial.println(treshold_voltage);
  }
  if (indicator_voltase_cukup == 1)
  {
    Serial.println("Lanjut");
  }
  //Serial.print("indicator_voltase = ");Serial.print(indicator_voltase_cukup);
}

int Komunikasi() {
  //Serial.println(Serial.available());
  while (Serial.available()) {
    // Read the incoming data and print it to the serial monitor
    char jalur_komunikasi = Serial.read();
    Data_komunikasi[i] = jalur_komunikasi;
    Data_komunikasi2[i] = jalur_komunikasi;
    Data_komunikasi3[i] = jalur_komunikasi;
    Data_komunikasi4[i] = jalur_komunikasi;
    Data_komunikasi5[i] = jalur_komunikasi;
    i++;
    if (Data_komunikasi[0] == '*')
    {
      one_time_report = 1;

    }
    w++;
  }
  if (Serial.available() == 0 && w > i)
  {
    w = 0;
    Data_komunikasi[0] = 'N';
    Data_komunikasi[1] = 'N';
    Data_komunikasi[2] = 'N';
    Data_komunikasi[3] = 'N';
    Data_komunikasi[4] = 'N';
    Data_komunikasi[5] = 'N';
    Data_komunikasi[6] = 'N';
    Data_komunikasi[7] = 'N';
    Data_komunikasi[8] = 'N';
    Data_komunikasi[9] = 'N';
    Data_komunikasi[10] = 'N';
    Data_komunikasi[11] = 'N';
    Data_komunikasi[12] = 'N';
    Data_komunikasi[13] = 'N';


  }
  if (Data_komunikasi5[0] == '!')
  {
    perintah_minta_data2[0] = Data_komunikasi5[1];
  }
  if (perintah_minta_data2[0] == '+')
  {
    start_detik_pembacaan = millis();
    if (treshold_voltage < treshold_maximum_voltage)
    {
      treshold_voltage = treshold_voltage + 5.00;
      Serial.print("(+5) set threshold inject = "); Serial.println(treshold_voltage);
    }
    else
    {
      Serial.print("Threshold inject Maximum = "); Serial.println(treshold_voltage);
    }
  }
  if (perintah_minta_data2[0] == '-' && treshold_voltage >= 10.00)
  {
    start_detik_pembacaan = millis();
    if (treshold_voltage > treshold_maximum_voltage)
    {
      treshold_voltage = treshold_voltage - 5.00;
      Serial.print("(-5) set threshold inject = "); Serial.println(treshold_voltage);
    }
    else
    {
      Serial.print("Threshold inject Minimum = "); Serial.println(treshold_voltage);
    }
  }
  if (perintah_minta_data2[0] == '_')
  {
    Serial.print("threshold inject = "); Serial.println(treshold_voltage);
  }
  if (Data_komunikasi2[0] == 'v' && indicator_voltase_cukup == 1)
  {
    volt_kirim = String(volt_kirim3);
    volt_kirim2 = "v" + volt_kirim;

    Stop_the_patok_a = 0;

    Serial.println(volt_kirim2);
    //Serial.print(" | "); Serial.println(detik_pembacaaan);
  }
  else if (Data_komunikasi2[0] == 'a' && indicator_voltase_cukup == 1)
  {
    ampere_kirim = String(ampere_kirim3);
    ampere_kirim2 = "a" + ampere_kirim;
    Stop_the_patok_b = 0;
    Serial.println(ampere_kirim2);
    //Serial.println(ampere_kirim2);
    //Serial.print(" | "); Serial.println(detik_pembacaaan);
  }
  if (Data_komunikasi3[0] == '%')
  {
    digitalWrite(Selector_E11, HIGH);
    digitalWrite(Selector_E12, HIGH);
    digitalWrite(Selector_E13, HIGH);
    digitalWrite(Selector_E21, HIGH);
    digitalWrite(Selector_E22, HIGH);
    digitalWrite(Selector_E23, HIGH);
    digitalWrite(Selector_E31, HIGH);
    digitalWrite(Selector_E32, HIGH);
    digitalWrite(Selector_E33, HIGH);
    digitalWrite(Selector_E41, HIGH);
    digitalWrite(Selector_E42, HIGH);
    digitalWrite(Selector_E43, HIGH);
    Serial.println("Semua decoder mati");
  }

  if (Data_komunikasi4[0] == '+') {
    start_detik_pembacaan = millis();
    Serial.println("Inject positif");
    //delay(200);
    activate = 1;
    digitalWrite(Relay_Reset, LOW);
    digitalWrite(Pin_Inject_AB, HIGH);
    digitalWrite(Pin_Inject_BA, LOW);
    indicator_positif = 1;
    indicator_negatif = 0;

    Stop_the_patok_a = 0;
    Stop_the_patok_b = 0;
    posisi_plus = 1;

    //delay(1000);
  }
  if (Data_komunikasi4[0] == '-') {
    start_detik_pembacaan = millis();
    Serial.println("Inject Negatif");
    //delay(200);
    activate = 1;
    digitalWrite(Relay_Reset, LOW);
    digitalWrite(Pin_Inject_AB, LOW);
    digitalWrite(Pin_Inject_BA, HIGH);
    indicator_positif = 0;
    indicator_negatif = 1;
    posisi_mines = 1;

    Stop_the_patok_a = 0;
    Stop_the_patok_b = 0;
  }
  if (Data_komunikasi4[0] == '_') {
    //indicator_voltase_cukup = 0;
    Serial.println("Not Injected");
    activate = 0;
    digitalWrite(Relay_Reset, HIGH);
    digitalWrite(Pin_Inject_BA, LOW);
    digitalWrite(Pin_Inject_AB, LOW);
    indicator_positif = 0;
    indicator_negatif = 0;

  }
  if (Data_komunikasi4[0] == '/') {

    Serial.println("Reset Inject Voltage");
    indicator_voltase_cukup = 0;
    digitalWrite(Pin_Inject_BA, LOW);
    digitalWrite(Pin_Inject_AB, LOW);
    delay(200);

    digitalWrite(Pin_Reset_Inject, HIGH);
    delay(500);
    digitalWrite(Pin_Reset_Inject, LOW);
    //delay(1000);
    step_voltage = 1;

    if (indicator_positif == 1 && indicator_negatif == 0)
    {
      digitalWrite(Pin_Inject_BA, LOW);
      digitalWrite(Pin_Inject_AB, HIGH);
    }

    else if (indicator_positif == 0 && indicator_negatif == 1)
    {

      digitalWrite(Pin_Inject_BA, HIGH);
      digitalWrite(Pin_Inject_AB, LOW);
    }
  }


  for (j = 0; j <= 12 ; j++)
  {
    skip = 0;
    if (j == 0 && Data_komunikasi[j] == '*') {
      baca_ok = 1;
      j++;
      one_time_report = 1;
    }
    if (baca_ok == 1) {
      int temp_data;
      if (Data_komunikasi[j] == '0') {
        temp_data = 0;
        x++;
      }
      else if (Data_komunikasi[j] == '1') {
        temp_data = 1;
        x++;
      }
      else if (Data_komunikasi[j] == '2') {
        temp_data = 2;
        x++;
      }
      else if (Data_komunikasi[j] == '3') {
        temp_data = 3;
        x++;
      }
      else if (Data_komunikasi[j] == '4') {
        temp_data = 4;
        x++;
      }
      else if (Data_komunikasi[j] == '5') {
        temp_data = 5;
        x++;
      }
      else if (Data_komunikasi[j] == '6') {
        temp_data = 6;
        x++;
      }
      else if (Data_komunikasi[j] == '7') {
        temp_data = 7;
        x++;
      }
      else if (Data_komunikasi[j] == '8') {
        temp_data = 8;
        x++;
      }
      else if (Data_komunikasi[j] == '9') {
        temp_data = 9;
        x++;
      }
      else if (Data_komunikasi[j] == ',') {
        skip = 1;
        x++;

        if (debug_mode == 1)
        {
          Serial.print("posisi x = "); Serial.println(x);
        }

        if (x == 2 || x == 5 || x == 8 || x == 11)
        {
          x++;
        }

      }
      if (x == 1) {
        Perintah_Kanal1 = temp_data;
      }
      else if (x == 2) {
        Perintah_Kanal1 = (Perintah_Kanal1 * 10) + temp_data;
      }
      else if (x == 4) {
        Perintah_Kanal2 = temp_data;
      }
      else if (x == 5 ) {
        Perintah_Kanal2 = (Perintah_Kanal2 * 10) + temp_data;

      }
      else if (x == 7) {
        Perintah_Kanal3 = temp_data;
      }
      else if (x == 8 ) {
        Perintah_Kanal3 = (Perintah_Kanal3 * 10) + temp_data;

      }
      else if (x == 10) {
        Perintah_Kanal4 = temp_data;
      }
      else if (x == 11 && stop_baca == 0) {
        Perintah_Kanal4 = (Perintah_Kanal4 * 10) + temp_data;
        stop_baca = 1;
      }
    }
  }
  i = 0;
  x = 0;
  //w++;
  stop_baca = 0;

  if (debug_mode == 1 || one_time_report == 1)
  {
    if (Perintah_Kanal1 >= 0 && Perintah_Kanal1 < 16)
    {
      line1 = Perintah_Kanal1;
      digitalWrite(Selector_E11, LOW );
      digitalWrite(Selector_E12, HIGH );
      digitalWrite(Selector_E13, HIGH );
    }

    else if (Perintah_Kanal1 >= 16 && Perintah_Kanal1 < 32)
    {
      line1 = Perintah_Kanal1 - 16;
      digitalWrite(Selector_E11, HIGH );
      digitalWrite(Selector_E12, LOW );
      digitalWrite(Selector_E13, HIGH );
    }

    else if (Perintah_Kanal1 >= 32 && Perintah_Kanal1 < 48)
    {
      line1 = Perintah_Kanal1 - 32;
      digitalWrite(Selector_E11, HIGH );
      digitalWrite(Selector_E12, HIGH );
      digitalWrite(Selector_E13, LOW );
    }

    if (Perintah_Kanal2 >= 0 && Perintah_Kanal2 < 16)
    {
      line2 = Perintah_Kanal2;
      digitalWrite(Selector_E21, LOW );
      digitalWrite(Selector_E22, HIGH );
      digitalWrite(Selector_E23, HIGH );
    }

    else if (Perintah_Kanal2 >= 16 && Perintah_Kanal2 < 32)
    {
      line2 = Perintah_Kanal2 - 16;
      digitalWrite(Selector_E21, HIGH );
      digitalWrite(Selector_E22, LOW );
      digitalWrite(Selector_E23, HIGH );
    }

    else if (Perintah_Kanal2 >= 32 && Perintah_Kanal2 < 48)
    {
      line2 = Perintah_Kanal2 - 32;
      digitalWrite(Selector_E21, HIGH );
      digitalWrite(Selector_E22, HIGH );
      digitalWrite(Selector_E23, LOW );
    }

    if (Perintah_Kanal3 >= 0 && Perintah_Kanal3 < 16)
    {
      line3 = Perintah_Kanal3;
      digitalWrite(Selector_E31, LOW );
      digitalWrite(Selector_E32, HIGH );
      digitalWrite(Selector_E33, HIGH );
    }

    else if (Perintah_Kanal3 >= 16 && Perintah_Kanal3 < 32)
    {
      line3 = Perintah_Kanal3 - 16;
      digitalWrite(Selector_E31, HIGH );
      digitalWrite(Selector_E32, LOW );
      digitalWrite(Selector_E33, HIGH );
    }

    else if (Perintah_Kanal3 >= 32 && Perintah_Kanal3 < 48)
    {
      line3 = Perintah_Kanal3 - 32;
      digitalWrite(Selector_E31, HIGH );
      digitalWrite(Selector_E32, HIGH );
      digitalWrite(Selector_E33, LOW );
    }

    if (Perintah_Kanal4 >= 0 && Perintah_Kanal4 < 16)
    {
      line4 = Perintah_Kanal4;
      digitalWrite(Selector_E41, LOW );
      digitalWrite(Selector_E42, HIGH );
      digitalWrite(Selector_E43, HIGH );
    }

    else if (Perintah_Kanal4 >= 16 && Perintah_Kanal4 < 32)
    {
      line4 = Perintah_Kanal4 - 16;
      digitalWrite(Selector_E41, HIGH );
      digitalWrite(Selector_E42, LOW );
      digitalWrite(Selector_E43, HIGH );
    }

    else if (Perintah_Kanal4 >= 32 && Perintah_Kanal4 < 48)
    {
      line4 = Perintah_Kanal4 - 32;
      digitalWrite(Selector_E41, HIGH );
      digitalWrite(Selector_E42, HIGH );
      digitalWrite(Selector_E43, LOW );
    }
    Serial.println("Good");
    indicator_voltase_cukup = 0;
    digitalWrite(Pin_Inject_BA, LOW);
    digitalWrite(Pin_Inject_AB, LOW);
    delay(200);
    digitalWrite(Pin_Reset_Inject, HIGH);
    delay(500);
    digitalWrite(Pin_Reset_Inject, LOW);
    //delay(1000);
    step_voltage = 1;
    /*Serial.print("Data yang diantarkan = "); Serial.println(Data_komunikasi);
      Serial.print("Nomor Relay yang diapply = ");
      Serial.print(Perintah_Kanal1);
      Serial.print(", "); Serial.print(Perintah_Kanal2);
      Serial.print(", "); Serial.print(Perintah_Kanal3);
      Serial.print(", "); Serial.println(Perintah_Kanal4);*/
    //digitalWrite(Relay_Reset, HIGH);
    one_time_report = 0;
    //delay(500);
    selector1.setLine(line1);
    selector2.setLine(line2);
    selector3.setLine(line3);
    selector4.setLine(line4);
    //digitalWrite(Relay_Reset, LOW);

    //delay(500);

    Data_komunikasi[0] = 'N';
    /*Data_komunikasi[1] = 'N';
      Data_komunikasi[2] = 'N';
      Data_komunikasi[3] = 'N';
      Data_komunikasi[4] = 'N';
      Data_komunikasi[5] = 'N';
      Data_komunikasi[6] = 'N';
      Data_komunikasi[7] = 'N';
      Data_komunikasi[8] = 'N';
      Data_komunikasi[9] = 'N';
      Data_komunikasi[10] = 'N';
      Data_komunikasi[11] = 'N';
      Data_komunikasi[12] = 'N';
      Data_komunikasi[13] = 'N';
    */
    if (debug_mode == 1)
    {
      Serial.print("Selektor yang hidup = ");
      Serial.print(selector1.getLine()); Serial.print(",");
      Serial.print(selector2.getLine()); Serial.print(",");
      Serial.print(selector3.getLine()); Serial.print(",");
      Serial.println(selector4.getLine());
    }
  }



  Data_komunikasi4[0] = 'N';
  Data_komunikasi2[1] = 'N';
  Data_komunikasi2[0] = 'N';
  Data_komunikasi3[0] = 'N';
  Data_komunikasi5[0] = 'N';
  perintah_minta_data[0] = 'N';
  perintah_minta_data2[0] = 'N';
}


int Get_Data_Multimeter() {

  error1 = ut61e1.measureMillivolts(type);
  error2 = ut61e2.measureMilliamps(type1);
  ampere = ut61e2.getMilliAmps();
  volt = ut61e1.getMillivolts();
  detik_pembacaaan = millis() - start_detik_pembacaan;
  //stop the patok
  if (indicator_voltase_cukup)
  {
    if (posisi_plus == 1)
    {
      digitalWrite(Pin_Inject_BA, LOW);
      digitalWrite(Pin_Inject_AB, LOW);
      posisi_plus = 0;
      ampere_kirim = ampere;
      volt_kirim = volt;
    }
    if (posisi_mines == 1)
    {
      digitalWrite(Pin_Inject_BA, LOW);
      digitalWrite(Pin_Inject_AB, LOW);
      posisi_mines = 0;
      ampere_kirim3 = ampere;
      volt_kirim3 = volt;
    }
  }




  //volt = 14;
  //ampere = 1;


  if (debug_mode == 1)
  {
    Serial.print("Volt Terbaca: " );
    Serial.println(volt);
    Serial.print("Ampere Terbaca: " );
    Serial.println(ampere);
  }

  if (volt > 220000000 || ampere > 220000000 ) {
    if (debug_mode == 1)
    {
      Serial.println("OL.");
    }
  }
}
