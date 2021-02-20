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
const cache=new Cache(3);

cache.set('1');
cache.get('1');
console.log(getCacheContent(cache), cache.length);
checkIntegrity(cache);
cache.set('1');
cache.get('1');
console.log(getCacheContent(cache), cache.length);
checkIntegrity(cache);
cache.set('2');
cache.set('3');
cache.set('4');
console.log(getCacheContent(cache), cache.length);
checkIntegrity(cache);

