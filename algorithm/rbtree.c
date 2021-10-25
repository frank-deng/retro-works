#include <stdio.h>
#include <malloc.h>
#include <assert.h>

typedef int value_t;
typedef enum __rbtree_color_t{
	RBTREE_BLACK,
	RBTREE_RED
}rbtree_color_t;
typedef struct __rbtree_leaf_t{
	struct __rbtree_leaf_t *parent;
	struct __rbtree_leaf_t *left;
	struct __rbtree_leaf_t *right;
	rbtree_color_t color;
	value_t value;
}rbtree_leaf_t;
typedef rbtree_leaf_t leaf_t;
typedef struct __rbtree_t{
	rbtree_leaf_t *root;
}rbtree_t;

void rbtree_init(rbtree_t *tree){
	tree->root=NULL;
}
static void __rbtree_free_leaf(rbtree_leaf_t *leaf){
	if(leaf->left){
		__rbtree_free_leaf(leaf->left);
	}
	if(leaf->right){
		__rbtree_free_leaf(leaf->right);
	}
	free(leaf);
}
void rbtree_close(rbtree_t *tree){
	__rbtree_free_leaf(tree->root);
	tree->root=NULL;
}
static rbtree_leaf_t* __create_leaf(rbtree_leaf_t *parent, value_t value){
	rbtree_leaf_t* result=NULL;
	result=(rbtree_leaf_t*)malloc(sizeof(rbtree_leaf_t));
	if(!result){
		fprintf(stderr,"Memory allocation error.\n");
		exit(1);
	}
	result->parent=parent;
	result->left=NULL;
	result->right=NULL;
	result->color=RBTREE_RED;
	result->value=value; //Modify here with correspond data type
	return result;
}
rbtree_leaf_t* rbtree_find(rbtree_t *tree, value_t value){
	rbtree_leaf_t* p=tree->root;
	while(p){
		if(value == p->value){
			return p;
		}
		if(value < p->value){
			p=p->left;
		}else{
			p=p->right;
		}
	}
	return NULL;
}
static rbtree_leaf_t *__get_neighbour(rbtree_leaf_t *leaf){
	rbtree_leaf_t *parent=NULL;
	if(!leaf || !(leaf->parent)){
		return NULL;
	}
	parent=leaf->parent;
	return leaf==parent->left ? parent->right : parent->left;
}
int rbtree_push(rbtree_t *tree, value_t value){
	leaf_t *p=tree->root, *insert=NULL,
		*parent=NULL, *gParent=NULL, *uParent=NULL, *ggParent=NULL;
	//Create root node
	if(!p){
		tree->root=__create_leaf(NULL,value);
		tree->root->color=RBTREE_BLACK;
		return 1;
	}
	//Find the correct insert position and insert the data
	while(p){
		if(value == p->value){  //Modify here with corresponding comparison method
			return 0;
		}
		if(value < p->value){  //Modify here with corresponding comparison method
			if(p->left){
				p=p->left;
				continue;
			}
			insert=p->left=__create_leaf(p,value);
			break;
		}else{
			if(p->right){
				p=p->right;
				continue;
			}
			insert=p->right=__create_leaf(p,value);
			break;
		}
	}
	if(!insert){
		return 0;
	}

	//Start adjusting rbtree
	while(insert){
		parent=insert->parent;
		if(!parent){
			insert->color=RBTREE_BLACK;
			break;
		}else if(RBTREE_BLACK == parent->color){
			break;
		}
		gParent=parent->parent;
		uParent=(gParent->left==parent ? gParent->right : gParent->left);
		if(uParent && parent->color==uParent->color){
			parent->color=uParent->color=RBTREE_BLACK;
			gParent->color=RBTREE_RED;
			insert=gParent;
			continue;
		}
		//Change color and right rotate
		if(insert==parent->left && parent==gParent->left){
			parent->color=RBTREE_BLACK;
			gParent->color=RBTREE_RED;
			ggParent=gParent->parent;

			gParent->left=parent->right;
			if(gParent->left){
				gParent->left->parent=gParent;
			}
			parent->right=gParent;
			gParent->parent=parent;
			parent->parent=ggParent;
			if(!ggParent){
				tree->root=parent;
			}else if(ggParent->left==gParent){
				ggParent->left=parent;
			}else if(ggParent->right==gParent){
				ggParent->right=parent;
			}
			break;
		}
		//Change color and left rotate
		if(insert==parent->right && parent==gParent->right){
			parent->color=RBTREE_BLACK;
			gParent->color=RBTREE_RED;
			ggParent=gParent->parent;

			gParent->right=parent->left;
			if(gParent->right){
				gParent->right->parent=gParent;
			}
			parent->left=gParent;
			gParent->parent=parent;
			parent->parent=ggParent;
			if(!ggParent){
				tree->root=parent;
			}else if(ggParent->left==gParent){
				ggParent->left=parent;
			}else if(ggParent->right==gParent){
				ggParent->right=parent;
			}
			break;
		}
		if(insert==parent->left && gParent->right==parent){
			parent->left=insert->right;
			if(parent->left){
				parent->left->parent=parent;
			}
			parent->parent=insert;
			insert->right=parent;
			insert->parent=gParent;
			gParent->right=insert;
			insert=parent;
			continue;
		}
		if(insert==parent->right && gParent->left==parent){
			parent->right=insert->left;
			if(parent->right){
				parent->right->parent=parent;
			}
			parent->parent=insert;
			insert->left=parent;
			insert->parent=gParent;
			gParent->left=insert;
			insert=parent;
			continue;
		}
	}
	return 1;
}
static void __rbtree_delete_adjust(rbtree_t *tree, rbtree_leaf_t *leaf){
	rbtree_leaf_t *parent=NULL, *leafS=NULL, *leafSL=NULL, *leafSR=NULL, *leafGP=NULL;
	rbtree_color_t color;
	while(leaf && leaf->parent){
		parent=leaf->parent;
		leafS=leafSL=leafSR=leafGP=NULL;
		if(leaf==parent->left){
			leafS=parent->right;
		}else{
			leafS=parent->left;
		}
		if(leafS){
			leafSL=leafS->left;
			leafSR=leafS->right;
		}
		if(RBTREE_BLACK==parent->color
			&& (!leafS || RBTREE_BLACK==leafS->color)
			&& (!leafSL || RBTREE_BLACK==leafSL->color)
			&& (!leafSR || RBTREE_BLACK==leafSR->color)){
			if(leafS){
				leafS->color=RBTREE_RED;
			}
			leaf=parent;
			continue;
		}else if(RBTREE_RED==parent->color
			&& (!leafS || RBTREE_BLACK==leafS->color)
			&& (!leafSL || RBTREE_BLACK==leafSL->color)
			&& (!leafSR || RBTREE_BLACK==leafSR->color)){
			parent->color=RBTREE_BLACK;
			if(leafS){
				leafS->color=RBTREE_RED;
			}
			return;
		}else if((leafS && leafS==parent->right && RBTREE_BLACK==leafS->color)
			&& (leafSR && RBTREE_RED==leafSR->color)){
			leafS->color=parent->color;
			parent->color=RBTREE_BLACK;
			leafSR->color=RBTREE_BLACK;
			leafGP=parent->parent;
			leafS->left=parent;
			parent->parent=leafS;
			parent->right=leafSL;
			if(leafSL){
				leafSL->parent=parent;
			}
			if(!leafGP){
				tree->root=leafS;
			}else if(parent==leafGP->left){
				leafGP->left=leafS;
			}else if(parent==leafGP->right){
				leafGP->right=leafS;
			}
			return;
		}else if((leafS && leafS==parent->left && RBTREE_BLACK==leafS->color)
			&& (leafSL && RBTREE_RED==leafSL->color)){
			leafS->color=parent->color;
			parent->color=RBTREE_BLACK;
			leafSL->color=RBTREE_BLACK;
			leafGP=parent->parent;
			leafS->right=parent;
			parent->parent=leafS;
			parent->left=leafSR;
			if(leafSR){
				leafSR->parent=parent;
			}
			if(!leafGP){
				tree->root=leafS;
			}else if(parent==leafGP->left){
				leafGP->left=leafS;
			}else if(parent==leafGP->right){
				leafGP->right=leafS;
			}
			return;
		}
		return;
	}
}
void rbtree_delete(rbtree_t* tree, rbtree_leaf_t *leaf){
	rbtree_leaf_t *leafTemp=NULL, *leafP=NULL;
	if(!leaf){
		return;
	}
	//Node to be deleted has both left and right node
	if(leaf->left && leaf->right && leaf->right->left){
		leafTemp=leaf->right->left;
		while(leafTemp->left){
			leafTemp=leafTemp->left;
		}
		leaf->value=leafTemp->value;
		leaf=leafTemp;
	}

	//Start adjusting tree
	if(leaf->parent && RBTREE_BLACK==leaf->color){
		__rbtree_delete_adjust(tree,leaf);
		return;
	}

	//Deleting node
	leafP=leaf->parent;
	leafTemp=NULL;
	if(leaf->right){
		leafTemp=leaf->right;
		leafTemp->left=leaf->left;
		if(leafTemp->left){
			leafTemp->left->parent=leafTemp;
		}
	}else if(leaf->left){
		leafTemp=leaf->left;
	}
	if(leafTemp){
		leafTemp->parent=leafP;
	}
	if(!leafP){
		tree->root=leafTemp;
	}else if(leaf==leafP->left){
		leafP->left=leafTemp;
	}else if(leaf==leafP->right){
		leafP->right=leafTemp;
	}
	free(leaf);leaf=NULL;
}
void __rbtree_leaf_dump(rbtree_leaf_t *leaf, int level){
	int i;
	if(!leaf){
		for(i=0; i<level; i++){
			putchar(' ');
			putchar(' ');
		}
		puts("NULL");
		return;
	}
	if(NULL!=leaf->left || NULL!=leaf->right){
		__rbtree_leaf_dump(leaf->right,level+1);
	}
	for(i=0; i<level; i++){
		putchar(' ');
		putchar(' ');
	}
	printf("%c,%d\n",leaf->color ? 'r' : 'B',leaf->value);
	if(NULL!=leaf->left || NULL!=leaf->right){
		_|| NULL!=leaf->right){
		__rbtree_leaf_dump(leaf->left,level+1);
	}
}
void rbtree_dump(rbtree_t *tree){
	if(!(tree->root)){
		return;
	}
	__rbtree_leaf_dump(tree->root, 0);
	putchar('\n');
}
int main(){
	rbtree_t tree;
	value_t input=0;
	FILE *fp=NULL;
	rbtree_init(&tree);
	fp=fopen("3.txt","r");
	while(EOF!=fscanf(fp,"%d",&input) && input>=0){
		rbtree_push(&tree,input);
		//rbtree_dump(&tree);
	}
	rbtree_dump(&tree);
	rbtree_delete(&tree,rbtree_find(&tree,6));
	rbtree_dump(&tree);
	rbtree_close(&tree);
	fclose(fp);
	return 0;
}