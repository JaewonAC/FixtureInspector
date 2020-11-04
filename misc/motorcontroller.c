#include <wiringPi.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <stdlib.h>
#include <sys/time.h>

#define ENCODER_A_PIN 0
#define ENCODER_B_PIN 2
#define PWM_PIN     1
#define DIR_PIN     16

volatile int step = 0;

void encoder_a_interrupt(void){
  if(digitalRead(ENCODER_A_PIN) == digitalRead(ENCODER_B_PIN)){
    step--;
  } else {
    step++;
  }
}

void encoder_b_interrupt(void){
  if(digitalRead(ENCODER_A_PIN) == digitalRead(ENCODER_B_PIN)){
    step++;
  } else {
    step--;
  }
}

int main(int argc, char *argv[]){
  int target_step = 0;
  float wait = 500;
  float p_gain = 1;
  float i_gain = 0.001;
  float d_gain = 0.001;
  int control_cw_min = 50;
  int control_ccw_min = 600;
  int control_cw_max = 600;
  int control_ccw_max = 700;
  
  for(int i=1;i<argc;i=i+2){
    if(strcmp(argv[i], "-t")==0){
      sscanf(argv[i+1], "%d", &target_step);
    } else if(strcmp(argv[i], "-w")==0){
      sscanf(argv[i+1], "%f", &wait);
    } else if(strcmp(argv[i], "-pg")==0){
      sscanf(argv[i+1], "%f", &p_gain);
    } else if(strcmp(argv[i], "-ig")==0){
      sscanf(argv[i+1], "%f", &i_gain);
    } else if(strcmp(argv[i], "-dg")==0){
      sscanf(argv[i+1], "%f", &d_gain);
    } else if(strcmp(argv[i], "-cmn")==0){
      sscanf(argv[i+1], "%d", &control_cw_min);
    } else if(strcmp(argv[i], "-ccmn")==0){
      sscanf(argv[i+1], "%d", &control_ccw_min);
    } else if(strcmp(argv[i], "-cmx")==0){
      sscanf(argv[i+1], "%d", &control_cw_max);
    } else if(strcmp(argv[i], "-ccmx")==0){
      sscanf(argv[i+1], "%d", &control_ccw_max);
    }
  }

  delay(wait);
  
  int ret = 0;

  ret = wiringPiSetup();
  if (ret < 0) {
    printf("Unable to setup wiring pi\n");
    fprintf (stderr, "Unable to setup wiringPi: %s\n", strerror (errno));
    return 1;
  } else {
    // printf("wiringPiSetup succeed. %d\n", ret);
  }

  pinMode(PWM_PIN, PWM_OUTPUT);
  pinMode(DIR_PIN, OUTPUT);
  pinMode(ENCODER_A_PIN, INPUT);
  pinMode(ENCODER_B_PIN, INPUT);

  ret = wiringPiISR(ENCODER_A_PIN, INT_EDGE_BOTH, &encoder_a_interrupt);
  if(ret < 0){
    printf("unable to setup ISR\n");
    fprintf(stderr, "Unable to setup ISR: %s\n", strerror(errno));
  } else {
    // printf("wiringPiISR ENCODER_A_PIN to encoder_a_interrupt succeed. %d\n", ret);
  }

  ret = wiringPiISR(ENCODER_B_PIN, INT_EDGE_BOTH, &encoder_b_interrupt);
  if(ret < 0){
    printf("unable to setup ISR\n");
    fprintf(stderr, "Unable to setup ISR: %s\n", strerror(errno));
  } else {
    // printf("wiringPiISR ENCODER_B_PIN to encoder_b_interrupt succeed. %d\n", ret);
  }

  // while(1){
  //   digitalWrite(DIR_PIN, LOW);
  //   pwmWrite(PWM_PIN, 300);
  // }
  
  struct timeval tv;
  gettimeofday(&tv, NULL);
  int cur_usec, delta_usec, prev_usec = 1000000*tv.tv_sec + tv.tv_usec;
  int error, prev_step = 0;
  int prev_error = 0;
  int stability = 0;
  int stability_max = 10;
  // printf("%d", prev_usec);
  while(stability < stability_max){
    gettimeofday(&tv, NULL);
    cur_usec = 1000000*tv.tv_sec + tv.tv_usec;
    delta_usec = cur_usec-prev_usec;
    error = target_step - step;
    float control = p_gain*(float)error +
                    i_gain*(float)error*delta_usec +
                    d_gain*(float)(error-prev_error)*delta_usec;
    // printf("prev : %d cur : %d delta : %d\n", prev_usec, cur_usec, delta_usec);
    // printf("target_step : %d step: %d\n", target_step, step);
    // printf("control : %f ", control);
    
    if(error == 0){
      digitalWrite(DIR_PIN, HIGH);
      pwmWrite(PWM_PIN, 1023);
      control = 0;
      stability++;
    } else {
      if(control>0){
        digitalWrite(DIR_PIN, LOW);
        control = control > control_cw_max ? control_cw_max : control;
        control = control < control_cw_min ? control_cw_min : control;
      } else {
        digitalWrite(DIR_PIN, HIGH);
        control = abs(control) > control_ccw_max ? control_ccw_max : abs(control);
        control = 1023 - (abs(control) < control_ccw_min ? control_ccw_min : abs(control));
      }
      pwmWrite(PWM_PIN, control);
      stability = 0;
    }
    // printf("after control : %f\n", control);

    prev_usec = cur_usec;
    prev_step = step;
    prev_error = error;
    delay(9);
  }
  
  digitalWrite(DIR_PIN, LOW);
  pwmWrite(PWM_PIN, 0);
}