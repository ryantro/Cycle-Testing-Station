long pos = 0;
String incomingStr;
#define MAX 40000
#define PUL 9
#define DIR 8

#define LZ 12
#define LM 11 


const byte numChars = 32;
char receivedChars[numChars];
boolean newData = false;
boolean isMoving = false;

void setup() {
  
  // configure pins to controll the stepper motor
  
  pinMode(PUL,OUTPUT);  // set Pin9 as PUL
  pinMode(DIR,OUTPUT);  // set Pin8 as DIR
  Serial.begin(9600);

  // configure pins for the limit switches
  
  pinMode(LZ, INPUT_PULLUP);
  pinMode(LM, INPUT_PULLUP);
}
/////



void loop() {
    recvWithStartEndMarkers();
    showNewData();
}

void recvWithStartEndMarkers() {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;
 
    while (Serial.available() > 0 && newData == false) {
        rc = Serial.read();

        if (recvInProgress == true) {
            if (rc != endMarker) {
                receivedChars[ndx] = rc;
                ndx++;
                if (ndx >= numChars) {
                    ndx = numChars - 1;
                }
            }
            else {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                newData = true;
            }
        }

        else if (rc == startMarker) {
            recvInProgress = true;
        }
    }
}

void showNewData() {
    if (newData == true) {
        //Serial.print("This just in ... ");
        //Serial.println(receivedChars);
        parseStr(receivedChars); 
        newData = false;
    }
}


/*
void loop() {
  handleSerial();
}
*/

/*
 * Function: handleSerial
 * ----------------------------
 * reads the serial input.
 */
void handleSerial() {
  
  while (Serial.available() > 0) {

  const char fda = '\n';
  
  incomingStr = Serial.readStringUntil('\r');  // read until timeout
  incomingStr.trim();                            // remove and \r \n whitespace at the end of the String
  parseStr(incomingStr);                         // parse the incoming String
  
 }
}





/*
 * Function: parseStr
 * ----------------------------
 * parses the input string read in through serial
 */
void parseStr(String command){

  /*
   * Check for relative movement command
   */
  if (command.indexOf("MOVEREL") != -1) {
    int index = command.indexOf(" ");           // split string
    String sub_s = command.substring(index,-1); // find number of pulses
    sub_s.trim();                               // trim str
    long i = sub_s.toInt();                      // convert str to int
    
    // check movement direction of stage
    if(i > 0) {
      moveStageUp(i);       // move stage up
    } else if (i < 0) {
      moveStageDown(-i);    // move stage down
    }

    // print stage position
    Serial.println(pos);
    
    return;
  }
  /*
   * check for absolute movement command
   */
  if (command.indexOf("MOVEABS") != -1) {
    int index = command.indexOf(" ");           // split string
    String sub_s = command.substring(index,-1); // find number of pulses
    sub_s.trim();                               // trim str
    long i = sub_s.toInt();                     // convert str to int
    
    moveAbs(i);   // move stage
    
    // print stage position
    Serial.println(pos);

    
    return;
  }
  /*
   * read the value of the zero limit switch
   */
  if (command.indexOf("READLZ") != -1){
    
    int sensorVal = digitalRead(LZ);
    Serial.println(sensorVal);
    
    return;
  }
  /*
   * read the value of the max limit switch
   */
  if (command.indexOf("READLM") != -1){

    int sensorVal = digitalRead(LM);
    Serial.println(sensorVal);
    
    return;
  }
  if (command.indexOf("POS?") != -1){

    Serial.println(pos);
    
    return;
  }
  /* TODO:
   * command to zero the system
   */
  if (command.indexOf("ZERO") != -1) {
    zero();
    Serial.println(pos);
    return;
  }

  Serial.println("ERROR");

}

void moveAbs(long i){
  long c = i - pos;
  if(c > 0) {
    moveStageUp(c);       // move stage up
  } else if (c < 0) {
    moveStageDown(-c);    // move stage down
  }
}

/* Fuction: moveStageDown
 * -------------
 * handles moving the stage down
 */
void moveStageDown(long i){
  isMoving = true;
  digitalWrite(DIR,HIGH);     // set high level direction
  delayMicroseconds(10);
  for(long x = 0; x < i; x++) // repeat 400 times a revolution when setting 400 on driver
  {
    if(pos > 0){

      if(digitalRead(LM) == HIGH){
        digitalWrite(PUL,HIGH); // output high
        delayMicroseconds(500); // set rotate speed
        digitalWrite(PUL,LOW);  // output low
        delayMicroseconds(500); // set rotate speed
        pos = pos - 1;
      } else {
        break;
      }
    } else {
      isMoving = false;
      break;
    }
  }
}

/* Fuction: zero
 * -------------
 * handles zeroing the stage
 */
void zero(){
  isMoving = true;
  digitalWrite(DIR,HIGH);     // set high level direction
  delayMicroseconds(10);
  while(digitalRead(LM) == HIGH){
    digitalWrite(PUL,HIGH); // output high
    delayMicroseconds(500); // set rotate speed
    digitalWrite(PUL,LOW);  // output low
    delayMicroseconds(500); // set rotate speed
  }
  isMoving = false;
  pos = 0;
}

/* Fuction: moveStageUp
 * -------------
 * handles moving the stage up
 */
void moveStageUp(long i){
  isMoving = true;
  digitalWrite(DIR,LOW); // set high level direction
  delayMicroseconds(10);
  for(long x = 0; x < i; x++)
  {
    if(digitalRead(LZ) == HIGH){
      if(pos < MAX){
        digitalWrite(PUL,HIGH);
        delayMicroseconds(500);
        digitalWrite(PUL,LOW);
        delayMicroseconds(500);
        pos = pos + 1;
      } else {
        break;
      }
    } else {
      isMoving = false;
      break;
    }
  }
}
