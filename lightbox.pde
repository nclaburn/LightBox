const int LED_RESET     = 25;
const int RED_LED       = 11;
const int GREEN_LED     = 9;
const int BLUE_LED      = 10;
const int YELLOW_LED    = 26;


// LED ARRAY used for randomizing LEDs
const int LED_ARRAY [] = {  RED_LED, GREEN_LED, BLUE_LED };
bool randomize = true;
bool commandMode = false;
bool dark = false;

// variables used for temperature monitoring
const int ONE_SECOND = 1000;
const int FIFTEEN_SECONDS = 15000;
const int THIRTY_SECONDS = 30000;
const int SIXTY_SECONDS = 60000;

const int POLL_INTERVAL_ARRAY [] = {  ONE_SECOND, FIFTEEN_SECONDS, THIRTY_SECONDS, SIXTY_SECONDS };
float temperature = 0;
const int TEMPERATURE_PIN = 0;
bool pollingTemperature = false;
int pollingInterval = 1000;

struct tRgbValue
{
  tRgbValue( byte redValue = 0, byte blueValue = 0, byte greenValue = 0 )
  {
    red = redValue;
    green = greenValue;
    blue = blueValue;
  };
  byte red;
  byte green;
  byte blue;
};

struct tLedColor
{
  tLedColor( int color = GREEN_LED, const byte redValue = 0, const byte greenValue = 255, const byte blueValue = 0 )
  {
    Color = color;
    RgbValue.red = redValue;
    RgbValue.green = greenValue;
    RgbValue.blue = blueValue;
  };
  
  tLedColor( int color, const tRgbValue rgbValue)
  {
    Color = color;
    RgbValue = rgbValue;
  };
     
  int Color;
  tRgbValue RgbValue;
};

const tLedColor RED_COLOR( RED_LED, 0, 255, 255 );
const tLedColor GREEN_COLOR( GREEN_LED, 255, 0, 255 );
const tLedColor BLUE_COLOR( BLUE_LED, 255, 0, 0 );
const tLedColor YELLOW_COLOR( YELLOW_LED, 0, 0, 255 );

enum
{
  GOOD     = 0,
  WARNING  = 1,
  ERROR    = 2,
  DANGER   = 3,
  FLASH    = 4
};

int multiplierArray[] = { 20, 15, 10, 5, 1};

tLedColor lastColor = GREEN_COLOR;
int lastError = GOOD;
 
void setup() 
{ 
  randomSeed( analogRead( TEMPERATURE_PIN ) );
  Serial.begin(9600);
  pinMode(GREEN_LED, OUTPUT);
  pinMode(BLUE_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);
  resetLEDs();
  Serial.println( "Lightbox initialized" );
  SoftwareSerial receiver = SoftwareSerial( RX_PIN, TX_PIN );
  receiver.begin();
} 

void fadeLED( tRgbValue &led, int level )
{
  int maxIntensity = 0;
  
  if( led.red < led.green )
    maxIntensity = led.red;
  else if( led.blue < led.red )
    maxIntensity = led.blue;
  else
    maxIntensity = led.green;
  
  int value = 255;
  
  while( value > maxIntensity )
  {
    if( led.red <= value )
      analogWrite( RED_LED, value );
    if( led.green <= value  )
      analogWrite( GREEN_LED, value );
    if( led.blue <= value  )
      analogWrite( BLUE_LED, value );
    delay( multiplierArray[level] );
    value--;
  }
  delay( 250 );
  while( value < 255 )
  {
    if( value >= led.red )
      analogWrite( RED_LED, value );
    if( value >= led.green )
      analogWrite( GREEN_LED, value );
    if( value >= led.blue )
      analogWrite( BLUE_LED, value );
    delay( multiplierArray[level] );
    value++;
  }
}

void fadeRandom( void )
{
  int maxRGB = 125;
  tRgbValue led( random( maxRGB, 255), random( maxRGB, 255), random( maxRGB, 255) );
  int level = random( 0, 3);
  fadeLED( led, level );
}

void resetLEDs( void )
{
  analogWrite( RED_LED, 255 );
  analogWrite( GREEN_LED, 255 );
  analogWrite( BLUE_LED, 255 );
}

// returns the temperature in celcius
int pollTemperature( void )
{
  int value = analogRead( TEMPERATURE_PIN );
  Serial.print( "Raw temp reading = " );
  Serial.println( value, DEC );
  Serial.print( "Calculated value = " );
  return ( ( 5.0 * value * 100.0 ) / 1024.0 );
}

