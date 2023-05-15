from translations import text as t, EN
import os, datetime, sys, collections, shutil


NEW_ENTRY_TOKEN = "+"
prefix = []
PRINT_WIDTH = 2
assert PRINT_WIDTH >= 2

DfsPair = collections.namedtuple('DfsPair', ['src', 'dst'])

class PseudoDirEntry:
    def __init__(self, path):
        self._path = os.path.abspath(path)
        assert os.path.exists(self.path)
    @property
    def path(self):
        return self._path
    @property
    def name(self):
        return os.path.basename(self.path)
    def is_dir(self, follow_symlinks=True):
        return os.path.isdir(self._real_path if follow_symlinks else self.path)
    def is_file(self, follow_symlinks=True):
        return os.path.isfile(self._real_path if follow_symlinks else self.path)
    def is_symlink(self):
        return os.path.islink(self.path)
    def stat(self):
        return os.stat(self.path, follow_symlinks=False)
    @property
    def _real_path(self):
        return os.path.realpath(self.path)

def tr(text):
    return t(text, EN)

def print_regular(text, end="\n"):
    left = (" " * PRINT_WIDTH + "|") * (len(prefix) - 1) + " " * PRINT_WIDTH
    print(left + text, end=end)

def print_new_entry():
    # the new entry should have been already pushed to `prefix`
    if len(prefix) > 1:
        print_empty_line()
        left = (" " * PRINT_WIDTH + "|") * (len(prefix) - 1)
        print(left[:-1] + NEW_ENTRY_TOKEN + "-" * (PRINT_WIDTH - 1) + prefix[-1].src.name)
    else:
        print("[root]")

def print_empty_line():
    left = (" " * PRINT_WIDTH + "|") * (len(prefix) - 1)
    print(left)

def get_input(available_options={}, beglin_line=True):
    assert 'q' not in available_options
    if not available_options:
        available_options = {
            "y": "Yes",
            "n": "No"
        }
    available_options = {**available_options, "q": "Quit"}
    value = None
    left = (" " * PRINT_WIDTH + "|") * len(prefix) + " " * PRINT_WIDTH if beglin_line else ""
    prompt = left + ", ".join(f"[{key}] {desc}" for key, desc in available_options.items()) + ": "
    while value not in available_options:
        value = input(prompt)
    if value == "q":
        print("Quitting...")
        sys.exit(0)
    return value

def get_roots():
    def validate(path):
        if not os.path.exists(path):
            print(f"Folder not found: {path}")
            return False
        if not os.path.isdir(path):
            print(f"Not a folder: {path}")
            return False
        return True
    src = input(tr("ASK_FOR_INPUT_SRC"))
    while not validate(src):
        src = input(tr("ASK_FOR_INPUT_SRC"))
    dst = input(tr("ASK_FOR_INPUT_DST"))
    while not validate(dst):
        dst = input(tr("ASK_FOR_INPUT_DST"))
    prefix.append(DfsPair(
        PseudoDirEntry(src),
        PseudoDirEntry(dst)
    ))

def copy_entry(entry):
    src_path = os.path.join(prefix[-1].src.path, entry.name)
    dst_path = os.path.join(prefix[-1].dst.path, entry.name)
    if os.path.exists(dst_path):
        raise Exception(f"{dst_path} already exists")

    if entry.is_dir(follow_symlinks=False):
        shutil.copytree(src_path, dst_path)
    else:
        shutil.copy2(src_path, dst_path)
def replace_entry():
    src_path = prefix[-1].src.path
    dst_path = prefix[-1].dst.path
    if not os.path.exists(dst_path):
        raise Exception(f"{dst_path} doesn't exists. Why are you replacing?")
    if prefix[-1].src.is_dir() or prefix[-1].dst.is_dir():
        raise Exception("entry replacement can't deal with folders")
    shutil.copy2(src_path, dst_path)

    
def get_entry_datetime(entry, mode='m'):
    if mode == 'c':
        timestamp = entry.stat().st_ctime
    elif mode == 'm':
        timestamp = entry.stat().st_mtime
    else:
        raise Exception(f"unknown mode {mode}")
    return datetime.datetime.fromtimestamp(timestamp)

