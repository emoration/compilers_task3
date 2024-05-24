
int main() {
    // declaration
    int var_i;
    int var_j;
    int var_cnt;
    float var_f;
    int[5][4] var_arr;
    int var_i;  // [ERROR] redeclaration

    // assignment, expression, type casting
    var_i = (int) 3.14 + 9 * 11;  // explicit type casting (float -> int)
    var_j = 50.123;  // implicit type casting (float -> int)
    var_cnt = 0;
    var_f = (float) 1 + (long) 0.9;  // explicit and implicit type casting (float + long -> double -> float)
    var_k = 10;   // [ERROR] undeclared variable

    // array
//    var_i = var_arr[2][1] + 10;
    var_arr[1][2] = var_arr[2][1] + 10;
    var_i[1] = 10;  // [ERROR] no-array variable's subscript

    // if-else
    if (var_j < 100 && var_i < 100)
        if (var_i > var_j)
            var_i = 100;
        else
            var_j = 100;

    // while
    while (var_j < 100) {
        var_j = var_j + 1;
    }

    // do-while
    do {
        var_j = var_j + 1;
    } while (var_j < 100);

    // for
    for (var_j = 0; var_j < 100; var_j = var_j + 1) {
        var_cnt = var_cnt + 1;
    }

    // break, continue
    for (var_j = 0; var_j < 100; var_j = var_j + 1) {
        if (var_j == 50)
            break;
        if (var_j == 25)
            continue;
        var_cnt = var_cnt + 1;
    }

    // [ERROR] break, continue outside loop
    break;
    continue;

}
