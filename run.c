#include <Python.h>  
  
int main(int argc, char *argv[]) {  
    Py_Initialize();  
    PyRun_SimpleFile("./main.py");
    Py_Finalize();  
    return 0;  
}