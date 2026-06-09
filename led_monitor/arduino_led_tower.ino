// Define the GPIO pins for the RGB channels
const int redPin = 5;
const int greenPin = 6;
const int bluePin = 4;

void setup() {
  // Initialize serial communication at 9600 baud
  Serial.begin(9600);
  
  // Set the LED pins as outputs
  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);
  
  // Ensure all LEDs start in the OFF state
  digitalWrite(redPin, LOW);
  digitalWrite(greenPin, LOW);
  digitalWrite(bluePin, LOW);

  // Print instructions to the Serial Monitor
  Serial.println("--- RGB LED Controller Ready ---");
  Serial.println("Send commands in the format: <Color><State>");
  Serial.println("Colors: R (Red), G (Green), B (Blue)");
  Serial.println("States: 1 (ON), 0 (OFF)");
  Serial.println("Example: 'R1' turns Red ON, 'G0' turns Green OFF.");
  Serial.println("--------------------------------");
}

void loop() {
  // Check if there is incoming serial data
  if (Serial.available() > 0) {
    
    // Read the incoming string until a newline character
    String command = Serial.readStringUntil('\n');
    
    // Remove any trailing whitespace, carriage returns, or line feeds
    command.trim(); 

    // Make sure the command is at least 2 characters long (e.g., "R1")
    if (command.length() >= 2) {
      
      // Extract the color (first character) and make it uppercase
      char color = toupper(command[0]);
      
      // Extract the state (second character)
      char state = command[1];
      
      // Determine if we should write HIGH or LOW
      int pinState = (state == '1') ? HIGH : LOW;

      // Apply the state to the correct pin
      switch (color) {
        case 'R':
          digitalWrite(redPin, pinState);
          Serial.print("Red channel set to ");
          Serial.println(pinState == HIGH ? "ON" : "OFF");
          break;
          
        case 'G':
          digitalWrite(greenPin, pinState);
          Serial.print("Green channel set to ");
          Serial.println(pinState == HIGH ? "ON" : "OFF");
          break;
          
        case 'B':
          digitalWrite(bluePin, pinState);
          Serial.print("Blue channel set to ");
          Serial.println(pinState == HIGH ? "ON" : "OFF");
          break;
          
        default:
          Serial.println("Error: Unknown color. Use R, G, or B.");
          break;
      }
    } else if (command.length() > 0) {
      // Catch invalid short commands (ignoring empty blank lines)
      Serial.println("Error: Command too short. Use format like 'R1'.");
    }
  }
}
