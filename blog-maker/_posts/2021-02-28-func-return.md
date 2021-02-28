---
layout: post
title: JavaScript中try、catch、finally块中的return的处理方式
tags: [JavaScript]
---

当`try`块未捕获异常时，以下表格归纳了`return`语句在`try`块、`finally`块、`finally`块之后的代码时，会使用哪个代码块里的return：

|`try`块return|`finally`块return|执行顺序|`return`对应的代码块|
|-----|-----|-----|-----|
|否|否|try→finally→finally之后的代码|finally之后|
|否|是|try→finally|finally|
|是|否|try→finally|try|
|是|是|try→finally|finally|

当`try`块捕获到异常时，以下表格归纳了`return`语句在`catch`块、`finally`块、`finally`块之后的代码时，会使用哪个代码块里的return：

|`catch`块return|`finally`块return|执行顺序|`return`对应的代码块|
|-----|-----|-----|-----|
|否|否|try→catch→finally→finally之后的代码|finally之后|
|否|是|try→catch→finally|finally|
|是|否|try→catch→finally|catch|
|是|是|try→catch→finally|finally|
