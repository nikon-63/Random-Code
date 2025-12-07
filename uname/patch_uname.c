#include <linux/module.h>
#include <linux/init.h>
#include <linux/uts.h>
#include <linux/utsname.h>
#include <linux/string.h>

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Modify uname -v at runtime");

extern struct uts_namespace init_uts_ns;

static char old_version[__NEW_UTS_LEN + 1];
static char *new_version = "Custom kernel version";
module_param(new_version, charp, 0644);

static int __init patch_uname_init(void)
{
    int copied;

    strscpy(old_version, init_uts_ns.name.version, sizeof(old_version));

    copied = strscpy(init_uts_ns.name.version,
                     new_version,
                     sizeof(init_uts_ns.name.version));

    if (copied < 0) {
        strscpy(init_uts_ns.name.version,
                old_version,
                sizeof(init_uts_ns.name.version));
        return -EINVAL;
    }

    return 0;
}

static void __exit patch_uname_exit(void)
{
    strscpy(init_uts_ns.name.version,
            old_version,
            sizeof(old_version));
}

module_init(patch_uname_init);
module_exit(patch_uname_exit);
