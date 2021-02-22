function checkIntegrity(cache){
  let header=cache.header, tail=cache.tail, result=[], resultReverse=[], counter=100000;
  while(header && tail && --counter){
    result.push(header);
    resultReverse.unshift(tail);
    header=header.next;
    tail=tail.prev;
  }

  if(result.length != resultReverse.length
    || result.length != cache.length){
    throw new Error('链表完整性校验未通过');
  }

  for(let i=0; i<result.length; i++){
    if(result[i] != resultReverse[i]){
      throw new Error('链表完整性校验未通过');
    }
  }

  for(let key of Object.keys(cache.hashIndex)){
    let item=cache.hashIndex[key];
    if(-1==result.indexOf(item)){
      throw new Error('链表完整性校验未通过'); 
    }
  }
  for(let item of result){
    if(!cache.hashIndex[item.key]){
      throw new Error('链表完整性校验未通过'); 
    }
  }

  return true;
}
function getCacheContent(cache){
  let pointer=cache.header, result=[], counter=100000;
  while(pointer && --counter){
    result.push(pointer.data);
    pointer=pointer.next;
  }
  if(counter<0){
    console.error('死循环');
  }
  return result;
}

const Cache=require('./CacheLRU');

const assert = require('assert');
describe('Cache创建',function(){
  it('总长正常',function(){
    assert.ok(new Cache(2));
    assert.ok(new Cache(3));
    assert.ok(new Cache(4));
    assert.ok(new Cache(10));
  });
  it('总长太小',function(){
    assert.throws(function(){
      new Cache(1);
    }, RangeError, /Cache size must be larger than 2/);
  });
});
describe('Cache中数据完整性检查',function(){
  it('没有数据',function(){
    const cache=new Cache(3);
    assert.equal(cache.get('1'),null);
    assert.equal(cache.get('2'),null);
    assert.deepEqual(cache.hashIndex,{});
  });
  it('1条数据',function(){
    const cache=new Cache(3);
    cache.set('1');
    assert.equal(cache.get('1'),'1');
    assert.equal(cache.get('2'),null);
    assert.deepEqual(cache.hashIndex,{'1':cache.header});
    assert.ok(checkIntegrity(cache));
  });
  it('多条数据',function(){
    const cache=new Cache(3);
    cache.set('1');
    assert.ok(checkIntegrity(cache));
    cache.set('2');
    assert.ok(checkIntegrity(cache));
    cache.set('3');
    assert.deepEqual(getCacheContent(cache),['1','2','3']);
    assert.ok(checkIntegrity(cache));
    cache.set('4');
    assert.equal(cache.get('1'),null);
    assert.equal(cache.get('2'),'2');
    assert.ok(checkIntegrity(cache));
    assert.deepEqual(getCacheContent(cache),['3','4','2']);
  });
});

