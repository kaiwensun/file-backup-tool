EN = "en"
ZH = "zh"

def text(key, lang, **kwargs):
    pattern = key if lang == EN else TRANSLATE[key][lang]
    return pattern.format(**kwargs)

TRANSLATE = {
    "What's the path of the source folder?": {
        ZH: "您想备份哪个文件夹？（备份的来源）"
    },
    "What's the path of the destination folder?": {
        ZH: "您想备份到哪个文件夹？（备份目的地）"
    },
    "file": {
        ZH: "文件"
    },
    "folder": {
        ZH: "文件夹"
    },
    "symlink": {
        ZH: "快捷方式"
    },
    "Source has the following more items in this folder": {
        ZH: "备份来源的这个文件夹中有以下从未备份过的项目"
    },
    "Destination has the following more items in this folder": {
        ZH: "备份至的这个目的地文件夹中有以下项目不在备份来源当中"
    },
    "backup root": {
        ZH: "起始目录"
    },
    "Quitting...": {
        ZH: "退出……"
    },
    "Quit": {
        ZH: "退出"
    },
    "Yes": {
        ZH: "是"
    },
    "No": {
        ZH: "否"
    },
    "Acknowledge": {
        ZH: "知道了"
    },
    "Folder not found: ": {
        ZH: "未找到文件夹："
    },
    "Not a folder: ": {
        ZH: "不是文件夹："
    },
    "bakckup tool": {
        ZH: "备份工具"
    },
    "source path": {
        ZH: "备份来源路径（从哪里复制）"
    },
    "destination path": {
        ZH: "备份目的地路径（复制到哪里）"
    },
    "Do not actually move or copy any files": {
        ZH: "试运行，不真正地移动或复制任何文件"
    },
    "Running in dry-run mode": {
        ZH: "试运行模式已打开"
    },
    "[DRYRUN]": {
        ZH: "[试运行]"
    },
    "Please acknowledge the diff": {
        ZH: "请知悉这些差异"
    },
    "Would you like to copy all the extra source files/folders to destination? ": {
        ZH: "您想要把所有备份来源中多余的新文件或文件夹复制到备份目的地吗？ "
    },
    "Let me select": {
        ZH: "让我选择"
    },
    "All processed": {
        ZH: "全部处理完毕"
    },
    "src is {src_type}, dst is {dst_type}. Please backup manually.": {
        ZH: "备份来源是一个{src_type}，但备份目的地现有的是一个{dst_type}。请手动备份它。"
    },
    "Git repo {path} is different from destination. Please backup manually.": {
        ZH: "Git代码库 {path} 与现有备份不一致。请手动备份它。"
    },
    "{entry_typ} sizes of src and dst are different: {src_size}B vs {dst_size}B": {
        ZH: "备份来源与备份目的地的{entry_typ}的大小不同：{src_size}B vs {dst_size}B"
    },
    "{entry_typ} last modified time of src and dst are different: {src_time} vs {dst_time}": {
        ZH: "{entry_typ}的修改时间不同：{src_time} vs {dst_time}"
    },
    "Would you like to backup? This will override the existing backup.": {
        ZH: "你是否要备份它？这会替换并覆盖当前已有的备份。"
    },
    "print help message": {
        ZH: "显示使用方式"
    },
    "Back up completed. Press Enter to exit...": {
        ZH: "备份完毕。按回车键退出程序。"
    },
    "Back up aborted. Press Enter to exit...": {
        ZH: "备份异常中断。按回车键退出程序。"
    }
}