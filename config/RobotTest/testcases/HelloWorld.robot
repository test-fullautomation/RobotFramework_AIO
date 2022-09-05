*** Settings ***
#Library         Selenium2Library
 
*** Test Cases ***
Hello World
   FOR    ${index}    IN RANGE    1    11
      Log  Hello world ${index}
   END