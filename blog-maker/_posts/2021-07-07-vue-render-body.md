---
layout: post
title: "Vue.js处理组件中有DOM需要在父组件以外的地方渲染的情况"
tags: [HTML, JavaScript, Vue.js]
---

对于悬浮窗一类的组件，组件里的内容往往需要渲染在父组件以外的地方，比如`<body>`，此时组件内需要做如下操作：

1. 在组件中为需要渲染到`<body>`上的DOM加上`ref`，比如`<div ref="container"></div>`，以索引到对应的DOM，可以是组件中最顶层的DOM。
2. 调用`document.body.appendChild(this.$refs.container)`，将目标DOM移动到`<body>`上，可以在`mounted()`生命周期中调用，也可以在第一次打开悬浮窗时调用。**在组件被销毁前，只能调用一次，否则极易导致页面崩溃！！**
3. 如果目标DOM已经被移动到`<body>`上了，则需要在`beforeDestroy()`生命周期中手动将目标DOM从`<body>`中删除。**否则将导致有无用DOM残留在页面上，造成内存泄漏！！**

这样可以防止因弹出框不在`<body>`上而导致出现悬浮窗被意外遮挡等问题。

注意
----

此类操作对于`Vue.js`而言为**非正常操作**，极易导致页面出现问题，比如：

* 虚拟DOM和页面上的真实DOM不一致，导致页面逻辑错乱、页面崩溃甚至浏览器崩溃。
* 可能出现大量无用DOM没有及时删除并残留在`<body>`上，易导致页面卡顿、崩溃、甚至浏览器崩溃。

因此此类操作需要在项目中的公共组件中实现，且在项目中推广开前需要进行全面的测试；不到万不得已不要在和业务高度相关、复用率低的组件中实现，以防止代码逻辑陷入混乱。

范例
----

以下是一个简单的对话框组件的代码：

	<template>
	  <div class='dialog-container'
	    ref='dialogContainer'
	    v-show='this.visible'>
	    <slot v-if='this.visible || !this.destroyOnClose'></slot>
	  </div>
	</template>
	<script>
	export default {
	  props:{
	    visible:{
	      type:Boolean,
	      default:false
	    },
	    destroyOnClose:{
	      type:Boolean,
	      default:false
	    }
	  },
	  data(){
	    return{
	      container:null
	    };
	  },
	  watch:{
	    visible(visible){
	      //当对话框被打开时，将对话框组件对应的DOM移动到body上
	      if(visible && !this.container){
	        this.$nextTick().then(()=>{
	          this.container=this.$refs.dialogContainer;
	          document.body.appendChild(this.container);
	        });
	      }
	    }
	  },
	  beforeDestroy(){
	    //如果对话框被打开过，就需要手动从body上删除对话框组件对应的DOM
	    if(this.container){
	      document.body.removeChild(this.container);
	      this.container=null;
	    }
	  }
	}
	</script>
	<style lang="less" scoped>
	.dialog-container{
	  position:fixed;
	  left:0;
	  right:0;
	  top:0;
	  bottom:0;
	  background: rgba(0,0,0,0.3);
	}
	</style>
