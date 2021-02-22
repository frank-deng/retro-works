module.exports=class{
  constructor(maxlength){
    const maxlength_min=2;
    if(maxlength<maxlength_min){
      throw new RangeError('Cache size must be larger than '+maxlength_min);
    }
    this.maxlength=maxlength;
    this.length=0;
    //链表准备
    this.header=this.tail=null;
    //索引表准备
    this.hashIndex={};
  }
  set(data,key=null){
    //未提供key则使用待缓存的数据作为key
    if(!key){
      key=data;
    }

    //当前key对应的项目已存在，走人
    if(this.hashIndex[key]){
      return;
    }

    //Cache项目准备
    let item={
      key,
      data,
      prev:null,
      next:null
    };

    //插入到索引表中
    this.hashIndex[key]=item;

    //Cache中没有项目
    if(!this.header){
      this.header=this.tail=item;
      this.length=1;
      return;
    }

    //插入到链表尾
    item.prev=this.tail;
    this.tail.next=item;
    this.tail=item;

    //Cache未满
    if(this.length<this.maxlength){
      this.length++;
      return;
    }

    //Cache已满，淘汰表头项目（最少使用的）
    let itemKnockout=this.header;
    delete this.hashIndex[itemKnockout.key];
    this.header=itemKnockout.next;
    this.header.prev=null;
  }
  get(key){
    let item=this.hashIndex[key];
    //未命中
    if(!item){
      return null;
    }

    //链表中只有1个项目，不做任何处理
    if(this.header==this.tail){
      return item.data;
    }

    //从链表中删除当前项目
    if(item==this.tail){
      this.tail=item.prev;
      this.tail.next=null;
    }else if(item==this.header){
      this.header=item.next;
      this.header.prev=null;
    }else{
      item.prev.next=item.next;
      item.next.prev=item.prev;
    }

    //将当前项目插入到链表尾部
    item.prev=this.tail;
    item.next=null;
    this.tail.next=item;
    this.tail=item;

    //返回命中的数据
    return item.data;
  }
}

