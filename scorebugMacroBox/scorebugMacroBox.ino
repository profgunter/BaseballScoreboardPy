#include "Keyboard.h"

/*
 * Pin Constants
 */
const int buttonPins[] = {4, 5, 6, 7, 8, 9, 19, 18, 15, 14, 16, 10};
const int numKeys = sizeof(buttonPins) / sizeof(buttonPins[0]); // Calculate the number of keys

/*
 * Button Keys
 */
const int keyMapping[] = {'p', 'c', 'b', 'k', 'o', 'r', KEY_KP_1, KEY_KP_2, KEY_KP_3, 'h', 's', 'e'};

/*
 * Keystate Tracking
 */
bool keyStates[numKeys]={false};

/*
 * Debounce Time
 */
const unsigned long debounceDelay = 50;
unsigned long debounceTimes[numKeys] = {0};

 void setup(){
  pinMode(1, INPUT_PULLUP); //check ground pin1
  if(!digitalRead(1)){
    for(;;){} //do nothing; require reset
  }

  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
  TXLED0;

  for (int i = 0; i < numKeys; i++) {
    pinMode(buttonPins[i], INPUT_PULLUP); // Set all switch pins as inputs with internal pull-up resistors
  }
  Keyboard.begin(); // Initialize the keyboard
}

void loop() {
  for (int i = 0; i < numKeys; i++) {
    unsigned long currentTime = millis(); // Get the current time
    
    // Check if the switch is pressed and debounce time has passed
    if (digitalRead(buttonPins[i]) == LOW && (currentTime - debounceTimes[i] >= debounceDelay)) {
      if (!keyStates[i]) { // If the key was not already pressed
        keyStates[i] = true; // Set the key as pressed
        Keyboard.press(keyMapping[i]); // Simulate pressing the defined key
      }
      debounceTimes[i] = currentTime; // Reset the debounce timer
    } else if (digitalRead(buttonPins[i]) == HIGH && keyStates[i]) {
      keyStates[i] = false; // Set the key as released
      Keyboard.release(keyMapping[i]); // Simulate releasing the defined key
    }
  }
}
