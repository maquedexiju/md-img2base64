---
title: Python-kivy-android-pyjnius
tags:
notebook: Python学习 
---

[TOC]

## Installation
[参考网址](https://github.com/kivy/pyjnius/blob/master/docs/source/installation.rst)
* 需要先安装 Java JDK and JRE
* 需要先安装 Cython 

安装： 
`sudo python setup.py install`
如果需要便宜某个拓展，可以在这个拓展的目录下使用
`make`

如果需要给Android打包，即使用python-for-android，需要使用，具体还要参考python-for-android的文档
`./distribute.sh -m 'pyjnius kivy'`

当遇到错误`"No Java runtime present, requesting install"`时，可以尝试在jdk的文件下把info.plist修改一下。
例如我的路径是 /Library/Java/JavaVirtualMachines/jdk1.8.0_131.jdk/Contents/Info.plist
在JVMCapabilities中加入`<string>JNI</string>`
<en-media type="application/zip" hash="e3f469de381447ffd9a60801db30da5f"></en-media>

## Hello World
一个示例程序，创建test.py并在文件内输入
```
from jnius import autoclass

Stack = autoclass('java.util.Stack')
stack = Stack()
stack.push('hello')
stack.push('world')

print stack.pop() # --> 'world'
print stack.pop() # --> 'hello'
```
terminal 进入该文件夹，并通过python test.py执行

## Java小知识
### 签名(signature)
|Signature|　　Java中的类型|
|---|---|
|Z|　　　　　　　boolean|
|B|　　　　　　　byte|
|C|　　　　　　　char|
|S|　　　　　　　short|
|I|　　　　　　　 int|
|J|　　　　　　　 long|
|F|　　　　　　　float|
|D|　　　　　　　double|
|V|            void|
|L fully-qualified-class;|　　 fully-qualified-class|
|[ type　|　type[]|
|( arg-types ) ret-type|　　method type

e.g.
```java
(ILjava/util/List;)V
-> argument 1 is an integer
-> argument 2 is a java.util.List object
-> the method doesn't return anything.

(java.util.Collection;[java.lang.Object;)V
-> argument 1 is a Collection
-> argument 2 is an array of Object
-> nothing is returned

([B)Z
-> argument 1 is a Byte []
-> a boolean is returned
```

### field
通过field来获取类的成员属性

## API
### 映射类
至少要定义`__javaclass__`属性，设置`__metaclass__`为`MetaJavaClass`

e.g.
```python
from jnius import JavaClass, MetaJavaClass

class Stack(JavaClass):
    #Represent the Java class name, in the format 'org/lang/Class'. (eg: 'java/util/Stack'), not org.lang.Class'.
    __javaclass__ = 'java/util/Stack'
    #Must be set to :class:`MetaJavaClass`, otherwise, all the    methods/fields declared will be not linked to the JavaClass.
    __metaclass__ = MetaJavaClass

    #If not set, we assume the default constructor to take no parameters. Otherwise, it can be a list of all possible signatures of the constructor.
    __javaconstructor__ == (
                '()V',
                '(Ljava/lang/String;)V',
                '([C)V',
                '([CII)V',
                # ...
            )
```

#### 映射Java方法
1. 先获取模块的签名， 使用`javap -s`指令
```java
$ javap -s java.util.Stack
    Compiled from "Stack.java"
    public class java.util.Stack extends java.util.Vector{
    public java.util.Stack();
        Signature: ()V
    public java.lang.Object push(java.lang.Object);
        Signature: (Ljava/lang/Object;)Ljava/lang/Object;
    public synchronized java.lang.Object pop();
        Signature: ()Ljava/lang/Object;
    public synchronized java.lang.Object peek();
        Signature: ()Ljava/lang/Object;
    public boolean empty();
        Signature: ()Z
    public synchronized int search(java.lang.Object);
        Signature: (Ljava/lang/Object;)I
    }
```

2. 创建签名和方法之间的映射
```python
class Stack(JavaClass):
    __javaclass__ = 'java/util/Stack'
    __metaclass__ = MetaJavaClass

    peek = JavaMethod('()Ljava/lang/Object;')
    empty = JavaMethod('()Z')
```

#### 映射静态方法
 ```python
 function = JavaMethod('signature', static = True)
 ```

#### 映射Java域
```python
field = JavaField('signature')
```

#### 映射Java静态域
```python
field = JavaField('signature', static = True)
```

#### 映射被多个签名调用的方法
e.g.
```java
public byte[] getBytes(java.lang.String)
public byte[] getBytes(java.nio.charset.Charset)
public byte[] getBytes()
```
可以映射成
```python
getBytes = JavaMultipleMethod([
        '(Ljava/lang/String;)[B',
        '(Ljava/nio/charset/Charset;)[B',
        '()[B'])
```

### 映射函数
```python
>>> from jnius import autoclass
#The name must be written in the format: `a.b.c`, not `a/b/c`.
>>> autoclass('java.lang.System')
<class 'jnius.java.lang.System'>

autoclass can also represent a nested Java class:

>>> autoclass('android.provider.Settings$Secure')
<class 'jnius.reflect.android.provider.Settings$Secure'>
```

### 在Python中定义Java类
至少需要定义`__javainterfaces__`属性和`java_method`修饰符。
注意！静态方法和静态域是不支持。
e.g. 实现 java/util/ListIterator接口
```python
from jnius import PythonJavaClass, java_method

class PythonListIterator(PythonJavaClass):
    #List of the Java interfaces you want to proxify, in the format 'org/lang/Class'.
    __javainterfaces__ = ['java/util/ListIterator']

    #Indicate which class loader to use: 'system' or 'app'
    #默认认为通过Java的API声明
    #在Android上需要使用'app'
    __javacontext__ = 'system'

    def __init__(self, collection, index=0):
        super(TestImplemIterator, self).__init__()
        self.collection = collection
        self.index = index

    #java_method(java_signature, name=None)
    #The `java_signature` must match the wanted signature of the interface. 
    #The `name` of the method will be the name of the Python method by default. 
    #You can still force it, in case of multiple signature with the same Java method name.
    @java_method('()Z')
    def hasNext(self):
        return self.index < len(self.collection.data) - 1

    @java_method('()Ljava/lang/Object;')
    def next(self):
        obj = self.collection.data[self.index]
        self.index += 1
        return obj

    # etc...
```

### JVM选项和类的路径
设置需要在在导入jnius导入前完成。
```python
import jnius_config
jnius_config.add_options('-Xrs', '-Xmx4096')
jnius_config.set_classpath('.', '/usr/local/fem/plugins/*')
import jnius
```
### Pyjnius与进程
在Python中创建本地进程，并在进程中调用Pyjnius时，Pyjnius方法会强制将该进程和当前的JVM捆绑起来。
当离开进程时，需要手动`detach`Pyjnius
e.g.
```python
import threading
import jnius

def run(...):
    try:
        # use pyjnius here
    finally:
        jnius.detach()
```

