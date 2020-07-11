# Quic Search

A python quick search programme for special databases

一个基于Python的快速特殊数据库搜索程序

**需要使用剪贴板（复制粘贴）时，请切换回搜索模式，相同的搜索项只会触发1次搜索，程序读取剪贴板的频率默认为2秒1次**

## 自建数据库示例

[jokin1999/quic-search-demo](https://github.com/jokin1999/quic-search-demo)

**需要官方收录数据库节点请提交[ISSUE](https://github.com/jokin1999/quic-search-demo/issues/new)，会尽快处理。**

## 快捷键

- `Ctrl + Shift + Alt + Z` 切换搜索模式、剪贴板模式、英译中、中译英（具体请参考软件提示）
- `Ctrl + Shift + Alt + S` 发送剪贴板内容至云便签
- `Ctrl + Shift + Alt + X` 获取云便签内容并复制到剪贴板

**所有快捷键操作与`CTRL+C`、复制操作均有提示音**

## 提示音说明

软件打开后会释放以`x.mp3`命名的提示音文件，提前试听可帮助熟悉软件

- `0.mp3` 通常表示错误或搜索模式
- `1.mp3` 通常表示成功或剪贴板模式
- `2.mp3` 通常表示英译中模式
- `3.mp3` 通常表示中译英模式

## 白名单格式说明

whitelist.txt
```
# QCS Login White List
key1
key2
```

## 数据库列表格式说明

文件：`list.txt`

```
# 示例数据库
# 名称,文件名,状态（0不可见，1正常，2维护）
# 请勿使用空白字符，可能导致一些未知错误

示例数据库,xxx,1
```

## 数据库格式说明

**数据库尽可能保持下方格式，多行Answer不可换行，不要出现多余的非空白行，`#`开头的行或空白行会被忽略。**

文件：`databases/xxx.qcsd`

```
# NAME = 示例数据库
# VERSION = v1.0

-> Question
=> Answer
```