void loop(  ) 
{ 
  if( Serial.available() )
  {
    //randomize = false;
    int led = Serial.read();
    
    switch( led )
    {
      case 'p':
      case 'P':
      {
        char val = Serial.read();
        
        // want to poll with the random time interval
        if( ( val == 'Z' ) ||
            ( val == 'z' ) )
        {
          randomize = true;
          pollingTemperature = true;
          pollingInterval = 0;
          Serial.println("Temperature polling with light sequence.");
        }
        else if( ( val == 'o' ) ||
                 ( val == 'O' ) )
        {          
          pollingTemperature = false;
          Serial.println( "Temperature polling off." );
        }
        else // we read the interval
        {
          pollingInterval = val - 48;
          
          // if the polling interval is out of range....
          if( ( pollingInterval < 0 ) ||
              ( pollingInterval > 3 ) )
          {
            Serial.print( "Polling interval out of range: " );
            Serial.println( pollingInterval + 48, DEC );
            Serial.println( "Defaulting to 1 second" );
            pollingInterval = POLL_INTERVAL_ARRAY[ ONE_SECOND ];
          }
          else // the polling interval is within range
          {
            randomize = false;
            pollingInterval = POLL_INTERVAL_ARRAY[ pollingInterval ];
            pollingTemperature = true;
            Serial.print( "Polling temperature every " );
            Serial.println( pollingInterval, DEC );
          }
        }
        return;
        break;
      }        
      case 't':
      case 'T':
      {
        Serial.println( pollTemperature(), DEC );
        return;
        break;
      } 
      case 'c':
      case 'C':
      {  
        resetLEDs();
        lastColor   = GREEN_COLOR;
        lastError = GOOD;
        pollingTemperature = false;
        randomize = false;
        Serial.println( "Lightbox command mode." );
        commandMode = true;
        return;
      }
      break;
      case 'D':
      case 'd':
        dark = !dark;
        resetLEDs();
        if( dark )
          Serial.println( "Lightbox is now dark." );
        else
          Serial.println( "Lightbox is now lit." );
          
        return;
        break;
      case 'z':
      case 'Z':
      {
        randomize = true;
        dark = false;
        commandMode = false;
        Serial.println( "Lightbox Internal randomization." );
        return; 
      }
      break;
      case 'f':
      case 'F':
      {
        randomize = false;
        lastError = FLASH;
        return;
      }     
      break;
      case 'R':
      case 'r':
      {
        randomize = false;
        lastColor = RED_COLOR;
        break;
      }
      case 'B':
      case 'b':
      {
        randomize = false;
        lastColor = BLUE_COLOR;
        break;
      }
      case 'G':
      case 'g':
      {
        randomize = false;
        lastColor = GREEN_COLOR;
        break;
      }
      case 'Y':
      case 'y':
      {
        randomize = false;
        lastColor = YELLOW_COLOR;
        break;
      }
      default:
      {
        Serial.print( "Unknown command " );
        //Serial.println( lastColor, BYTE );
        lastColor = YELLOW_COLOR;
        lastError = FLASH;
        return;
      }
    }
    
    byte errorLevel = 0;    
    int levelIn = Serial.read() - 48;
    errorLevel = levelIn;  
    
    if( ( errorLevel >= 0 ) && ( errorLevel < 5 ) )
      lastError = errorLevel;
    else
    {
      Serial.print( "Value " );
      Serial.print( errorLevel, DEC );
      Serial.println( " out of range." );
    }
    
    /*Serial.print( "Letter=" );
    Serial.println( lastColor, BYTE );
    Serial.print( "Error=" );
    Serial.println( lastError, DEC );*/
   
  } 
  else // if we're not receiving serial data
  {  
    if( !commandMode )
    {
      // if we're randomizing lights
      if( randomize ) // should we randomize?
      {
        fadeRandom();
        
        // if we're polling & lights are on then our interval is tied
        // to the light 
        if( pollingTemperature )
          Serial.println( pollTemperature(), DEC );    
      }
      else // we're not randomizing
      {
        // if we're polling then poll to the interval
        if( pollingTemperature )
        {
          Serial.println( pollTemperature(), DEC );    
          delay( pollingInterval );
        }
      }
    }
    
    if( commandMode && !dark ) // just fade the last thing.
    {
      fadeLED( lastColor.RgbValue, lastError );  
      resetLEDs();
    }    
  }
}
