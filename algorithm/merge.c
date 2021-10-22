#include <stdio.h>

typedef int item_t;
int main(size_t argc, char *argv[]){
	FILE *fp0, *fp1;
	item_t num0, num1;
	if(argc<3){
		printf("Usage: %s file1 file2\n","merge.exe");
		return 1;
	}
	fp0=fopen(argv[1],"r");
	fp1=fopen(argv[2],"r");
	if(!fp0){
		printf("Fail to open file %s\n",argv[1]);
		return 1;
	}
	if(!fp1){
		printf("Fail to open file %s\n",argv[2]);
		return 1;
	}
	/*Merging in process*/
	fscanf(fp0,"%d",&num0);
	fscanf(fp1,"%d",&num1);
	while(!feof(fp0) && !feof(fp1)){
		if(num0<=num1){
			printf("%d\n",num0);
			fscanf(fp0,"%d",&num0);
		}else{
			printf("%d\n",num1);
			fscanf(fp1,"%d",&num1);
		}
	}
	if(!feof(fp0)){
		while(EOF!=fscanf(fp0,"%d",&num0)){
			printf("%d\n",num0);
		}
	}else if(!feof(fp1)){
		while(EOF!=fscanf(fp1,"%d",&num1)){
			printf("%d\n",num1);
		}
	}
	fclose(fp0);
	fclose(fp1);
	return 0;
}