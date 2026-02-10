#include <linux/module.h>
#include <linux/printk.h>

#include "greet.h"

MODULE_LICENSE("GPL");

void greet() {
    printk(KERN_INFO "greet(): howdy!\n");
}
