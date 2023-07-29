博客生成器 Blog Maker
=====================

类似Jekyll的静态博客网站生成器，支持LaTeX数学公式。  
A Jekyll-like static blog site generator, supports LaTeX mathematical equations.

需要在Linux环境（如Debian、Ubuntu）中运行。  
Require running under Linux environments like Debian, Ubuntu.

安装 Installation
-----------------

执行以下命令安装所需的软件：  
Execute the following commands to install the softwares required:

	sudo apt-get install nodejs imagemagick
	cd /path/to/blog-maker && npm install

使用方法 Usage
--------------

编辑完文档后，运行`npm start`即可生成博客站点内容，生成结果在`dist`目录中。  
After editing documents, run `npm start` to generate the blog site, generated files can be found at `dist` directory.

实用命令 Useful Commands
------------------------

### Linux下安装字体 Install Fonts Under Linux

1. 将字体文件复制到`/usr/share/fonts`中，并将字体文件的权限改为`644`。  
Copy font files to `/usr/share/fonts` and change the permission of the font files into `644`.
2. 运行`sudo fc-cache -v`使得新添加的字体生效。  
Run `sudo fc-cache -v` to activate newly added fonts.
3. 运行`fc-list`查看新添加的字体是否生效。  
Run `fc-list` to check whether the newly-added fonts are useable.

