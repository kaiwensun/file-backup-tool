EN = "en"
ZH = "zh"

def text(key, lang, **kwargs):
    return TRANSLATE[key][lang].format(**kwargs)

TRANSLATE = dict(
    ASK_FOR_INPUT_SRC = {
        EN: "What's the path of the source folder?"
    },
    ASK_FOR_INPUT_DST = {
        EN: "What's the path of the destination folder?"
    },
    WARN_SRC_MISS_DST_EXIST = {
        EN: '[WARN] destination file/folder "{dst}" exists, but the source file is missing.'
    },
    TYP_FILE = {
        EN: "file"
    },
    TYP_FOLDER = {
        EN: "folder"
    },
    TYP_SYMLINK = {
        EN: "symlink"
    },
    SHOW_SRC_EXTRA = {
        EN: "Source has the following more items in this folder"
    },
    SHOW_DST_EXTRA = {
        EN: "Destination has the following more items in this folder"
    }
    
)