#ifndef test_hpp_
#define test_hpp_

#include <stdio.h>
#include <string.h>

class Test{
private:
    size_t failedCount;
public:
    Test(){
        this->failedCount = 0;
        this->run();
    }
    ~Test(){
        if (this->failedCount > 0) {
            printf("%d test cases failed.\n", this->failedCount);
        } else {
            puts("All test cases succeed.");
        }
    }
    void run();
};

#define EXP_TRUE(expr) do { \
    if (expr) { \
        printf("Succeed: %s == true\n", #expr); \
    } else { \
        printf("Failed: %s == false\n", #expr); \
        this->failedCount++; \
    } \
} while (0)

#define EXP_FALSE(expr) do { \
    if (!expr) { \
        printf("Succeed: %s == false\n", #expr); \
    } else { \
        printf("Failed: %s == false\n", #expr); \
        this->failedCount++; \
    } \
} while (0)

#define EXP_EQ(val, expr) do { \
    if ((expr) == (val)) { \
        printf("Succeed: %s == %s\n", #expr, #val); \
    } else { \
        printf("Failed: %s == %s\n", #expr, #val); \
        this->failedCount++; \
    } \
} while (0)

#define EXP_NE(val, expr) do { \
    if ((expr) != (val)) { \
        printf("Succeed: %s != %s\n", #expr, #val); \
    } else { \
        printf("Failed: %s != %s\n", #expr, #val); \
        this->failedCount++; \
    } \
} while (0)

#define EXP_STREQ(val, expr) do { \
    char *exprRes = (expr); \
    char *valRes = (val); \
    if (NULL == exprRes) { \
        printf("Failed: %s is NULL\n", #expr); \
        this->failedCount++; \
    } \
    if (0 == strcmp(exprRes, valRes)) { \
        printf("Succeed: %s streq %s\n", #expr, #val); \
    } else { \
        printf("Failed: %s\n  Expected: %s  Actual: %s\n", #expr, valRes, exprRes); \
        this->failedCount++; \
    } \
} while (0)

#endif
