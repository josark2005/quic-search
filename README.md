# Quic Search

A python quick search programme for special databases

一个基于Python的快速特殊数据库搜索程序

**需要使用剪贴板（复制粘贴）时，请切换回搜索模式，相同的搜索项只会触发1次搜索，程序读取剪贴板的频率默认为2秒1次**

## 数据库示例

[jokin1999/quic-search-demo](https://github.com/jokin1999/quic-search-demo)

## 快捷键

`Ctrl + Shift + Alt + Z` 切换剪贴板模式与搜索模式

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

文件：`databases/xxx.qcsd`

```
# NAME = 示例数据库
# VERSION = v1.0

-> Question
=> Answer
```
