---
layout: post
title: "Vue自定义弹出框"
tags: [HTML, JavaScript]
---

参考文章: [https://molunerfinn.com/vue-components/](https://molunerfinn.com/vue-components/)

如何不通过显式的在页面里写好组件的html结构通过v-model去调用组件，而是通过在js里通过形如`this.$message()`这样的方法调用组件？

首先创建一个Notice.vue的文件：

	<template>
	  <div class="notice">
		<div class="content" v-text='content'></div>
	  </div>
	</template>

	<script>
	  export default {
		name: 'notice',
		data () {
		  return {
			visible: false,
			content: '',
			duration: 3000
		  }
		},
		methods: {
		  setTimer() {
			setTimeout(() => {
			  this.close() // 3000ms之后调用关闭方法
			}, this.duration)
		  },
		  close() {
			this.visible = false
			setTimeout(() => {
			  this.$destroy(true)
			  this.$el.parentNode.removeChild(this.$el) // 从DOM里将这个组件移除
			}, 500)
		  }
		},
		mounted() {
		  this.setTimer() // 挂载的时候就开始计时，3000ms后消失
		}
	  }
	</script>

上面写的东西跟普通的一个单文件Vue组件没有什么太大的区别。不过区别就在于，没有props了，那么是如何通过外部来控制这个组件的显隐呢？

所以还需要一个js文件来接管这个组件，并调用extend方法。同目录下可以创建一个index.js的文件。

	import Vue from 'vue'

	const NoticeConstructor = Vue.extend(require('./Notice.vue').default) // 直接将Vue组件作为Vue.extend的参数
	const Notice = (content) => {
	  let id = 'notice-' + nId++
	  const NoticeInstance = new NoticeConstructor({
		data: {
		  content: content
		}
	  }) // 实例化一个带有content内容的Notice
	  NoticeInstance.id = id
	  NoticeInstance.vm = NoticeInstance.$mount() // 挂载但是并未插入dom，是一个完整的Vue实例
	  NoticeInstance.vm.visible = true
	  document.body.appendChild(NoticeInstance.vm.$el) // 将dom插入body
	  NoticeInstance.vm.$el.style.zIndex = nId + 1001 // 后插入的Notice组件z-index加一，保证能盖在之前的上面
	  return NoticeInstance.vm
	}

	export default {
	  install: Vue => {
		Vue.prototype.$notice = Notice // 将Notice组件暴露出去，并挂载在Vue的prototype上
	  }
	}

这个文件里我们能看到通过`NoticeConstructor`我们能够通过js的方式去控制一个组件的各种属性。然后把它注册进Vue的`prototype`上，这样就可以在页面内部使用形如`this.$notice()`方法了，可以方便调用这个组件来写做出简单的通知提示效果了。

最后在js里调用一下Vue.use()方法：

	import Notice from 'notice/index.js'
	Vue.use(Notice)

