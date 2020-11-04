
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <stdlib.h>
#include <sys/time.h>

int main(int argc, char *argv[]){
  int temp;
  printf("n args %d\n", argc);
  for(int i=0; i < argc; i++){
    printf("%s\n", argv[i]);
  }

  for(int i=1; i < argc; i=i+2){
    printf("%d %s\n", i, argv[i]);
    printf("%d\n", strcmp(argv[i], "-a"));
    if(strcmp(argv[i], "-a")==0){
      // sscanf(argv[i+1], "%d", &temp);
      // printf("hello %d %d\n", i, temp);
      printf("hello %d %d\n", i, atoi(argv[i+1]));
    } else if(strcmp(argv[i], "-b")==0){
      // sscanf(argv[i+1], "%d", &temp);
      // printf("world %d %d\n", i, temp);
      printf("world %d %d\n", i, atoi(argv[i+1]));
    } else{
      printf("hello world\n");
    }
  }
}