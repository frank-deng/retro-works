---
layout: post
title: "React.js处理组件对应的DOM需要在父组件以外的地方渲染的情况"
tags: [HTML, JavaScript, React.js]
---

对于悬浮窗一类的组件，组件里的内容往往需要渲染在父组件以外的地方，比如`<body>`，此时组件内需要做如下操作：

1. 在组件对应的`Class`中准备一个变量`container`，默认值为`null`，用于存储渲染容器对应的DOM，该变量将用于从`<body>`中删除该DOM的操作。
2. 组件默认的`render()`函数返回`null`，防止该组件在父组件中渲染DOM。
3. 在组件的`componentDidUpdate()`生命周期中处理相关的渲染逻辑。如果渲染用的容器不存在或被删除，则手工使用原生的`document.createElement()`创建对应的容器，并使用`document.body.appendChild()`，将该容器添加到`<body>`的末尾，然后使用`this.container`变量存储渲染用容器DOM；最后使用`ReactDOM.render()`（第2个参数传渲染容器对应的DOM）将待渲染的内容渲染到容器DOM中。
4. 在组件的`componentWillUnmount()`进行对应的销毁操作，比如当挂在`<body>`上的渲染用的容器DOM仍然存在时，将该DOM从`<body>`中删除。

这样可以防止因弹出框不在`<body>`上而导致出现悬浮窗被意外遮挡等问题。

注意
----

* 在组件的`componentDidUpdate()`生命周期中可以随时新建或销毁渲染容器对应的DOM。但不建议在此生命周期中销毁渲染容器对应的DOM，销毁DOM的工作建议只放在`componentWillUnmount()`生命周期中进行。
* 在组件的`componentDidUpdate()`生命周期中尽量避免在该生命周期中执行过多操作，因为每次`this.props`发生变化时，该生命周期方法都会被调用一次，易造成性能问题。
* 将组件里的内容渲染在父组件以外的操作一般应在项目的公用组件库中实现，一般不要在和业务高度相关、复用率低的组件中实现，以防止代码逻辑陷入混乱。

范例
----

以下是一个简单的对话框组件的代码：

	import {Component} from 'react';
	import ReactDOM from 'react-dom';
	export default class Dialog extends Component{
		//Modal容器对应的DOM
		container=null;
		componentDidUpdate(){
			let visible=this.props.visible;
			//切换body上的容器的新建和销毁
			if(!visible && this.container){
				document.body.removeChild(this.container);
				this.container=null;
			}else if(visible && !this.container){
				let container = document.createElement("div");
				container.classList.add('dialog-container');
				if(this.props.modalClass){
					container.classList.add(this.props.modalClass);
				}
				this.container=container;
				document.body.appendChild(container);
			}
			//更新对话框里的内容
			if(!visible){
				return;
			}
			let classList=['dialog-body'];
			if(this.props.customClass){
				classList.push(this.props.customClass);
			}
			ReactDOM.render(
				<div className={classList.join(' ')}>{this.props.children}</div>,
				this.container
			);
		}
		componentWillUnmount(){
			//Modal被销毁时，将对应的DOM手动清除
			if(this.container){
				document.body.removeChild(this.container);
				this.container=null;
			}
		}
		//不使用组件默认的render()函数，因为该组件对应的DOM不在父组件对应的DOM下面，而在body上
		render(){
			return null;
		}
	}

