# 查找自定的目录（不查找子目录）
find . ! -name "test" -type d -prune -o -type f -name "*.txt" -print

# 压缩多个文件
将文件file_00.txt、file_01.txt、file_02.txt、file_03.txt压缩为文件file.tar.gz

以下有4种实现方法：

方法一：

tar -cvf file.tar.gz file_00.txt file_01.txt file_02.txt file_03.txt

方法二：
tar -cvf file.tar.gz file*.txt

方法三：
find . -name "file*" | xargs -exec tar -cvf file.tar.gz;

方法四：
find . -name "file*"  -exec tar -cvf file.tar.gz {} \;

注意：方法四中最后的{}与\之间是存在空格的，并且最后的分号是必须的。
