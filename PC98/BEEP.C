#include <dos.h>
int main(){
  sound(2000);
  delay(500);
  sound(1000);
  delay(500);
  nosound();
  return 0;
}