def datetime2str(datetime):
    fmt = "%Y-%m-%d %H:%M:%S"
    return datetime.strftime(fmt)

def get_file_entry_type_string(entry):
    if entry.is_symlink():
        typ = "TYP_SYMLINK"
    elif entry.is_dir(follow_symlinks=False):
        typ = "TYP_FOLDER"
    elif entry.is_file(follow_symlinks=False):
        typ = "TYP_FILE"
    else:
        raise Exception(f"Unknown type entry {entry}")
    return tr(typ)

def quick_compare(src_entries, dst_entries):
    extra_src = []
    extra_dst = []
    i = j = 0
    while i < len(src_entries) or j < len(dst_entries):
        s = src_entries[i] if i < len(src_entries) else None
        d = dst_entries[j] if j < len(dst_entries) else None
        i += 1
        j += 1
        if s is None:
            extra_dst.append(d)
            i -= 1
            continue
        if d is None:
            extra_src.append(s)
            j -= 1
            continue
        if s.name == d.name:
            continue
        elif s.name < d.name:
            extra_src.append(s)
        else:
            extra_dst.append(d)
    if extra_src:
        print_empty_line()
        print_regular(tr("SHOW_SRC_EXTRA"))
        for extra in extra_src:
            print_regular("  " + extra.name)
    if extra_dst:
        print_empty_line()
        print_regular(tr("SHOW_DST_EXTRA"))
        for extra in extra_dst:
            print_regular("  " + extra.name)
    if extra_src:
        print_regular("Would you like to copy all the extra source files/folders to destination? ", end="")
        answer = get_input({
            "y": "Yes",
            "n": "No",
            "s": "Let me select"
        }, beglin_line=False)
        if answer == "y":
            for extra in extra_src:
                copy_entry(extra)
        elif answer == "s":
            for extra in extra_src:
                print_regular(f"{extra.name} ", end="")
                if get_input(beglin_line=False) == "y":
                    copy_entry(extra)
            print_regular("All processed ", end="")
    return extra_src, extra_dst

def walk(src, dst):
    src_entries = sorted(os.scandir(src), key=lambda f: f.name)
    dst_entries = sorted(os.scandir(dst), key=lambda f: f.name)
    quick_compare(src_entries, dst_entries)
    i = j = 0
    while i < len(src_entries) and j < len(dst_entries):
        s = src_entries[i]
        d = dst_entries[j]
        i += 1
        j += 1
        if s.name < d.name:
            j -= 1
            continue
        if s.name > d.name:
            i -= 1
            continue
        prefix.append(DfsPair(s, d))
        print_new_entry()
        if get_file_entry_type_string(s) != get_file_entry_type_string(d):
            print_regular(f"src is {get_file_entry_type_string(s)}, dst is {get_file_entry_type_string(d)}. Please backup manually.")
            get_input({"a": "Acknowledge"})
            prefix.pop()
            continue
        if s.is_dir(follow_symlinks=False):
            walk(s.path, d.path)
        else:
            src_size = s.stat().st_size
            dst_size = d.stat().st_size
            src_mtime = get_entry_datetime(s)
            dst_mtime = get_entry_datetime(d)
            is_diff = False
            entry_typ = get_file_entry_type_string(s)
            if src_size != dst_size:
                print_regular(f"{entry_typ} sizes of src and dst are different: {src_size} vs {dst_size}")
                is_diff = True
            if src_mtime != dst_mtime:
                print_regular(f"{entry_typ} last modified time of src and dst are different: {datetime2str(src_mtime)} vs {datetime2str(dst_mtime)}")
                is_diff = True
            if is_diff:
                print_regular("Would you like to backup? This will override the existing backup. ", end="")
                if "y" == get_input(beglin_line=False):
                    replace_entry()
        prefix.pop()


def main():
    get_roots()
    print_new_entry()
    walk(prefix[0].src.path, prefix[0].dst.path)

if __name__ == "__main__":
    main()