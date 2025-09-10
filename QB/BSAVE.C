#include <stdio.h>

#define BLOCK_SIZE (4096)
#define MAX_SIZE (0xffff)

int main(int argc,char *argv[])
{
	unsigned long total_size=0,rsize=0;
	unsigned char buf[BLOCK_SIZE],u8_val;
	unsigned short u16_val;
	char *psrc,*pdest;
	FILE *fsrc=NULL,*fdest=NULL;
	if(argc<3){
		fprintf(stderr,"Usage: %s input_file output_file\n",argv[0]);
		return 1;
	}
	psrc=argv[1];
	pdest=argv[2];
	fsrc=fopen(psrc,"rb");
	if(fsrc==NULL){
		fprintf(stderr,"Failed to open source file %s\n",psrc);
		return 1;
	}
	fdest=fopen(pdest,"wb");
	if(fdest==NULL){
		fclose(fsrc);
		fprintf(stderr,"Failed to open dest file %s\n",pdest);
		return 1;
	}
	if(fseek(fsrc,0,SEEK_END)!=0){
		fprintf(stderr,"Failed to get src file size\n");
		goto end;
	}
	total_size=ftell(fsrc);
	if(total_size>MAX_SIZE){
		fprintf(stderr,"Src file size exceeds 64k\n");
		goto end;
	}
	fseek(fsrc,0,SEEK_SET);
	fseek(fdest,0,SEEK_SET);
	u8_val=0xfd;
	fwrite(&u8_val,1,sizeof(u8_val),fdest);
	u16_val=0;
	fwrite(&u16_val,1,sizeof(u16_val),fdest);
	fwrite(&u16_val,1,sizeof(u16_val),fdest);
	u16_val=total_size;
	fwrite(&u16_val,1,sizeof(u16_val),fdest);
	rsize=fread(buf,1,sizeof(buf),fsrc);
	while(rsize>0){
		fwrite(buf,1,rsize,fdest);
		rsize=fread(buf,1,sizeof(buf),fsrc);
	}
	u8_val=0x1a;
	fwrite(&u8_val,1,sizeof(u8_val),fdest);
	printf("Data size: %lu\n",total_size);
end:
	fclose(fdest);
	fclose(fsrc);
	return 0;
}

