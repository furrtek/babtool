// Dumps 25X04 serial flash chip
// furrtek 2019

#include <SPI.h>

#define PIN_CS 9

void setup() {
    pinMode(PIN_CS, OUTPUT);
    digitalWrite(PIN_CS, HIGH);
    Serial.begin(115200);
    SPI.begin();
    SPI.setDataMode(SPI_MODE0);
    delay(300);
}

void loop() {
    Serial.println("Device ID:");
    digitalWrite(PIN_CS, LOW);
    SPI.transfer(0x9F);     // Read JEDEC infos
    Serial.print(SPI.transfer(0xFF), HEX);
    Serial.print(SPI.transfer(0xFF), HEX);
    Serial.println(SPI.transfer(0xFF), HEX);
    digitalWrite(PIN_CS, HIGH);

    Serial.println("Enable logging and press any key to dump");
    while (!Serial.read()) {};

    digitalWrite(PIN_CS, LOW);
    SPI.transfer(0x03); // Read
    SPI.transfer(0x00); // Start address
    SPI.transfer(0x00);
    SPI.transfer(0x00);
    for (uint32_t c = 0; c < 524288UL; c++)
        Serial.write(SPI.transfer(0xFF));
    digitalWrite(PIN_CS, HIGH);
    delay(300);
}
