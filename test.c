#include <windows.h>  
  
int main() {  
    // 执行cmd命令，不弹出窗口  
    ShellExecute(NULL, "open", "cmd.exe", "/c python main.py", NULL, SW_HIDE);  
    return 0;  
}

