#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>

// 这是一个故意留有漏洞的函数
void vulnerable(char *str) {
    char buffer[10]; // 缓冲区非常小，只有 10 字节
    
    // 危险操作：strcpy 没有检查长度
    // 如果输入超过 10 字节，就会覆盖栈内存，导致 Segmentation Fault (崩溃)
    strcpy(buffer, str); 
    
    if (strcmp(buffer, "secret") == 0) {
        printf("You found the secret!\n");
    } else {
        printf("Received: %s\n", buffer);
    }
}

int main() {
    char input[100];
    // 从标准输入读取数据
    if (read(0, input, 100) > 0) {
        vulnerable(input);
    }
    return 0;
}
