# AutoHack 使用指南

> 本文中，AutoHack 统称为 AH

## 介绍

AH 是一款自动 hack 器/数据生成器/评测器。其原理为，采用一个标准程序生成大量的随机数据，再使用这些数据评测其他程序。

## 安装 / 运行

使用 `requirements.txt` 安装依赖的第三方库，后续直接运行 `autoHack.random.py` 即可。AH 可以使用 `Ctrl + C` 强制退出，但需要手动删去根目录下的临时文件。通常，这些文件的拓展名是 `.in` `.out` `.ans`。

## 配置

AH 的所有配置都存在于 `dataGenerator.py` 内。若要更改数据生成器，可在第 47 行开始编写自己的数据生成器。使用以下语句向输入文件写入：

```python
inputFile.write()
```

其他配置都在第 5 行开始的 `Config` 类内，各项配置如下：

### Line 6 - Line 13

`numberOfSamples` : 随机生成的数据数量  
`sourceFile` : 源文件名，不带拓展名  
`stdFile` ： 标程文件名，不带拓展名  
`timeLimits` : 时间限制  
`exitWhenThereIsADiscrepancy` : 是否在出现差异时直接退出  
`waitTime` : 差异详细信息显示的秒数  
`ignoreSomeCharactersAtTheEnd` : 是否忽略最后的空行及行末空格  
`saveWrongOutput` ： 是否存储错误的输出

### Line 15 - Line 18 (Program)

`compileBeforeRun` : 是否由 AH 编译程序  
`compileArgs` : 编译参数，`-o` 由 AH 自动填写  
`useFileIO` : 是否使用文件输入输出  

### Line 20 - Line 23 (File)

`dataFileName` : 数据文件名及其拓展名
`fileName` : 文件输入输出文件名及其拓展名
`wrongOutputFileName` : 存储的错误输出文件名及其拓展名

### Line 25 - Line 27 (Debug)

`skipGenerate` : 是否跳过生成数据，跳过则使用上一次的数据  
`skipRun` : 是否跳过运行，若您把 AH 当作数据生成器，此项可能有用
