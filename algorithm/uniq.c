#include <stdio.h>
#include <malloc.h>
#include <string.h>

typedef char* value_t;
typedef enum{
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
typedef struct{
	rbtree_leaf_t *root;
}rbtree_t;

void rbtree_init(rbtree_t *tree){
	tree->root=NULL;
}
static void __rbtree_free_leaf(rbtree_leaf_t *leaf){
	if(leaf->left){
		__rbtree_free_leaf(leaf->left);
		leaf->left=NULL;
	}
	if(leaf->right){
		__rbtree_free_leaf(leaf->right);
		leaf->right=NULL;
	}
	free(leaf->value);
	leaf->value=NULL;
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
	result->value=(char*)malloc(sizeof(char)*(strlen(value)+1));
	strcpy(result->value,value);
	return result;
}
static rbtree_leaf_t *__get_neighbour(rbtree_leaf_t *leaf){
	rbtree_leaf_t *parent=NULL;
	if(!leaf || !(leaf->parent)){
		return NULL;
	}
	parent=leaf->parent;
	return leaf==parent->left ? parent->right : parent->left;
}
static void __rbtree_update_parent(
	rbtree_t *tree, rbtree_leaf_t *oldLeaf, rbtree_leaf_t *newLeaf){
	rbtree_leaf_t *parent=NULL;
	if(!oldLeaf){
		return;
	}
	parent=oldLeaf->parent;
	if(newLeaf){
		newLeaf->parent=parent;
	}
	if(!parent){
		tree->root=newLeaf;
	}else if(oldLeaf==parent->left){
		parent->left=newLeaf;
	}else if(oldLeaf==parent->right){
		parent->right=newLeaf;
	}
}
static void __rbtree_right_rotate(rbtree_t *tree, rbtree_leaf_t *leaf){
	rbtree_leaf_t *leafLeft;
	if(!leaf){
		return;
	}
	leafLeft=leaf->left;
	if(!leafLeft){
		return;
	}
	__rbtree_update_parent(tree,leaf,leafLeft);
	leaf->left=leafLeft->right;
	if(leaf->left){
		leaf->left->parent=leaf;
	}
	leafLeft->right=leaf;
	leaf->parent=leafLeft;
}
static void __rbtree_left_rotate(rbtree_t *tree, rbtree_leaf_t *leaf){
	rbtree_leaf_t *leafRight;
	if(!leaf){
		return;
	}
	leafRight=leaf->right;
	if(!leafRight){
		return;
	}
	__rbtree_update_parent(tree,leaf,leafRight);
	leaf->right=leafRight->left;
	if(leaf->right){
		leaf->right->parent=leaf;
	}
	leafRight->left=leaf;
	leaf->parent=leafRight;
}
int rbtree_push(rbtree_t *tree, value_t value){
	leaf_t *p=tree->root, *insert=NULL,
		*parent=NULL, *gParent=NULL, *uParent=NULL;
	int comp=0;
	//Create root node
	if(!p){
		tree->root=__create_leaf(NULL,value);
		tree->root->color=RBTREE_BLACK;
		return 1;
	}
	//Find the correct insert position and insert the data
	while(p){
		comp=strcmp(value,p->value);
		if(!comp){
			return 0;
		}
		if(comp>0){
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
			__rbtree_right_rotate(tree,gParent);
			break;
		}
		//Change color and left rotate
		if(insert==parent->right && parent==gParent->right){
			parent->color=RBTREE_BLACK;
			gParent->color=RBTREE_RED;
			__rbtree_left_rotate(tree,gParent);
			break;
		}
		if(insert==parent->left && gParent->right==parent){
			__rbtree_right_rotate(tree,parent);
			insert=parent;
			continue;
		}
		if(insert==parent->right && gParent->left==parent){
			__rbtree_left_rotate(tree,parent);
			insert=parent;
			continue;
		}
	}
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
	char input[2048]="";
	rbtree_init(&tree);
	while(NULL!=gets(input)){
		if(rbtree_push(&tree,input)){
			puts(input);
		}
	}
	//rbtree_dump(&tree);
	rbtree_close(&tree);
	return 0;
}