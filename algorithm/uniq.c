#include <stdio.h>
#include <malloc.h>

typedef int value_t;
typedef enum __rbtree_color_t{
	RBTREE_BLACK,
	RBTREE_RED
}rbtree_color_t;
typedef enum __rbtree_insert_pos_t{
	INSERT_LEFT,
	INSERT_RIGHT
}rbtree_insert_pos_t;
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
	unsigned int counter=0x7fff;
	leaf_t *p=tree->root, *insert=NULL,
		*parent=NULL, *gParent=NULL, *uParent=NULL, *ggParent=NULL;
	rbtree_insert_pos_t insertPos;
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
	while(counter--){
		if(!insert){
			break;
		}
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
	/*
	if(!counter){
		puts("Dead loop");
		exit(1);
	}
	*/

	return 1;
}
void __rbtree_leaf_dump(rbtree_leaf_t *leaf, int level){
	int i;
	for(i=0; i<level; i++){
		putchar(' ');
		putchar(' ');
	}
	if(!leaf){
		puts("NULL");
		return;
	}
	printf("%c,%d\n",leaf->color ? 'r' : 'B',leaf->value);
	if(NULL==leaf->left && NULL==leaf->right){
		return;
	}
	__rbtree_leaf_dump(leaf->left,level+1);
	__rbtree_leaf_dump(leaf->right,level+1);
}
void rbtree_dump(rbtree_t *tree){
	if(!(tree->root)){
		return;
	}
	__rbtree_leaf_dump(tree->root, 0);
}
int main(){
	rbtree_t tree;
	value_t input;
	rbtree_init(&tree);
	while(EOF!=scanf("%d",&input)){
		if(rbtree_push(&tree,input)){
			printf("%d\n",input);
		}
	}
	//rbtree_dump(&tree);
	rbtree_close(&tree);
	return 0;
}