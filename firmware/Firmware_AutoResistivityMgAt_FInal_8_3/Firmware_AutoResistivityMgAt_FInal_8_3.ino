#include "UT61E.h"

#define PIN_DTR1 30
UT61E ut61e1 = UT61E(&Serial2, PIN_DTR1);

#define PIN_DTR2 28
UT61E ut61e2 = UT61E(&Serial1, PIN_DTR2);

//System Variable
char Data_komunikasi[13];
char Data_komunikasi2[12];
char Data_komunikasi3[12];
char Data_komunikasi4[12];
char Data_komunikasi5[12];
char perintah_minta_data[12];
char perintah_minta_data2[12];
// long Perintah_Kanal1;
// long Perintah_Kanal2;
// long Perintah_Kanal3;
// long Perintah_Kanal4;
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

// #define Vread A0
#define Relay110 34
#define Relay172 36
#define Relay200 38
#define Relay220 40
#define Relay380 42
#define RelayNeutral 44
#define RelayPositif 46
#define RelayNegatif 47
#define Pin_pengaman 15

bool NeutralKecil = 1;
bool NeutralBesar = 0;

double AVGTegangan = 0;
double TotalTegangan = 0;
double Tegangan = 0;
int ADCinput = 0;
int Threshold = 25;
int LevelTegangan = 1;
int LamaInject = 100;
int BanyakSampling = 10;
int IntervalSampling = 20;


void setup() {
  //setup Hammam
  Serial.begin(9600);
  pinMode(Relay110, OUTPUT);
  pinMode(Relay172, OUTPUT);
  pinMode(Relay200, OUTPUT);
  pinMode(Relay220, OUTPUT);
  pinMode(Relay380, OUTPUT);
  pinMode(RelayPositif, OUTPUT);
  pinMode(RelayNegatif, OUTPUT);
  pinMode(RelayNeutral, OUTPUT);
  pinMode(Pin_pengaman, OUTPUT);

  digitalWrite(RelayNegatif, HIGH);
  digitalWrite(RelayPositif, HIGH);
  digitalWrite(RelayNeutral, HIGH);
  digitalWrite(Relay110, HIGH);
  digitalWrite(Relay172, HIGH);
  digitalWrite(Relay200, HIGH);
  digitalWrite(Relay220, HIGH);
  digitalWrite(Relay380, HIGH);
  digitalWrite(Pin_pengaman, HIGH);
}

void loop() {
  Get_Data_Multimeter();

  while (Serial.available() > 0) { 
    char serial = Serial.read();

    if (serial == '+') {
      digitalWrite(Pin_pengaman, LOW);
      digitalWrite(RelayNegatif, HIGH);
      digitalWrite(RelayPositif, LOW);
      LevelTegangan = 1;
      Serial.println("Inject Positif");
      delay(10);
    }

    else if (serial == '-') {
      digitalWrite(Pin_pengaman, LOW);
      digitalWrite(RelayNegatif, LOW);
      digitalWrite(RelayPositif, HIGH);
      Serial.println("Inject Negatif");
      LevelTegangan = 1;
      delay(10);
    }

    else if (serial == '.') {
      digitalWrite(RelayNegatif, LOW);
      digitalWrite(RelayPositif, HIGH);
      digitalWrite(Pin_pengaman, HIGH);
      Serial.println("Not Injected");
      LevelTegangan = 1;
      delay(10);
    }

    else if (serial == 'v') {
      volt_kirim = String(volt);
      volt_kirim2 = "v" + volt_kirim;
      Stop_the_patok_a = 0;

      Serial.println(volt_kirim2);
    } 
    
    else if (serial == 'a') {
      ampere_kirim = String(ampere);
      ampere_kirim2 = "a" + ampere_kirim;
      Stop_the_patok_b = 0;

      Serial.println(ampere_kirim2);
    }
  }
  
  //Fix
  if (LevelTegangan == 1) {
    digitalWrite(Relay110, LOW);
    digitalWrite(Relay172, HIGH);
    digitalWrite(Relay200, HIGH);
    digitalWrite(Relay220, HIGH);
    digitalWrite(Relay380, HIGH);
    LevelTegangan = 2;
    digitalWrite(RelayNeutral, NeutralKecil);
  }

  else if (volt <= Threshold && LevelTegangan == 2) {
    digitalWrite(Relay110, HIGH);
    digitalWrite(Relay172, LOW);
    digitalWrite(Relay200, HIGH);
    digitalWrite(Relay220, HIGH);
    digitalWrite(Relay380, HIGH);
    LevelTegangan = 3;
    digitalWrite(RelayNeutral, NeutralKecil);
  }

  else if (volt <= Threshold && LevelTegangan == 3) {
    digitalWrite(Relay110, HIGH);
    digitalWrite(Relay172, HIGH);
    digitalWrite(Relay200, LOW);
    digitalWrite(Relay220, HIGH);
    digitalWrite(Relay380, HIGH);
    LevelTegangan = 4;
    digitalWrite(RelayNeutral, NeutralKecil);
  }

  else if (volt <= Threshold && LevelTegangan == 4) {
    digitalWrite(Relay110, HIGH);
    digitalWrite(Relay172, HIGH);
    digitalWrite(Relay200, HIGH);
    digitalWrite(Relay220, LOW);
    digitalWrite(Relay380, HIGH);
    LevelTegangan = 5;
    digitalWrite(RelayNeutral, NeutralBesar);
  }

  else if (volt <= Threshold && LevelTegangan == 5) {
    digitalWrite(Relay110, HIGH);
    digitalWrite(Relay172, HIGH);
    digitalWrite(Relay200, HIGH);
    digitalWrite(Relay220, HIGH);
    digitalWrite(Relay380, LOW);
    digitalWrite(RelayNeutral, NeutralBesar);
  }

  else if (volt >= Threshold)
  {
    digitalWrite(Pin_pengaman, HIGH);
    Serial.println("OK");
  }
}

void Get_Data_Multimeter() {
  error1 = ut61e1.measureMillivolts(type);
  error2 = ut61e2.measureMilliamps(type1);
  ampere = ut61e2.getMilliAmps();
  volt = ut61e1.getMillivolts();
  detik_pembacaaan = millis() - start_detik_pembacaan;
  //stop the patok
  if (indicator_voltase_cukup) {
    if (posisi_plus == 1) {
      posisi_plus = 0;
      ampere_kirim = ampere;
      volt_kirim = volt;
    }
    if (posisi_mines == 1) {
      posisi_mines = 0;
      ampere_kirim3 = ampere;
      volt_kirim3 = volt;
    }
  }

  if (debug_mode == 1) {
    Serial.print("Volt Terbaca: ");
    Serial.println(volt);
    Serial.print("Ampere Terbaca: ");
    Serial.println(ampere);
  }

  if (volt > 220000000 || ampere > 220000000) {
    if (debug_mode == 1) {
      Serial.println("OL.");
    }
  }
}
